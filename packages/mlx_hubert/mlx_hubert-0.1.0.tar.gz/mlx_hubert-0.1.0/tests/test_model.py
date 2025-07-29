"""Tests for HuBERT model components."""

import pytest
import mlx.core as mx
import numpy as np
from mlx_hubert import HubertConfig, HubertModel, HubertForCTC


class TestHubertModel:
    """Test HuBERT model functionality."""
    
    @pytest.fixture
    def config(self):
        """Create a small config for testing."""
        return HubertConfig(
            hidden_size=32,
            num_hidden_layers=2,
            num_attention_heads=4,
            intermediate_size=64,
            conv_dim=[16, 32],
            conv_stride=[2, 2],
            conv_kernel=[3, 3],
            num_feat_extract_layers=2,
        )
    
    @pytest.fixture
    def model(self, config):
        """Create model instance."""
        return HubertModel(config)
    
    @pytest.fixture
    def ctc_model(self, config):
        """Create CTC model instance."""
        return HubertForCTC(config)
    
    def test_model_creation(self, model, config):
        """Test model instantiation."""
        assert model is not None
        assert model.config == config
        assert hasattr(model, 'feature_extractor')
        assert hasattr(model, 'feature_projection')
        assert hasattr(model, 'encoder')
    
    def test_forward_pass(self, model):
        """Test forward pass through model."""
        batch_size = 2
        seq_length = 1000
        
        # Create dummy input
        input_values = mx.random.normal((batch_size, seq_length))
        
        # Forward pass
        outputs = model(input_values)
        
        # Check outputs
        assert hasattr(outputs, 'last_hidden_state')
        assert outputs.last_hidden_state.shape[0] == batch_size
        assert outputs.last_hidden_state.shape[2] == model.config.hidden_size
    
    def test_ctc_forward_pass(self, ctc_model):
        """Test CTC model forward pass."""
        batch_size = 2
        seq_length = 1000
        
        # Create dummy input
        input_values = mx.random.normal((batch_size, seq_length))
        
        # Forward pass
        outputs = ctc_model(input_values)
        
        # Check outputs
        assert hasattr(outputs, 'logits')
        assert outputs.logits.shape[0] == batch_size
        assert outputs.logits.shape[2] == ctc_model.config.vocab_size
    
    def test_attention_mask(self, model):
        """Test model with attention mask."""
        batch_size = 2
        seq_length = 1000
        
        input_values = mx.random.normal((batch_size, seq_length))
        attention_mask = mx.ones((batch_size, seq_length))
        attention_mask[0, 500:] = 0  # Mask second half of first sequence
        
        outputs = model(input_values, attention_mask=attention_mask)
        
        assert outputs.last_hidden_state is not None
    
    def test_feature_extraction_output_length(self, model):
        """Test feature extraction output length calculation."""
        input_lengths = mx.array([1000, 800, 600])
        
        output_lengths = model._get_feat_extract_output_lengths(input_lengths)
        
        # Calculate expected lengths
        expected = input_lengths
        for kernel, stride in zip(model.config.conv_kernel, model.config.conv_stride):
            expected = (expected - kernel) // stride + 1
        
        assert mx.array_equal(output_lengths, expected)