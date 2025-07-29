"""Configuration classes for HuBERT models."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union, Dict, Any
import json


@dataclass
class HubertConfig:
    """Configuration class to store the configuration of a HuBERT model.
    
    Args:
        vocab_size: Vocabulary size of the model. Defines the number of different tokens.
        hidden_size: Dimensionality of the encoder layers and the pooler layer.
        num_hidden_layers: Number of hidden layers in the Transformer encoder.
        num_attention_heads: Number of attention heads for each attention layer.
        intermediate_size: Dimensionality of the "intermediate" (i.e., feed-forward) layer.
        hidden_act: The non-linear activation function in the encoder and pooler.
        hidden_dropout: The dropout probability for all fully connected layers.
        activation_dropout: The dropout ratio for activations inside the fully connected layer.
        attention_dropout: The dropout ratio for the attention probabilities.
        feat_proj_layer_norm: Whether to apply LayerNorm to the output of the feature encoder.
        feat_proj_dropout: The dropout probability for the feature projection layer.
        feat_extract_norm: The norm to be applied to 1D convolutional layers in feature encoder.
        feat_extract_activation: The non-linear activation function in the 1D convolutional layers.
        feat_extract_dropout: The dropout probability for 1D convolutional layers.
        conv_dim: A tuple of integers defining the number of output channels of each conv layer.
        conv_stride: A tuple of integers defining the stride of each conv layer.
        conv_kernel: A tuple of integers defining the kernel size of each conv layer.
        conv_bias: Whether the conv layers have a bias.
        num_conv_pos_embeddings: Number of convolutional positional embeddings.
        num_conv_pos_embedding_groups: Number of groups of convolutional positional embeddings.
        conv_pos_batch_norm: Whether to use batch normalization on convolutional positional embeddings.
        apply_spec_augment: Whether to apply SpecAugment data augmentation.
        mask_time_prob: Probability of masking a time step.
        mask_time_length: Length of vector span to mask along the time axis.
        mask_time_min_masks: Minimum number of masked spans along the time axis.
        mask_feature_prob: Probability of masking a feature channel.
        mask_feature_length: Length of vector span to mask along the feature axis.
        mask_feature_min_masks: Minimum number of masked spans along the feature axis.
        num_codevectors_per_group: Number of entries in each codebook.
        num_codevector_groups: Number of codebook groups.
        contrastive_logits_temperature: The temperature for the contrastive loss.
        num_negatives: Number of negative samples for the contrastive loss.
        codevector_dim: Dimensionality of the codebook vectors.
        proj_codevector_dim: Dimensionality of the projected codebook vectors.
        diversity_loss_weight: The weight of the diversity loss.
        ctc_loss_reduction: Specifies the reduction to apply to the output of `torch.nn.CTCLoss`.
        ctc_zero_infinity: Whether to zero infinite losses and the associated gradients of `torch.nn.CTCLoss`.
        use_weighted_layer_sum: Whether to use weighted layer sum.
        layer_norm_eps: The epsilon used by the layer normalization layers.
        do_stable_layer_norm: Whether to apply stable layer norm architecture.
        num_feat_extract_layers: Number of feature extraction convolutional layers.
    """
    
    vocab_size: int = 32
    hidden_size: int = 768
    num_hidden_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    hidden_act: str = "gelu"
    hidden_dropout: float = 0.1
    activation_dropout: float = 0.1
    attention_dropout: float = 0.1
    feat_proj_layer_norm: bool = True
    feat_proj_dropout: float = 0.0
    feat_extract_norm: str = "group"
    feat_extract_activation: str = "gelu"
    feat_extract_dropout: float = 0.0
    conv_dim: List[int] = field(default_factory=lambda: [512, 512, 512, 512, 512, 512, 512])
    conv_stride: List[int] = field(default_factory=lambda: [5, 2, 2, 2, 2, 2, 2])
    conv_kernel: List[int] = field(default_factory=lambda: [10, 3, 3, 3, 3, 2, 2])
    conv_bias: bool = False
    num_conv_pos_embeddings: int = 128
    num_conv_pos_embedding_groups: int = 16
    conv_pos_batch_norm: bool = False
    apply_spec_augment: bool = True
    mask_time_prob: float = 0.05
    mask_time_length: int = 10
    mask_time_min_masks: int = 2
    mask_feature_prob: float = 0.0
    mask_feature_length: int = 10
    mask_feature_min_masks: int = 0
    num_codevectors_per_group: int = 320
    num_codevector_groups: int = 2
    contrastive_logits_temperature: float = 0.1
    num_negatives: int = 100
    codevector_dim: int = 256
    proj_codevector_dim: int = 256
    diversity_loss_weight: float = 0.1
    ctc_loss_reduction: str = "sum"
    ctc_zero_infinity: bool = False
    use_weighted_layer_sum: bool = False
    layer_norm_eps: float = 1e-5
    do_stable_layer_norm: bool = False
    num_feat_extract_layers: int = 7
    
    architectures: Optional[List[str]] = None
    model_type: Optional[str] = "hubert"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    def to_json_string(self) -> str:
        """Convert config to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_pretrained(self, save_directory: str):
        """Save config to directory."""
        import os
        os.makedirs(save_directory, exist_ok=True)
        with open(os.path.join(save_directory, "config.json"), "w") as f:
            f.write(self.to_json_string())
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "HubertConfig":
        """Create config from dictionary."""
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_keys}
        return cls(**filtered_dict)
    
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str) -> "HubertConfig":
        """Load config from pretrained model."""
        import os
        import json
        
        config_file = os.path.join(pretrained_model_name_or_path, "config.json")
        with open(config_file, "r") as f:
            config_dict = json.load(f)
        
        return cls.from_dict(config_dict)