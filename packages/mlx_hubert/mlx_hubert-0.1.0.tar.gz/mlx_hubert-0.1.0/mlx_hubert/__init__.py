"""
MLX-HuBERT: HuBERT implementation in MLX for Apple Silicon.

This package provides an efficient implementation of HuBERT (Hidden Unit BERT)
optimized for Apple Silicon using the MLX framework.
"""

__version__ = "0.1.0"

from .config import HubertConfig
from .model import HubertModel, HubertForCTC
from .processor import HubertProcessor
from .utils import load_model, save_model, convert_from_transformers

__all__ = [
    "HubertConfig",
    "HubertModel", 
    "HubertForCTC",
    "HubertProcessor",
    "load_model",
    "save_model",
    "convert_from_transformers",
]