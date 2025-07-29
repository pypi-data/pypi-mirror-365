"""Layer implementations for HuBERT models."""

import mlx.core as mx
import mlx.nn as nn
from typing import Optional, Tuple


class HubertSamePadLayer(nn.Module):
    """Implements same padding for convolution layers.
    
    Args:
        num_conv_pos_embeddings: Number of convolutional positional embeddings.
    """
    
    def __init__(self, num_conv_pos_embeddings: int):
        super().__init__()
        self.num_pad_remove = 1 if num_conv_pos_embeddings % 2 == 0 else 0

    def __call__(self, hidden_states: mx.array) -> mx.array:
        """Apply same padding by removing excess padding if needed.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, channels).
            
        Returns:
            Tensor with adjusted padding.
        """
        if self.num_pad_remove > 0:
            hidden_states = hidden_states[:, :-self.num_pad_remove, :]
        return hidden_states


class HubertNoLayerNormConvLayer(nn.Module):
    """Convolutional layer without layer normalization.
    
    Args:
        config: Model configuration.
        layer_id: Index of the layer in the feature extractor.
    """
    
    def __init__(self, config, layer_id: int = 0):
        super().__init__()
        self.in_conv_dim = config.conv_dim[layer_id - 1] if layer_id > 0 else 1
        self.out_conv_dim = config.conv_dim[layer_id]

        self.conv = nn.Conv1d(
            self.in_conv_dim,
            self.out_conv_dim,
            kernel_size=config.conv_kernel[layer_id],
            stride=config.conv_stride[layer_id],
            bias=config.conv_bias,
        )
        self.activation = nn.gelu if config.feat_extract_activation == "gelu" else nn.relu

    def __call__(self, hidden_states: mx.array) -> mx.array:
        """Apply convolution and activation.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, channels).
            
        Returns:
            Activated tensor.
        """
        hidden_states = self.conv(hidden_states)
        hidden_states = self.activation(hidden_states)
        return hidden_states


class HubertLayerNormConvLayer(nn.Module):
    """Convolutional layer with layer normalization.
    
    Args:
        config: Model configuration.
        layer_id: Index of the layer in the feature extractor.
    """
    
    def __init__(self, config, layer_id: int = 0):
        super().__init__()
        self.in_conv_dim = config.conv_dim[layer_id - 1] if layer_id > 0 else 1
        self.out_conv_dim = config.conv_dim[layer_id]

        self.conv = nn.Conv1d(
            self.in_conv_dim,
            self.out_conv_dim,
            kernel_size=config.conv_kernel[layer_id],
            stride=config.conv_stride[layer_id],
            bias=config.conv_bias,
        )
        self.layer_norm = nn.LayerNorm(self.out_conv_dim, eps=config.layer_norm_eps)
        self.activation = nn.gelu if config.feat_extract_activation == "gelu" else nn.relu

    def __call__(self, hidden_states: mx.array) -> mx.array:
        """Apply convolution, layer norm, and activation.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, channels).
            
        Returns:
            Normalized and activated tensor.
        """
        hidden_states = self.conv(hidden_states)
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.activation(hidden_states)
        return hidden_states


class HubertGroupNormConvLayer(nn.Module):
    """Convolutional layer with group normalization.
    
    Args:
        config: Model configuration.
        layer_id: Index of the layer in the feature extractor.
    """
    
    def __init__(self, config, layer_id: int = 0):
        super().__init__()
        self.in_conv_dim = config.conv_dim[layer_id - 1] if layer_id > 0 else 1
        self.out_conv_dim = config.conv_dim[layer_id]

        self.conv = nn.Conv1d(
            self.in_conv_dim,
            self.out_conv_dim,
            kernel_size=config.conv_kernel[layer_id],
            stride=config.conv_stride[layer_id],
            bias=config.conv_bias,
        )
        self.layer_norm = nn.GroupNorm(
            self.out_conv_dim, self.out_conv_dim, pytorch_compatible=True
        )
        self.activation = nn.gelu if config.feat_extract_activation == "gelu" else nn.relu

    def __call__(self, hidden_states: mx.array) -> mx.array:
        """Apply convolution, group norm, and activation.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, channels).
            
        Returns:
            Normalized and activated tensor.
        """
        hidden_states = self.conv(hidden_states)
        hidden_states = self.layer_norm(hidden_states)
        
        hidden_states = self.activation(hidden_states)
        return hidden_states


