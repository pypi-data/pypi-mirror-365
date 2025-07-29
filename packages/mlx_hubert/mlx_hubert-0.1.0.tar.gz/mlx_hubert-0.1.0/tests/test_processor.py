"""Tests for HuBERT processor."""

import pytest
import numpy as np
from mlx_hubert import HubertProcessor


class TestHubertProcessor:
    """Test HuBERT processor functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return HubertProcessor(sampling_rate=16000)
    
    def test_processor_creation(self, processor):
        """Test processor instantiation."""
        assert processor is not None
        assert processor.sampling_rate == 16000
        assert processor.pad_token_id == 0
        assert len(processor.vocab_dict) == 32
    
    def test_single_audio_processing(self, processor):
        """Test processing single audio sequence."""
        audio = np.random.randn(16000).astype(np.float32)  # 1 second
        
        outputs = processor(audio)
        
        assert "input_values" in outputs
        assert outputs["input_values"].shape == (1, 16000)
        assert "attention_mask" in outputs
        assert outputs["attention_mask"].shape == (1, 16000)
    
    def test_batch_audio_processing(self, processor):
        """Test processing batch of audio sequences."""
        audio1 = np.random.randn(16000).astype(np.float32)
        audio2 = np.random.randn(12000).astype(np.float32)
        
        outputs = processor([audio1, audio2], padding=True)
        
        assert outputs["input_values"].shape == (2, 16000)  # Padded to max length
        assert outputs["attention_mask"].shape == (2, 16000)
        assert np.all(outputs["attention_mask"][1, 12000:] == 0)  # Check padding
    
    def test_audio_normalization(self, processor):
        """Test audio normalization."""
        audio = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        
        outputs = processor(audio, do_normalize=True)
        normalized = outputs["input_values"][0]
        
        # Check normalization (zero mean, unit variance)
        assert np.abs(np.mean(normalized)) < 1e-6
        assert np.abs(np.std(normalized) - 1.0) < 1e-6
    
    def test_decode_tokens(self, processor):
        """Test token decoding."""
        # Test simple decoding
        tokens = [5, 4, 17, 5, 18]  # "A MAN"
        text = processor.decode(tokens)
        assert text == "A MAN"
        
        # Test with special tokens
        tokens = [0, 5, 0, 17, 5, 18, 0]  # With padding
        text = processor.decode(tokens, skip_special_tokens=True)
        assert text == "A MAN"
        
        # Test unknown tokens
        tokens = [5, 100, 17]  # A <unk> M
        text = processor.decode(tokens, skip_special_tokens=False)
        assert "<unk>" in text
    
    def test_batch_decode(self, processor):
        """Test batch decoding."""
        sequences = [
            [5, 4, 17, 5, 18],  # "A MAN"
            [23, 13, 22],       # "SIR"
        ]
        
        texts = processor.batch_decode(sequences)
        
        assert len(texts) == 2
        assert texts[0] == "A MAN"
        assert texts[1] == "SIR"
    
    def test_truncation(self, processor):
        """Test audio truncation."""
        audio = np.random.randn(20000).astype(np.float32)
        
        outputs = processor(audio, max_length=16000, truncation=True)
        
        assert outputs["input_values"].shape == (1, 16000)
        assert outputs["attention_mask"].shape == (1, 16000)
    
    def test_custom_vocabulary(self):
        """Test processor with custom vocabulary."""
        custom_vocab = {
            "<pad>": 0,
            "H": 1,
            "E": 2,
            "L": 3,
            "O": 4,
        }
        
        processor = HubertProcessor(vocab_dict=custom_vocab)
        
        tokens = [1, 2, 3, 3, 4]  # "HELLO"
        text = processor.decode(tokens)
        assert text == "HELLO"