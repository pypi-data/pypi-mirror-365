"""Audio processing utilities for HuBERT."""

import mlx.core as mx
import numpy as np
from typing import List, Union, Optional, Dict
import warnings


class HubertProcessor:
    """Processor for preparing audio inputs and decoding model outputs.
    
    This processor handles audio preprocessing and token decoding for HuBERT models.
    It's designed to be compatible with the Wav2Vec2Processor interface.
    
    Args:
        vocab_dict: Dictionary mapping tokens to indices.
        sampling_rate: Expected sampling rate of input audio.
        padding_value: Value to use for padding.
        return_attention_mask: Whether to return attention masks.
        do_normalize: Whether to normalize audio to zero mean and unit variance.
    """
    
    def __init__(
        self,
        vocab_dict: Optional[Dict[str, int]] = None,
        sampling_rate: int = 16000,
        padding_value: float = 0.0,
        return_attention_mask: bool = True,
        do_normalize: bool = True,
    ):
        self.sampling_rate = sampling_rate
        self.padding_value = padding_value
        self.return_attention_mask = return_attention_mask
        self.do_normalize = do_normalize
        
        # Default CTC vocabulary if not provided
        if vocab_dict is None:
            # Basic English alphabet + special tokens
            vocab_dict = {
                "<pad>": 0, "<s>": 1, "</s>": 2, "<unk>": 3,
                "|": 4, "E": 5, "T": 6, "A": 7, "O": 8, "N": 9,
                "I": 10, "H": 11, "S": 12, "R": 13, "D": 14, "L": 15,
                "U": 16, "M": 17, "W": 18, "C": 19, "F": 20, "G": 21,
                "Y": 22, "P": 23, "B": 24, "V": 25, "K": 26, "'": 27,
                "X": 28, "J": 29, "Q": 30, "Z": 31,
            }
        
        self.vocab_dict = vocab_dict
        self.vocab_dict_inv = {v: k for k, v in vocab_dict.items()}
        self.pad_token_id = vocab_dict.get("<pad>", 0)
        self.unk_token_id = vocab_dict.get("<unk>", 3)
        self.blank_token = "|"
        self.blank_token_id = vocab_dict.get("|", 4)
        self.word_delimiter_token = " "
        self.word_delimiter_token_id = vocab_dict.get(" ", vocab_dict.get("|", 4))
    
    def __call__(
        self,
        audio: Union[np.ndarray, List[np.ndarray]],
        sampling_rate: Optional[int] = None,
        padding: Union[bool, str] = True,
        max_length: Optional[int] = None,
        truncation: bool = False,
    ) -> Dict[str, mx.array]:
        """Process audio inputs for model.
        
        Args:
            audio: Raw audio waveform(s).
            sampling_rate: Sampling rate of the audio.
            padding: Whether to pad sequences to the same length.
            max_length: Maximum length to truncate/pad to.
            truncation: Whether to truncate sequences longer than max_length.
            
        Returns:
            Dictionary with MLX arrays for model input.
        """
        if sampling_rate is not None and sampling_rate != self.sampling_rate:
            warnings.warn(
                f"Audio sampling rate ({sampling_rate}) doesn't match processor's "
                f"sampling rate ({self.sampling_rate}). Resampling is recommended."
            )
        
        # Ensure input is a list
        if isinstance(audio, np.ndarray):
            if audio.ndim == 1:
                audio = [audio]
            else:
                audio = list(audio)
        
        # Process each audio sequence
        processed = []
        lengths = []
        
        for seq in audio:
            if not isinstance(seq, np.ndarray):
                seq = np.array(seq, dtype=np.float32)
            else:
                seq = seq.astype(np.float32)
            
            # Normalize if requested
            if self.do_normalize:
                mean = seq.mean()
                std = seq.std() + 1e-7
                seq = (seq - mean) / std
            
            lengths.append(len(seq))
            processed.append(seq)
        
        # Handle padding/truncation
        if padding or truncation:
            if max_length is None and padding:
                max_length = max(lengths)
            
            padded = []
            attention_mask = []
            
            for seq, length in zip(processed, lengths):
                if truncation and max_length and length > max_length:
                    seq = seq[:max_length]
                    length = max_length
                
                if padding and max_length and length < max_length:
                    padding_length = max_length - length
                    seq = np.pad(seq, (0, padding_length), constant_values=self.padding_value)
                    mask = np.ones(max_length, dtype=np.int32)
                    mask[length:] = 0
                else:
                    mask = np.ones(length, dtype=np.int32)
                
                padded.append(seq)
                attention_mask.append(mask)
            
            processed = padded
        else:
            attention_mask = [np.ones(length, dtype=np.int32) for length in lengths]
        
        # Stack into batch and convert to MLX arrays
        input_values = mx.array(np.stack(processed))
        
        result = {"input_values": input_values}
        
        if self.return_attention_mask:
            result["attention_mask"] = mx.array(np.stack(attention_mask))
        
        return result
    
    def decode(
        self,
        token_ids: Union[np.ndarray, List[int]],
        skip_special_tokens: bool = True,
        clean_up_tokenization_spaces: bool = True,
        output_word_offsets: bool = False,
    ) -> Union[str, Dict[str, Union[str, List[int]]]]:
        """Decode token IDs to text using CTC decoding.
        
        Args:
            token_ids: Predicted token IDs.
            skip_special_tokens: Whether to skip special tokens in output.
            clean_up_tokenization_spaces: Whether to clean up extra spaces.
            output_word_offsets: Whether to output word offsets.
            
        Returns:
            Decoded text string or dictionary with text and offsets.
        """
        if isinstance(token_ids, np.ndarray):
            token_ids = token_ids.tolist()
        
        from itertools import groupby
        grouped_tokens = [(token, len(list(group))) for token, group in groupby(token_ids)]
        
        tokens = [token for token, _ in grouped_tokens]
        
        decoded_chars = []
        
        for token in tokens:
            if skip_special_tokens and token == self.pad_token_id:
                continue
            
            if token == self.blank_token_id:
                decoded_chars.append(" ")
                continue
            
            if token in self.vocab_dict_inv:
                char = self.vocab_dict_inv[token]
                if not (skip_special_tokens and char in ["<pad>", "<s>", "</s>", "<unk>"]):
                    decoded_chars.append(char)
            else:
                if not skip_special_tokens:
                    decoded_chars.append("<unk>")
        
        # Join characters
        text = "".join(decoded_chars)
        
        # Clean up spaces
        if clean_up_tokenization_spaces:
            # Replace multiple spaces with single space
            while "  " in text:
                text = text.replace("  ", " ")
            text = text.strip()
        
        if output_word_offsets:
            # Compute word offsets
            words = text.split(" ")
            word_offsets = []
            current_offset = 0
            
            for word in words:
                if word:
                    word_offsets.append(current_offset)
                current_offset += len(word) + 1
            
            return {
                "text": text,
                "word_offsets": word_offsets,
            }
        
        return text
    
    def batch_decode(
        self,
        sequences: Union[np.ndarray, List[List[int]]],
        skip_special_tokens: bool = True,
        clean_up_tokenization_spaces: bool = True,
    ) -> List[str]:
        """Decode multiple sequences of token IDs.
        
        Args:
            sequences: Batch of token ID sequences.
            skip_special_tokens: Whether to skip special tokens.
            clean_up_tokenization_spaces: Whether to clean up spaces.
            
        Returns:
            List of decoded text strings.
        """
        return [
            self.decode(
                seq,
                skip_special_tokens=skip_special_tokens,
                clean_up_tokenization_spaces=clean_up_tokenization_spaces,
            )
            for seq in sequences
        ]
    
    @classmethod
    def from_pretrained(cls, model_id: str) -> "HubertProcessor":
        """Load processor from pretrained model.
        
        Args:
            model_id: Model identifier or path.
            
        Returns:
            Configured processor instance.
        """
        import json
        import os
        from pathlib import Path
        from huggingface_hub import hf_hub_download
        
        # Check if it's a local path
        if os.path.exists(model_id):
            model_path = Path(model_id)
            vocab_path = model_path / "vocab.json"
            config_path = model_path / "preprocessor_config.json"
        else:
            # Download from HuggingFace Hub
            try:
                vocab_path = Path(hf_hub_download(model_id, "vocab.json"))
                config_path = Path(hf_hub_download(model_id, "preprocessor_config.json"))
            except Exception:
                # If download fails, try without vocab/config
                vocab_path = None
                config_path = None
        
        # Load vocabulary
        vocab_dict = None
        if vocab_path and vocab_path.exists():
            with open(vocab_path, "r") as f:
                vocab_dict = json.load(f)
        
        # Load config
        sampling_rate = 16000
        do_normalize = True
        return_attention_mask = True
        
        if config_path and config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
            sampling_rate = config.get("sampling_rate", 16000)
            do_normalize = config.get("do_normalize", True)
            return_attention_mask = config.get("return_attention_mask", True)
        
        return cls(
            vocab_dict=vocab_dict,
            sampling_rate=sampling_rate,
            do_normalize=do_normalize,
            return_attention_mask=return_attention_mask,
        )