class HubertPositionalConvEmbedding(nn.Module):
    """Convolutional positional embeddings.
    
    Args:
        config: Model configuration.
    """
    
    def __init__(self, config):
        super().__init__()
        self.conv = nn.Conv1d(
            config.hidden_size,
            config.hidden_size,
            kernel_size=config.num_conv_pos_embeddings,
            padding=config.num_conv_pos_embeddings // 2,
            groups=config.num_conv_pos_embedding_groups,
        )

        self.batch_norm = None
        self.conv_pos_batch_norm = config.conv_pos_batch_norm
        if config.conv_pos_batch_norm:
            self.batch_norm = nn.BatchNorm(config.hidden_size)

        self.padding = HubertSamePadLayer(config.num_conv_pos_embeddings)
        self.activation = nn.gelu if config.feat_extract_activation == "gelu" else nn.relu

    def __call__(self, hidden_states: mx.array) -> mx.array:
        """Apply convolutional positional embeddings.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, channels).
            
        Returns:
            Tensor with positional embeddings applied.
        """
        if self.batch_norm is not None:
            # BatchNorm expects (batch, channels, length) so we need to transpose
            hidden_states = mx.transpose(hidden_states, (0, 2, 1))
            hidden_states = self.batch_norm(hidden_states)
            hidden_states = mx.transpose(hidden_states, (0, 2, 1))
        
        hidden_states = self.conv(hidden_states)
        hidden_states = self.padding(hidden_states)
        hidden_states = self.activation(hidden_states)
        
        return hidden_states


class HubertFeatureEncoder(nn.Module):
    """Convolutional feature encoder for raw audio.
    
    Converts raw audio waveform into learned representations through
    a series of 1D convolutional layers.
    
    Args:
        config: Model configuration.
    """
    
    def __init__(self, config):
        super().__init__()
        
        if config.feat_extract_norm == "group":
            conv_layers = [HubertGroupNormConvLayer(config, layer_id=0)] + [
                HubertNoLayerNormConvLayer(config, layer_id=i + 1) 
                for i in range(config.num_feat_extract_layers - 1)
            ]
        elif config.feat_extract_norm == "layer":
            conv_layers = [
                HubertLayerNormConvLayer(config, layer_id=i) 
                for i in range(config.num_feat_extract_layers)
            ]
        else:
            raise ValueError(
                f"`config.feat_extract_norm` is {config.feat_extract_norm}, "
                f"but has to be one of ['group', 'layer']"
            )
        
        self.num_layers = len(conv_layers)
        for i, layer in enumerate(conv_layers):
            setattr(self, f"conv_layer_{i}", layer)

    def __call__(self, input_values: mx.array) -> mx.array:
        """Extract features from raw audio.
        
        Args:
            input_values: Raw audio waveform of shape (batch, length).
            
        Returns:
            Extracted features of shape (batch, new_length, hidden_size).
        """
        # MLX expects channel-last format: (batch, length, channels)
        # Input is (batch, length), so add channel dimension at the end
        hidden_states = mx.expand_dims(input_values, axis=-1)
        
        for i in range(self.num_layers):
            conv_layer = getattr(self, f"conv_layer_{i}")
            hidden_states = conv_layer(hidden_states)
        
        return hidden_states
    
    def freeze(self):
        """Freeze all parameters in the feature encoder."""
        for i in range(self.num_layers):
            layer = getattr(self, f"conv_layer_{i}")
            layer.freeze()


class HubertFeatureProjection(nn.Module):
    """Projects extracted features to model dimension.
    
    Args:
        config: Model configuration.
    """
    
    def __init__(self, config):
        super().__init__()
        self.feat_proj_layer_norm = config.feat_proj_layer_norm
        if self.feat_proj_layer_norm:
            self.layer_norm = nn.LayerNorm(config.conv_dim[-1], eps=config.layer_norm_eps)
        self.projection = nn.Linear(config.conv_dim[-1], config.hidden_size)

    def __call__(self, hidden_states: mx.array) -> mx.array:
        """Project features to model dimension.
        
        Args:
            hidden_states: Input features of shape (batch, length, conv_dim).
            
        Returns:
            Projected features of shape (batch, length, hidden_size).
        """
        if self.feat_proj_layer_norm:
            hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.projection(hidden_states)
        return hidden_states


