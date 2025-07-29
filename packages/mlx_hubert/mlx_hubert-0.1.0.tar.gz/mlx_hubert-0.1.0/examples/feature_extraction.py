"""Example of using MLX-HuBERT for feature extraction.

This example shows how to:
1. Extract speech representations from audio
2. Use features for downstream tasks
3. Visualize extracted features
"""

import mlx.core as mx
import numpy as np
from mlx_hubert import load_model, HubertProcessor
from datasets import load_dataset


def extract_features():
    """Extract HuBERT features from audio."""
    
    # Load base model (without CTC head)
    print("Loading HuBERT base model...")
    model_id = "mzbac/hubert-base-ls960"  # Base model for feature extraction
    model, config = load_model(model_id)
    model.eval()
    
    # Load processor
    processor = HubertProcessor.from_pretrained(model_id)
    
    # Load example audio
    print("Loading audio data...")
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    audio_sample = ds[0]["audio"]["array"]
    
    # Process audio
    inputs = processor(audio_sample)
    input_values = inputs["input_values"]
    
    # Extract features
    print("Extracting features...")
    outputs = model(
        input_values,
        output_hidden_states=True,  # Get all layer outputs
        return_dict=True
    )
    
    # Get features from different layers
    last_hidden_state = outputs.last_hidden_state
    all_hidden_states = outputs.hidden_states  # Tuple of all layer outputs
    
    print(f"\nFeature dimensions:")
    print(f"Last hidden state shape: {last_hidden_state.shape}")
    print(f"Number of layers: {len(all_hidden_states) if all_hidden_states else 'N/A'}")
    
    # Convert to numpy for analysis
    features_np = np.array(last_hidden_state)
    
    # Compute statistics
    print(f"\nFeature statistics:")
    print(f"Mean: {features_np.mean():.4f}")
    print(f"Std: {features_np.std():.4f}")
    print(f"Min: {features_np.min():.4f}")
    print(f"Max: {features_np.max():.4f}")
    
    return features_np


def pool_features():
    """Example of feature pooling strategies."""
    
    model_id = "mzbac/hubert-base-ls960"
    model, config = load_model(model_id)
    model.eval()
    
    processor = HubertProcessor.from_pretrained(model_id)
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    
    # Process batch
    batch_size = 3
    audio_samples = [ds[i]["audio"]["array"] for i in range(batch_size)]
    inputs = processor(audio_samples, padding=True)
    input_values = inputs["input_values"]
    
    # Extract features (without attention mask for now)
    outputs = model(input_values)
    features = outputs.last_hidden_state  # (batch, time, features)
    
    print("\nFeature pooling examples:")
    print(f"Original shape: {features.shape}")
    
    # 1. Mean pooling over time
    mean_pooled = mx.mean(features, axis=1)
    print(f"Mean pooled shape: {mean_pooled.shape}")
    
    # 2. Max pooling over time
    max_pooled = mx.max(features, axis=1)
    print(f"Max pooled shape: {max_pooled.shape}")
    
    # 3. First hidden state (CLS token equivalent)
    first_pooled = features[:, 0, :]
    print(f"First hidden shape: {first_pooled.shape}")
    
    # 4. Last hidden state
    last_pooled = features[:, -1, :]
    print(f"Last hidden shape: {last_pooled.shape}")
    
    return mean_pooled, max_pooled, last_pooled


def layer_wise_features():
    """Extract and analyze features from different layers."""
    
    model_id = "mzbac/hubert-base-ls960"
    model, config = load_model(model_id)
    model.eval()
    
    processor = HubertProcessor.from_pretrained(model_id)
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    audio_sample = ds[0]["audio"]["array"]
    
    inputs = processor(audio_sample)
    input_values = inputs["input_values"]
    
    # Get all hidden states
    outputs = model(
        input_values,
        output_hidden_states=True,
        return_dict=True
    )
    
    all_hidden_states = outputs.hidden_states
    
    print("\nLayer-wise analysis:")
    print(f"Total layers: {len(all_hidden_states)}")
    
    # Analyze each layer
    layer_stats = []
    for i, hidden_state in enumerate(all_hidden_states):
        hs_np = np.array(hidden_state)
        stats = {
            'layer': i,
            'mean': hs_np.mean(),
            'std': hs_np.std(),
            'norm': np.linalg.norm(hs_np.mean(axis=(0, 1)))
        }
        layer_stats.append(stats)
        
        if i % 4 == 0:  # Print every 4th layer
            print(f"Layer {i:2d}: mean={stats['mean']:6.3f}, "
                  f"std={stats['std']:6.3f}, norm={stats['norm']:6.3f}")
    
    # Use weighted combination of layers (learned or fixed weights)
    # Example: Simple average of last 4 layers
    last_4_layers = all_hidden_states[-4:]
    weighted_features = mx.mean(mx.stack(last_4_layers), axis=0)
    print(f"\nWeighted features shape: {weighted_features.shape}")
    
    return layer_stats


def similarity_example():
    """Compute similarity between audio samples using features."""
    
    model_id = "mzbac/hubert-base-ls960"
    model, config = load_model(model_id)
    model.eval()
    
    processor = HubertProcessor.from_pretrained(model_id)
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    
    # Extract features from multiple samples
    num_samples = 5
    all_features = []
    
    print("\nExtracting features from audio samples...")
    for i in range(num_samples):
        audio = ds[i]["audio"]["array"]
        inputs = processor(audio)
        input_values = inputs["input_values"]
        
        outputs = model(input_values)
        # Mean pool over time dimension
        features = mx.mean(outputs.last_hidden_state, axis=1)
        all_features.append(features)
    
    # Stack features
    feature_matrix = mx.squeeze(mx.stack(all_features))
    
    # Compute cosine similarity matrix
    # Normalize features
    feature_norms = mx.sqrt(mx.sum(feature_matrix * feature_matrix, axis=1, keepdims=True))
    normalized_features = feature_matrix / feature_norms
    
    # Compute similarity
    similarity_matrix = normalized_features @ normalized_features.T
    similarity_np = np.array(similarity_matrix)
    
    print("\nCosine similarity matrix:")
    print(similarity_np)
    
    # Find most similar pairs
    np.fill_diagonal(similarity_np, 0)  # Exclude self-similarity
    max_idx = np.unravel_index(np.argmax(similarity_np), similarity_np.shape)
    print(f"\nMost similar pair: samples {max_idx[0]} and {max_idx[1]} "
          f"(similarity: {similarity_np[max_idx]:.4f})")
    
    return similarity_matrix


if __name__ == "__main__":
    print("=== Basic Feature Extraction ===")
    features = extract_features()
    
    print("\n=== Feature Pooling Strategies ===")
    mean_pool, max_pool, last_pool = pool_features()
    
    print("\n=== Layer-wise Feature Analysis ===")
    layer_stats = layer_wise_features()
    
    print("\n=== Audio Similarity Example ===")
    similarity = similarity_example()