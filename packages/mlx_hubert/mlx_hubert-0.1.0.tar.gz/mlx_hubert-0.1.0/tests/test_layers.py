"""Tests for HuBERT layers."""

import pytest
import mlx.core as mx
import numpy as np
from mlx_hubert.layers import (
    HubertGroupNormConvLayer,
    HubertLayerNormConvLayer,
    HubertPositionalConvEmbedding,
    HubertAttention,
    HubertFeedForward,
    HubertEncoderLayer,
)
from mlx_hubert import HubertConfig


class TestHubertLayers:
    """Test individual HuBERT layers."""
    
    @pytest.fixture
    def config(self):
        """Create config for testing."""
        return HubertConfig(
            hidden_size=32,
            num_attention_heads=4,
            intermediate_size=64,
            conv_dim=[16, 32],
            conv_stride=[2, 2],
            conv_kernel=[3, 3],
        )
    
    def test_group_norm_conv_layer(self, config):
        """Test group norm convolution layer."""
        layer = HubertGroupNormConvLayer(config, layer_id=0)
        
        # Input: (batch, length, channels)
        input_tensor = mx.random.normal((2, 100, 1))
        output = layer(input_tensor)
        
        # Check output shape
        expected_length = (100 - 3) // 2 + 1  # After conv with kernel=3, stride=2
        assert output.shape == (2, expected_length, 16)
    
    def test_layer_norm_conv_layer(self, config):
        """Test layer norm convolution layer."""
        layer = HubertLayerNormConvLayer(config, layer_id=0)
        
        input_tensor = mx.random.normal((2, 100, 1))
        output = layer(input_tensor)
        
        expected_length = (100 - 3) // 2 + 1
        assert output.shape == (2, expected_length, 16)
    
    def test_positional_conv_embedding(self, config):
        """Test positional convolution embedding."""
        layer = HubertPositionalConvEmbedding(config)
        
        # Input: (batch, length, hidden_size)
        input_tensor = mx.random.normal((2, 50, 32))
        output = layer(input_tensor)
        
        # Output should have same shape as input
        assert output.shape == input_tensor.shape
    
    def test_attention_layer(self, config):
        """Test attention layer."""
        layer = HubertAttention(config)
        
        batch_size = 2
        seq_length = 10
        hidden_size = 32
        
        hidden_states = mx.random.normal((batch_size, seq_length, hidden_size))
        
        # Test without attention mask
        output, attn_weights = layer(hidden_states, output_attentions=True)
        
        assert output.shape == (batch_size, seq_length, hidden_size)
        assert attn_weights.shape == (batch_size, 4, seq_length, seq_length)  # 4 heads
        
        # Test with attention mask
        attention_mask = mx.ones((batch_size, 1, 1, seq_length))
        attention_mask[0, :, :, 5:] = -10000.0  # Mask positions 5-9 for first batch
        
        output_masked, _ = layer(hidden_states, attention_mask=attention_mask)
        assert output_masked.shape == (batch_size, seq_length, hidden_size)
    
    def test_feed_forward_layer(self, config):
        """Test feed-forward layer."""
        layer = HubertFeedForward(config)
        
        input_tensor = mx.random.normal((2, 10, 32))
        output = layer(input_tensor)
        
        assert output.shape == input_tensor.shape
    
    def test_encoder_layer(self, config):
        """Test complete encoder layer."""
        layer = HubertEncoderLayer(config)
        
        hidden_states = mx.random.normal((2, 10, 32))
        
        outputs = layer(hidden_states, output_attentions=True)
        
        assert len(outputs) == 2  # (hidden_states, attention_weights)
        assert outputs[0].shape == hidden_states.shape
        assert outputs[1] is not None  # Attention weights
    
    def test_gelu_activation(self):
        """Test GELU activation matches expected behavior."""
        from mlx_hubert.layers import gelu
        
        # Test values
        x = mx.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        output = gelu(x)
        
        # GELU should be smooth and differentiable
        assert output.shape == x.shape
        
        # Check approximate values
        expected = mx.array([-0.0454, -0.1588, 0.0, 0.8412, 1.9546])
        assert mx.allclose(output, expected, atol=0.01)