class HubertAttention(nn.Module):
    """Multi-head self-attention layer.
    
    Args:
        config: Model configuration.
        layer_idx: Optional layer index for logging.
    """
    
    def __init__(self, config, layer_idx: Optional[int] = None):
        super().__init__()
        self.embed_dim = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = self.embed_dim // self.num_heads
        self.scaling = self.head_dim**-0.5

        self.k_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.v_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.q_proj = nn.Linear(self.embed_dim, self.embed_dim)
        self.out_proj = nn.Linear(self.embed_dim, self.embed_dim)

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
        output_attentions: bool = False,
    ) -> Tuple[mx.array, Optional[mx.array]]:
        """Apply multi-head self-attention.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, hidden_size).
            attention_mask: Optional attention mask.
            output_attentions: Whether to return attention weights.
            
        Returns:
            Tuple of (output, attention_weights) where attention_weights is None
            if output_attentions is False.
        """
        batch_size, seq_length, _ = hidden_states.shape

        queries = self.q_proj(hidden_states)
        keys = self.k_proj(hidden_states)
        values = self.v_proj(hidden_states)

        queries = queries.reshape(batch_size, seq_length, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)
        keys = keys.reshape(batch_size, seq_length, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)
        values = values.reshape(batch_size, seq_length, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)

        if output_attentions:
            # If we need attention weights, compute them manually
            queries_scaled = queries * self.scaling
            attn_weights = queries_scaled @ keys.transpose(0, 1, 3, 2)
            
            if attention_mask is not None:
                # Reshape attention_mask from (batch, seq_len) to (batch, 1, 1, seq_len)
                attention_mask_reshaped = attention_mask[:, None, None, :]
                # Create a mask that's -inf where mask is 0 (padding positions)
                attention_mask_reshaped = mx.where(attention_mask_reshaped == 0, -1e9, 0.0)
                attn_weights = attn_weights + attention_mask_reshaped
            
            attn_probs = mx.softmax(attn_weights, axis=-1)
            attn_output = attn_probs @ values
        else:
            # Use optimized scaled_dot_product_attention when we don't need attention weights
            # Prepare mask for scaled_dot_product_attention
            if attention_mask is not None:
                # Create additive mask: 0 for attended positions, large negative for masked positions
                # The mask should be (batch, heads, seq_len, seq_len) for full attention
                # But we can use broadcasting with (batch, 1, 1, seq_len)
                mask = attention_mask[:, None, None, :]
                mask = mx.where(mask == 0, mx.finfo(queries.dtype).min, 0.0)
            else:
                mask = None
            
            # Use fast scaled dot product attention
            attn_output = mx.fast.scaled_dot_product_attention(
                queries, keys, values, scale=self.scaling, mask=mask
            )
            attn_probs = None

        attn_output = attn_output.transpose(0, 2, 1, 3).reshape(batch_size, seq_length, self.embed_dim)
        attn_output = self.out_proj(attn_output)

        outputs = (attn_output, attn_probs) if output_attentions else (attn_output, None)
        return outputs


class HubertFeedForward(nn.Module):
    """Feed-forward network layer.
    
    Args:
        config: Model configuration.
    """
    
    def __init__(self, config):
        super().__init__()
        self.intermediate_dense = nn.Linear(config.hidden_size, config.intermediate_size)
        self.intermediate_act_fn = nn.gelu if config.hidden_act == "gelu" else nn.relu
        self.output_dense = nn.Linear(config.intermediate_size, config.hidden_size)

    def __call__(self, hidden_states: mx.array) -> mx.array:
        """Apply feed-forward transformation.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, hidden_size).
            
        Returns:
            Transformed tensor of same shape.
        """
        hidden_states = self.intermediate_dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        hidden_states = self.output_dense(hidden_states)
        return hidden_states


