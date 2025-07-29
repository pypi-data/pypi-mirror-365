"""HuBERT model implementations."""

import mlx.core as mx
import mlx.nn as nn
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .config import HubertConfig
from .layers import (
    HubertFeatureEncoder,
    HubertFeatureProjection,
    HubertEncoder,
)


@dataclass
class HubertOutput:
    """Output type for HuBERT models.
    
    Attributes:
        last_hidden_state: Sequence of hidden states from the last encoder layer.
        hidden_states: Hidden states from all layers (if requested).
        attentions: Attention weights from all layers (if requested).
    """
    last_hidden_state: mx.array
    hidden_states: Optional[tuple] = None
    attentions: Optional[tuple] = None


@dataclass
class CausalLMOutput:
    """Output type for language modeling.
    
    Attributes:
        logits: Prediction scores for each vocabulary token.
        hidden_states: Hidden states from all layers (if requested).
        attentions: Attention weights from all layers (if requested).
    """
    logits: mx.array
    hidden_states: Optional[tuple] = None
    attentions: Optional[tuple] = None


class HubertModel(nn.Module):
    """HuBERT base model for feature extraction.
    
    This model extracts speech representations from raw audio waveforms
    using a convolutional feature encoder followed by a transformer encoder.
    
    Args:
        config: Model configuration.
    """
    
    def __init__(self, config: HubertConfig):
        super().__init__()
        self.config = config
        self.feature_extractor = HubertFeatureEncoder(config)
        self.feature_projection = HubertFeatureProjection(config)
        
        if config.mask_time_prob > 0 or config.mask_feature_prob > 0:
            self.masked_spec_embed = mx.zeros((config.hidden_size,))
        
        self.encoder = HubertEncoder(config)

    def _mask_hidden_states(
        self, 
        hidden_states: mx.array,
        mask_time_indices: Optional[mx.array] = None,
    ) -> mx.array:
        """Apply SpecAugment masking to hidden states.
        
        Args:
            hidden_states: Input features to mask.
            mask_time_indices: Pre-computed mask indices.
            
        Returns:
            Masked hidden states.
        """
        if mask_time_indices is not None:
            hidden_states = mx.where(
                mask_time_indices.reshape(-1, mask_time_indices.shape[-1], 1),
                self.masked_spec_embed,
                hidden_states
            )
        return hidden_states

    def __call__(
        self,
        input_values: mx.array,
        attention_mask: Optional[mx.array] = None,
        mask_time_indices: Optional[mx.array] = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ) -> HubertOutput:
        """Extract features from raw audio.
        
        Args:
            input_values: Raw audio waveform of shape (batch, length).
            attention_mask: Mask for valid audio positions.
            mask_time_indices: Indices for masked time steps (for pre-training).
            output_attentions: Whether to return attention weights.
            output_hidden_states: Whether to return all hidden states.
            return_dict: Whether to return a HubertOutput object.
            
        Returns:
            HubertOutput containing extracted features.
        """
        # Extract features from raw audio
        extract_features = self.feature_extractor(input_values)
        
        # Project features to model dimension
        hidden_states = self.feature_projection(extract_features)
        
        # Apply SpecAugment masking if provided
        if mask_time_indices is not None:
            hidden_states = self._mask_hidden_states(hidden_states, mask_time_indices)
        
        if attention_mask is not None:
            attention_mask = self._get_feature_vector_attention_mask(
                extract_features.shape[1], attention_mask
            )
        
        encoder_outputs = self.encoder(
            hidden_states,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=True,
        )
        
        hidden_states = encoder_outputs["last_hidden_state"]
        
        if not return_dict:
            return (hidden_states,) + tuple(
                v for v in [encoder_outputs.get("hidden_states"), encoder_outputs.get("attentions")] 
                if v is not None
            )
        
        return HubertOutput(
            last_hidden_state=hidden_states,
            hidden_states=encoder_outputs.get("hidden_states"),
            attentions=encoder_outputs.get("attentions"),
        )
    
    def _get_feature_vector_attention_mask(
        self, 
        feature_vector_length: int, 
        attention_mask: mx.array
    ) -> mx.array:
        """Compute attention mask for feature vectors.
        
        The feature extractor reduces the sequence length through strided convolutions.
        This method computes the corresponding attention mask for the reduced sequence.
        
        Args:
            feature_vector_length: Length of feature vector sequence.
            attention_mask: Original attention mask for raw audio.
            
        Returns:
            Attention mask for feature vectors.
        """
        # Compute how many audio samples correspond to one feature vector
        output_lengths = self._get_feat_extract_output_lengths(attention_mask.sum(axis=1))
        
        batch_size = attention_mask.shape[0]
        
        # Create position indices for the feature vectors
        # Shape: (1, feature_vector_length)
        position_indices = mx.arange(feature_vector_length)[None, :]
        
        # Expand output_lengths to shape (batch_size, 1) for broadcasting
        output_lengths = output_lengths[:, None]
        
        # Create mask by comparing position indices with output lengths
        # Broadcasting: (batch_size, 1) < (1, feature_vector_length) -> (batch_size, feature_vector_length)
        feature_attention_mask = (position_indices < output_lengths).astype(attention_mask.dtype)
            
        return feature_attention_mask
    
    def _get_feat_extract_output_lengths(self, input_lengths: mx.array) -> mx.array:
        """Compute output length of feature extractor for given input lengths.
        
        Args:
            input_lengths: Lengths of input sequences.
            
        Returns:
            Output lengths after feature extraction.
        """
        def _conv_out_length(input_length, kernel_size, stride):
            return (input_length - kernel_size) // stride + 1
        
        for kernel_size, stride in zip(self.config.conv_kernel, self.config.conv_stride):
            input_lengths = _conv_out_length(input_lengths, kernel_size, stride)
            
        return input_lengths.astype(mx.int32)


class HubertForCTC(nn.Module):
    """HuBERT model with CTC head for automatic speech recognition.
    
    This model adds a linear projection layer on top of the HuBERT encoder
    to predict character or subword tokens using CTC loss.
    
    Args:
        config: Model configuration.
    """
    
    def __init__(self, config: HubertConfig):
        super().__init__()
        self.config = config
        self.hubert = HubertModel(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size)
        
    def freeze_feature_encoder(self):
        """Freeze the feature encoder to prevent updates during training."""
        self.hubert.feature_extractor.freeze()
        
    def __call__(
        self,
        input_values: mx.array,
        attention_mask: Optional[mx.array] = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ) -> CausalLMOutput:
        """Compute CTC logits from raw audio.
        
        Args:
            input_values: Raw audio waveform of shape (batch, length).
            attention_mask: Mask for valid audio positions.
            output_attentions: Whether to return attention weights.
            output_hidden_states: Whether to return all hidden states.
            return_dict: Whether to return a CausalLMOutput object.
            
        Returns:
            CausalLMOutput containing CTC logits.
        """
        outputs = self.hubert(
            input_values,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=True,
        )
        
        hidden_states = outputs.last_hidden_state
        logits = self.lm_head(hidden_states)
        
        if not return_dict:
            output = (logits,) + tuple(
                v for v in [outputs.hidden_states, outputs.attentions] if v is not None
            )
            return output
        
        return CausalLMOutput(
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )