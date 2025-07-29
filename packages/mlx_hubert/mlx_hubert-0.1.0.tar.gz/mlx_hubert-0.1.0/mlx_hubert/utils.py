"""Utility functions for model loading and saving."""

import json
import mlx.core as mx
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
import warnings
from safetensors import safe_open
from safetensors.numpy import save_file
from huggingface_hub import hf_hub_download
import os
import time

from .config import HubertConfig
from .model import HubertForCTC, HubertModel


def load_pytorch_weights(model, pytorch_state_dict: Dict[str, Any], config: HubertConfig):
    """Load PyTorch weights into MLX model.
    
    This function handles the conversion of PyTorch tensors to MLX arrays
    and manages differences in tensor layouts between frameworks.
    
    Args:
        model: MLX model instance.
        pytorch_state_dict: PyTorch state dictionary.
        config: Model configuration.
        
    Returns:
        Updated model with loaded weights.
    """
    
    # Check if this is a CTC model or base model
    is_ctc_model = hasattr(model, 'hubert')
    
    # Define weight mapping from MLX names to PyTorch names
    weight_map = {}
    
    if is_ctc_model:
        # For CTC model, weights are under model.hubert
        # Feature extractor conv layers
        weight_map["hubert.feature_extractor.conv_layer_0.conv.weight"] = "hubert.feature_extractor.conv_layers.0.conv.weight"
        if config.conv_bias:
            weight_map["hubert.feature_extractor.conv_layer_0.conv.bias"] = "hubert.feature_extractor.conv_layers.0.conv.bias"
        weight_map["hubert.feature_extractor.conv_layer_0.layer_norm.weight"] = "hubert.feature_extractor.conv_layers.0.layer_norm.weight"
        weight_map["hubert.feature_extractor.conv_layer_0.layer_norm.bias"] = "hubert.feature_extractor.conv_layers.0.layer_norm.bias"
        
        weight_map.update({
            
            # Feature projection
            "hubert.feature_projection.layer_norm.weight": "hubert.feature_projection.layer_norm.weight",
            "hubert.feature_projection.layer_norm.bias": "hubert.feature_projection.layer_norm.bias",
            "hubert.feature_projection.projection.weight": "hubert.feature_projection.projection.weight",
            "hubert.feature_projection.projection.bias": "hubert.feature_projection.projection.bias",
            
            # Positional conv embedding bias only
            "hubert.encoder.pos_conv_embed.conv.bias": "hubert.encoder.pos_conv_embed.conv.bias",
            
            # Encoder layer norm
            "hubert.encoder.layer_norm.weight": "hubert.encoder.layer_norm.weight",
            "hubert.encoder.layer_norm.bias": "hubert.encoder.layer_norm.bias",
            
            # LM head
            "lm_head.weight": "lm_head.weight",
            "lm_head.bias": "lm_head.bias",
        })
    else:
        # For base model, weights are at the root without 'hubert.' prefix
        # Feature extractor conv layers
        weight_map["feature_extractor.conv_layer_0.conv.weight"] = "feature_extractor.conv_layers.0.conv.weight"
        if config.conv_bias:
            weight_map["feature_extractor.conv_layer_0.conv.bias"] = "feature_extractor.conv_layers.0.conv.bias"
        weight_map["feature_extractor.conv_layer_0.layer_norm.weight"] = "feature_extractor.conv_layers.0.layer_norm.weight"
        weight_map["feature_extractor.conv_layer_0.layer_norm.bias"] = "feature_extractor.conv_layers.0.layer_norm.bias"
        
        weight_map.update({
            
            # Feature projection
            "feature_projection.layer_norm.weight": "feature_projection.layer_norm.weight",
            "feature_projection.layer_norm.bias": "feature_projection.layer_norm.bias",
            "feature_projection.projection.weight": "feature_projection.projection.weight",
            "feature_projection.projection.bias": "feature_projection.projection.bias",
            
            # Positional conv embedding bias only
            "encoder.pos_conv_embed.conv.bias": "encoder.pos_conv_embed.conv.bias",
            
            # Encoder layer norm
            "encoder.layer_norm.weight": "encoder.layer_norm.weight",
            "encoder.layer_norm.bias": "encoder.layer_norm.bias",
        })
    
    # Add mappings for all conv layers (starting from layer 1, layer 0 was handled above)
    for i in range(1, config.num_feat_extract_layers):
        if is_ctc_model:
            weight_map[f"hubert.feature_extractor.conv_layer_{i}.conv.weight"] = f"hubert.feature_extractor.conv_layers.{i}.conv.weight"
            if config.conv_bias:
                weight_map[f"hubert.feature_extractor.conv_layer_{i}.conv.bias"] = f"hubert.feature_extractor.conv_layers.{i}.conv.bias"
            # Add layer norm mappings based on feat_extract_norm setting
            if config.feat_extract_norm == "layer":
                weight_map[f"hubert.feature_extractor.conv_layer_{i}.layer_norm.weight"] = f"hubert.feature_extractor.conv_layers.{i}.layer_norm.weight"
                weight_map[f"hubert.feature_extractor.conv_layer_{i}.layer_norm.bias"] = f"hubert.feature_extractor.conv_layers.{i}.layer_norm.bias"
        else:
            weight_map[f"feature_extractor.conv_layer_{i}.conv.weight"] = f"feature_extractor.conv_layers.{i}.conv.weight"
            if config.conv_bias:
                weight_map[f"feature_extractor.conv_layer_{i}.conv.bias"] = f"feature_extractor.conv_layers.{i}.conv.bias"
            # Add layer norm mappings based on feat_extract_norm setting
            if config.feat_extract_norm == "layer":
                weight_map[f"feature_extractor.conv_layer_{i}.layer_norm.weight"] = f"feature_extractor.conv_layers.{i}.layer_norm.weight"
                weight_map[f"feature_extractor.conv_layer_{i}.layer_norm.bias"] = f"feature_extractor.conv_layers.{i}.layer_norm.bias"
    
    # Add mappings for encoder layers
    for i in range(config.num_hidden_layers):
        if is_ctc_model:
            layer_prefix = f"hubert.encoder.layer_{i}"
        else:
            layer_prefix = f"encoder.layer_{i}"
        pt_prefix = f"hubert.encoder.layers.{i}" if is_ctc_model else f"encoder.layers.{i}"
        
        # Self attention
        weight_map[f"{layer_prefix}.attention.q_proj.weight"] = f"{pt_prefix}.attention.q_proj.weight"
        weight_map[f"{layer_prefix}.attention.q_proj.bias"] = f"{pt_prefix}.attention.q_proj.bias"
        weight_map[f"{layer_prefix}.attention.k_proj.weight"] = f"{pt_prefix}.attention.k_proj.weight"
        weight_map[f"{layer_prefix}.attention.k_proj.bias"] = f"{pt_prefix}.attention.k_proj.bias"
        weight_map[f"{layer_prefix}.attention.v_proj.weight"] = f"{pt_prefix}.attention.v_proj.weight"
        weight_map[f"{layer_prefix}.attention.v_proj.bias"] = f"{pt_prefix}.attention.v_proj.bias"
        weight_map[f"{layer_prefix}.attention.out_proj.weight"] = f"{pt_prefix}.attention.out_proj.weight"
        weight_map[f"{layer_prefix}.attention.out_proj.bias"] = f"{pt_prefix}.attention.out_proj.bias"
        
        # Layer norms
        weight_map[f"{layer_prefix}.layer_norm.weight"] = f"{pt_prefix}.layer_norm.weight"
        weight_map[f"{layer_prefix}.layer_norm.bias"] = f"{pt_prefix}.layer_norm.bias"
        weight_map[f"{layer_prefix}.final_layer_norm.weight"] = f"{pt_prefix}.final_layer_norm.weight"
        weight_map[f"{layer_prefix}.final_layer_norm.bias"] = f"{pt_prefix}.final_layer_norm.bias"
        
        # Feed forward
        weight_map[f"{layer_prefix}.feed_forward.intermediate_dense.weight"] = f"{pt_prefix}.feed_forward.intermediate_dense.weight"
        weight_map[f"{layer_prefix}.feed_forward.intermediate_dense.bias"] = f"{pt_prefix}.feed_forward.intermediate_dense.bias"
        weight_map[f"{layer_prefix}.feed_forward.output_dense.weight"] = f"{pt_prefix}.feed_forward.output_dense.weight"
        weight_map[f"{layer_prefix}.feed_forward.output_dense.bias"] = f"{pt_prefix}.feed_forward.output_dense.bias"
    
    # Convert weights
    new_state = {}
    missing_keys = []
    for mlx_key, pt_key in weight_map.items():
        if pt_key in pytorch_state_dict:
            tensor = pytorch_state_dict[pt_key]
            if hasattr(tensor, 'detach'):
                tensor = tensor.detach().cpu().numpy()
            elif not isinstance(tensor, np.ndarray):
                tensor = np.array(tensor)
            
            # Handle different tensor layouts
            if "conv" in mlx_key and "weight" in mlx_key and len(tensor.shape) == 3:
                # Conv1d weights: PyTorch uses (out_channels, in_channels, kernel_size)
                # MLX uses (out_channels, kernel_size, in_channels)
                tensor = tensor.transpose(0, 2, 1)
            
            new_state[mlx_key] = mx.array(tensor)
        else:
            missing_keys.append(pt_key)
    
    # Handle weight norm for pos_conv_embed
    pos_conv_key_prefix = "hubert.encoder.pos_conv_embed" if is_ctc_model else "encoder.pos_conv_embed"
    if f"{pos_conv_key_prefix}.conv.parametrizations.weight.original0" in pytorch_state_dict:
        # Reconstruct weight from weight norm parametrization
        g = pytorch_state_dict[f"{pos_conv_key_prefix}.conv.parametrizations.weight.original0"]
        v = pytorch_state_dict[f"{pos_conv_key_prefix}.conv.parametrizations.weight.original1"]
        
        if hasattr(g, 'detach'):
            g = g.detach().cpu().numpy()
        if hasattr(v, 'detach'):
            v = v.detach().cpu().numpy()
            
        # Weight norm for pos_conv_embed uses a special parametrization:
        # g shape: (1, 1, kernel_size) - gain per kernel position
        # v shape: (out_channels, in_channels, kernel_size)
        # norm is computed over dims (0,1) giving shape (1, 1, kernel_size)
        # weight = g * v / norm
        
        # Compute norm per kernel position
        v_reshaped = v.reshape(-1, v.shape[2])
        v_norm = np.linalg.norm(v_reshaped, axis=0, keepdims=True)
        v_norm = v_norm.reshape(1, 1, -1)
        
        # Normalize v
        v_normalized = v / (v_norm + 1e-12)
        
        # Apply gain
        weight = g * v_normalized
        
        # Transpose conv weight from PyTorch to MLX format
        weight = weight.transpose(0, 2, 1)
        if is_ctc_model:
            new_state["hubert.encoder.pos_conv_embed.conv.weight"] = mx.array(weight)
        else:
            new_state["encoder.pos_conv_embed.conv.weight"] = mx.array(weight)
    
    # Handle masked_spec_embed if present
    masked_embed_key = "hubert.masked_spec_embed" if is_ctc_model else "masked_spec_embed"
    if masked_embed_key in pytorch_state_dict:
        tensor = pytorch_state_dict[masked_embed_key]
        if hasattr(tensor, 'detach'):
            tensor = tensor.detach().cpu().numpy()
        # Check if model has hubert attribute (CTC model) or is the base model
        if hasattr(model, 'hubert') and hasattr(model.hubert, "masked_spec_embed"):
            model.hubert.masked_spec_embed = mx.array(tensor)
        elif hasattr(model, "masked_spec_embed"):
            model.masked_spec_embed = mx.array(tensor)
    
    # Helper functions for dictionary manipulation
    def flatten_dict(d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def unflatten_dict(flat_dict):
        nested_dict = {}
        for key, value in flat_dict.items():
            parts = key.split('.')
            d = nested_dict
            for part in parts[:-1]:
                if part not in d:
                    d[part] = {}
                d = d[part]
            d[parts[-1]] = value
        return nested_dict
    
    # Update model weights
    nested_state = unflatten_dict(new_state)
    
    # Filter out keys that don't exist in the model
    # This handles cases where bias=False in Conv layers
    model_params = dict(model.parameters())
    flat_model_params = flatten_dict(model_params)
    
    # Only keep weights that exist in the model
    filtered_state = {}
    for key, value in new_state.items():
        if key in flat_model_params:
            filtered_state[key] = value
    
    # Update with filtered state
    filtered_nested_state = unflatten_dict(filtered_state)
    model.update(filtered_nested_state)
    
    # Only warn about missing keys that are NOT conv biases when conv_bias=False
    if missing_keys:
        # Filter out expected missing conv biases
        unexpected_missing = []
        for key in missing_keys:
            if "conv.bias" in key and not config.conv_bias:
                continue  # Expected to be missing
            unexpected_missing.append(key)
        
        if unexpected_missing:
            warnings.warn(f"Some weights were not found: {unexpected_missing[:5]}{'...' if len(unexpected_missing) > 5 else ''}")
    
    return model


def load_from_safetensors(model, safetensors_path: str, config: HubertConfig):
    """Load weights from safetensors file.
    
    Args:
        model: MLX model instance.
        safetensors_path: Path to safetensors file.
        config: Model configuration.
        
    Returns:
        Model with loaded weights.
    """
    with safe_open(safetensors_path, framework="pt", device="cpu") as f:
        metadata = f.metadata()
        is_mlx_format = metadata and metadata.get("format") == "mlx"
    
    if is_mlx_format:
        weights = mx.load(safetensors_path)
        
        def unflatten_dict(flat_dict):
            nested_dict = {}
            for key, value in flat_dict.items():
                parts = key.split('.')
                d = nested_dict
                for part in parts[:-1]:
                    if part not in d:
                        d[part] = {}
                    d = d[part]
                d[parts[-1]] = value
            return nested_dict
        
        nested_weights = unflatten_dict(weights)
        model.update(nested_weights)
        return model
    else:
        state_dict = {}
        with safe_open(safetensors_path, framework="pt", device="cpu") as f:
            for key in f.keys():
                state_dict[key] = f.get_tensor(key)
        
        return load_pytorch_weights(model, state_dict, config)


def load_model(
    model_id: str,
    from_pretrained: bool = True,
    config: Optional[HubertConfig] = None,
) -> tuple:
    """Load HuBERT model from local path or HuggingFace Hub.
    
    The model type (base or CTC) is automatically determined from the config.
    
    Args:
        model_id: Local path or HuggingFace model ID.
        from_pretrained: Whether to load pretrained weights.
        config: Optional model configuration.
        
    Returns:
        Tuple of (model, config).
    """
    # Convert to absolute path if it's a relative path
    if model_id.startswith('.') or model_id.startswith('/') or os.path.exists(model_id):
        model_path = Path(model_id).resolve()
        is_local = True
    else:
        model_path = Path(model_id)
        is_local = False
    
    # Load config
    if config is None:
        if is_local and model_path.exists():
            config = HubertConfig.from_pretrained(str(model_path))
        else:
            # Try to download from HuggingFace Hub
            config_path = hf_hub_download(model_id, "config.json")
            config = HubertConfig.from_pretrained(os.path.dirname(config_path))
    
    # Initialize model based on architectures in config
    if config.architectures is not None and len(config.architectures) > 0:
        architecture = config.architectures[0]
        if architecture == "HubertForCTC":
            model = HubertForCTC(config)
        elif architecture == "HubertModel":
            model = HubertModel(config)
        else:
            raise ValueError(f"Unknown architecture: {architecture}")
    else:
        # Fallback: if no architectures specified, try to infer from vocab_size
        # CTC models typically have a small vocab_size (e.g., 32)
        if hasattr(config, 'vocab_size') and config.vocab_size < 100:
            warnings.warn(
                "No architectures field in config. Inferring HubertForCTC based on small vocab_size. "
                "Please update your model config to include architectures field."
            )
            model = HubertForCTC(config)
        else:
            warnings.warn(
                "No architectures field in config. Defaulting to HubertModel. "
                "Please update your model config to include architectures field."
            )
            model = HubertModel(config)
    
    # Load weights if requested
    if from_pretrained:
        if is_local and model_path.exists():
            # Load from local path
            safetensors_path = model_path / "model.safetensors"
            if safetensors_path.exists():
                model = load_from_safetensors(model, str(safetensors_path), config)
            else:
                raise ValueError(f"No model.safetensors found in {model_path}")
        else:
            # Download from HuggingFace Hub
            safetensors_path = hf_hub_download(model_id, "model.safetensors")
            model = load_from_safetensors(model, safetensors_path, config)
    
    return model, config


def save_model(
    model: Union[HubertModel, HubertForCTC],
    config: HubertConfig,
    save_directory: str,
):
    """Save model and configuration to directory.
    
    Args:
        model: Model to save.
        config: Model configuration.
        save_directory: Directory to save to.
    """
    save_path = Path(save_directory)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure architectures field is set correctly based on model type
    if isinstance(model, HubertForCTC):
        config.architectures = ["HubertForCTC"]
    elif isinstance(model, HubertModel):
        config.architectures = ["HubertModel"]
    
    # Save config
    config.save_pretrained(str(save_path))
    
    # Get model weights
    weights = dict(model.parameters())
    
    # Flatten nested dict structure
    def flatten_dict(d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    flat_weights = flatten_dict(weights)
    
    # Save as safetensors (MLX format)
    model_path = save_path / "model.safetensors"
    mx.save_safetensors(str(model_path), flat_weights, metadata={"format": "mlx"})
    
    # Create index file for compatibility
    total_size = sum(v.nbytes for v in flat_weights.values())
    total_params = sum(v.size for v in flat_weights.values())
    
    index_data = {
        "metadata": {
            "total_size": int(total_size),
            "total_parameters": int(total_params),
        },
        "weight_map": {k: "model.safetensors" for k in sorted(flat_weights.keys())}
    }
    
    with open(save_path / "model.safetensors.index.json", "w") as f:
        json.dump(index_data, f, indent=2)
    
    print(f"Model saved to {save_path}")


def convert_from_transformers(
    model_name: str,
    output_dir: str,
) -> Tuple[str, str]:
    """Convert HuggingFace HuBERT model to MLX format.
    
    This function loads a HuBERT model from HuggingFace and converts it
    to the MLX safetensors format for efficient loading.
    
    Args:
        model_name: HuggingFace model identifier (e.g., "facebook/hubert-large-ls960-ft").
        output_dir: Directory to save converted files.
        
    Returns:
        Tuple of (model_path, config_path).
        
    Example:
        >>> # Convert a CTC model
        >>> convert_from_transformers(
        ...     "facebook/hubert-large-ls960-ft",
        ...     "./converted_model"
        ... )
        
        >>> # Convert a base model
        >>> convert_from_transformers(
        ...     "facebook/hubert-base-ls960",
        ...     "./converted_base"
        ... )
    """
    try:
        from transformers import (
            HubertForCTC as HFHubertForCTC,
            HubertModel as HFHubertModel,
            Wav2Vec2Processor,
            Wav2Vec2CTCTokenizer,
            AutoConfig,
        )
        import torch
    except ImportError as e:
        raise ImportError(
            f"Missing dependencies for conversion: {e}\n"
            "Install with: pip install transformers torch"
        )
    
    print(f"\n{'='*60}")
    print(f"Converting Model: {model_name}")
    print(f"{'='*60}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load model
    print("1. Loading model from HuggingFace...")
    start_time = time.time()
    
    config = AutoConfig.from_pretrained(model_name)
    if hasattr(config, "architectures") and config.architectures:
        if "HubertForCTC" in config.architectures[0]:
            model_type = "ctc"
        else:
            model_type = "base"
    elif "ft" in model_name or "ctc" in model_name.lower():
        model_type = "ctc"
    else:
        model_type = "base"
    
    if model_type == "ctc":
        print("   Using HubertForCTC (has CTC head)")
        model = HFHubertForCTC.from_pretrained(model_name, use_safetensors=True)
    else:
        print("   Using HubertModel (base model)")
        model = HFHubertModel.from_pretrained(model_name, use_safetensors=True)
    
    config = model.config
    load_time = time.time() - start_time
    print(f"   ✓ Loaded in {load_time:.2f}s")
    
    state_dict = model.state_dict()
    
    total_params = sum(p.numel() for p in state_dict.values())
    total_size_mb = sum(p.numel() * p.element_size() for p in state_dict.values()) / (1024 * 1024)
    
    ctc_params = {k: v for k, v in state_dict.items() if "lm_head" in k}
    ctc_param_count = sum(p.numel() for p in ctc_params.values()) if ctc_params else 0
    
    print(f"2. Model statistics:")
    print(f"   - Model type: {model_type}")
    print(f"   - Total parameters: {total_params:,}")
    if ctc_params:
        print(f"   - CTC head parameters: {ctc_param_count:,}")
    print(f"   - Size: {total_size_mb:.2f} MB")
    print(f"   - Layers: {len(state_dict)}")
    
    model_path = os.path.join(output_dir, "model.safetensors")
    print("3. Saving safetensors format...")
    
    metadata = {
        "format": "pt",
        "model_name": model_name,
        "model_type": config.model_type,
        "architecture": model.__class__.__name__,
        "has_ctc_head": str(bool(ctc_params)),
        "vocab_size": str(config.vocab_size),
        "total_parameters": str(total_params),
        "ctc_parameters": str(ctc_param_count)
    }
    
    save_file(state_dict, model_path, metadata=metadata)
    print(f"   ✓ Saved to: {model_path}")
    
    config_path = os.path.join(output_dir, "config.json")
    config.save_pretrained(output_dir)
    print(f"   ✓ Config saved")
    
    print("4. Saving processor components...")
    
    preprocessor_config = {
        "do_normalize": True,
        "feature_extractor_type": "Wav2Vec2FeatureExtractor",
        "feature_size": 1,
        "padding_side": "right",
        "padding_value": 0.0,
        "return_attention_mask": True,
        "sampling_rate": 16000
    }
    with open(os.path.join(output_dir, "preprocessor_config.json"), 'w') as f:
        json.dump(preprocessor_config, f, indent=2)
    print(f"   ✓ Preprocessor config saved")
    
    processor_saved = False
    try:
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        processor.save_pretrained(output_dir)
        processor_saved = True
        print(f"   ✓ Processor saved (includes tokenizer if CTC model)")
    except Exception as e:
        print(f"   ⚠ Could not load full processor: {e}")
    
    if not processor_saved and model_type == "ctc":
        print("   Attempting to save tokenizer separately...")
        try:
            tokenizer = Wav2Vec2CTCTokenizer.from_pretrained(model_name)
            tokenizer.save_pretrained(output_dir)
            print(f"   ✓ Tokenizer saved")
        except Exception as e:
            print(f"   ⚠ Could not load tokenizer: {e}")
            
            vocab = {
                "<pad>": 0, "<s>": 1, "</s>": 2, "<unk>": 3,
                "|": 4, "E": 5, "T": 6, "A": 7, "O": 8, "N": 9,
                "I": 10, "H": 11, "S": 12, "R": 13, "D": 14, "L": 15,
                "U": 16, "M": 17, "W": 18, "C": 19, "F": 20, "G": 21,
                "Y": 22, "P": 23, "B": 24, "V": 25, "K": 26, "'": 27,
                "X": 28, "J": 29, "Q": 30, "Z": 31
            }
            with open(os.path.join(output_dir, "vocab.json"), 'w') as f:
                json.dump(vocab, f, indent=2)
            
            tokenizer_config = {
                "unk_token": "<unk>",
                "bos_token": "<s>",
                "eos_token": "</s>",
                "pad_token": "<pad>",
                "do_lower_case": False,
                "word_delimiter_token": "|",
                "tokenizer_class": "Wav2Vec2CTCTokenizer"
            }
            with open(os.path.join(output_dir, "tokenizer_config.json"), 'w') as f:
                json.dump(tokenizer_config, f, indent=2)
            
            special_tokens_map = {
                "bos_token": "<s>",
                "eos_token": "</s>",
                "unk_token": "<unk>",
                "pad_token": "<pad>"
            }
            with open(os.path.join(output_dir, "special_tokens_map.json"), 'w') as f:
                json.dump(special_tokens_map, f, indent=2)
            
            print(f"   ✓ Created basic tokenizer files")
    
    # List saved files
    print(f"\n5. Files created in {output_dir}:")
    for file in sorted(os.listdir(output_dir)):
        file_path = os.path.join(output_dir, file)
        if os.path.isfile(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"   - {file} ({size_kb:.1f} KB)")
    
    return model_path, config_path