class HubertEncoderLayer(nn.Module):
    """Transformer encoder layer.
    
    Args:
        config: Model configuration.
        layer_idx: Optional layer index for logging.
    """
    
    def __init__(self, config, layer_idx: Optional[int] = None):
        super().__init__()
        self.attention = HubertAttention(config, layer_idx=layer_idx)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.feed_forward = HubertFeedForward(config)
        self.final_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
        output_attentions: bool = False,
    ) -> Tuple[mx.array, ...]:
        """Apply transformer encoder layer.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, hidden_size).
            attention_mask: Optional attention mask.
            output_attentions: Whether to return attention weights.
            
        Returns:
            Tuple of (output, attention_weights) where attention_weights is included
            only if output_attentions is True.
        """
        attn_residual = hidden_states
        hidden_states, attn_weights = self.attention(
            hidden_states,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
        )
        hidden_states = attn_residual + hidden_states

        hidden_states = self.layer_norm(hidden_states)
        hidden_states = hidden_states + self.feed_forward(hidden_states)
        hidden_states = self.final_layer_norm(hidden_states)

        outputs = (hidden_states,)

        if output_attentions:
            outputs += (attn_weights,)

        return outputs


class HubertEncoderLayerStableLayerNorm(nn.Module):
    """Transformer encoder layer with stable layer norm architecture.
    
    This variant applies layer normalization before the self-attention
    and feed-forward layers rather than after.
    
    Args:
        config: Model configuration.
        layer_idx: Optional layer index for logging.
    """
    
    def __init__(self, config, layer_idx: Optional[int] = None):
        super().__init__()
        self.attention = HubertAttention(config, layer_idx=layer_idx)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.feed_forward = HubertFeedForward(config)
        self.final_layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
        output_attentions: bool = False,
    ) -> Tuple[mx.array, ...]:
        """Apply transformer encoder layer with stable layer norm.
        
        Args:
            hidden_states: Input tensor of shape (batch, length, hidden_size).
            attention_mask: Optional attention mask.
            output_attentions: Whether to return attention weights.
            
        Returns:
            Tuple of (output, attention_weights) where attention_weights is included
            only if output_attentions is True.
        """
        attn_residual = hidden_states
        hidden_states = self.layer_norm(hidden_states)
        hidden_states, attn_weights = self.attention(
            hidden_states,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
        )
        hidden_states = attn_residual + hidden_states

        hidden_states = hidden_states + self.feed_forward(self.final_layer_norm(hidden_states))

        outputs = (hidden_states,)

        if output_attentions:
            outputs += (attn_weights,)

        return outputs


class HubertEncoder(nn.Module):
    """Transformer encoder for HuBERT.
    
    Args:
        config: Model configuration.
    """
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.pos_conv_embed = HubertPositionalConvEmbedding(config)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        
        for i in range(config.num_hidden_layers):
            if config.do_stable_layer_norm:
                layer = HubertEncoderLayerStableLayerNorm(config, layer_idx=i)
            else:
                layer = HubertEncoderLayer(config, layer_idx=i)
            setattr(self, f"layer_{i}", layer)

    def __call__(
        self,
        hidden_states: mx.array,
        attention_mask: Optional[mx.array] = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ) -> dict:
        """Apply transformer encoder.
        
        Args:
            hidden_states: Input features of shape (batch, length, hidden_size).
            attention_mask: Optional attention mask.
            output_attentions: Whether to return attention weights.
            output_hidden_states: Whether to return all hidden states.
            return_dict: Whether to return a dictionary.
            
        Returns:
            Dictionary with keys:
                - last_hidden_state: Final layer output.
                - hidden_states: All layer outputs (if output_hidden_states).
                - attentions: All attention weights (if output_attentions).
        """
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None

        if attention_mask is not None:
            hidden_states = hidden_states * mx.expand_dims(attention_mask, axis=-1)

        position_embeddings = self.pos_conv_embed(hidden_states)
        hidden_states = hidden_states + position_embeddings
        
        if not self.config.do_stable_layer_norm:
            hidden_states = self.layer_norm(hidden_states)

        for i in range(self.config.num_hidden_layers):
            layer = getattr(self, f"layer_{i}")
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states,)

            layer_outputs = layer(
                hidden_states,
                attention_mask=attention_mask,
                output_attentions=output_attentions,
            )

            hidden_states = layer_outputs[0]

            if output_attentions:
                all_self_attentions = all_self_attentions + (layer_outputs[1],)

        if self.config.do_stable_layer_norm:
            hidden_states = self.layer_norm(hidden_states)

        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)

        if not return_dict:
            return tuple(v for v in [hidden_states, all_hidden_states, all_self_attentions] if v is not None)

        return {
            "last_hidden_state": hidden_states,
            "hidden_states": all_hidden_states,
            "attentions": all_self_attentions,
        }