"""Example of using HuBERT base model for feature extraction.

This example demonstrates:
1. Loading a pretrained HuBERT base model
2. Extracting speech representations
3. Using features for various tasks
"""

import mlx.core as mx
import numpy as np
from mlx_hubert import load_model, HubertProcessor
from datasets import load_dataset


def main():
    """Run base model feature extraction example."""
    
    # Load the converted base model
    print("Loading HuBERT base model...")
    model_id = "mzbac/hubert-base-ls960"
    model, config = load_model(model_id)
    model.eval()
    
    # Load processor
    processor = HubertProcessor.from_pretrained(model_id)
    
    # Load example audio
    print("\nLoading example audio...")
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    audio_sample = ds[0]["audio"]["array"]
    
    # Process audio
    inputs = processor(audio_sample)
    input_values = inputs["input_values"]
    
    # Extract features
    print("Extracting features...")
    outputs = model(input_values)
    features = outputs.last_hidden_state
    
    print(f"\nResults:")
    print(f"  Input audio length: {len(audio_sample)} samples ({len(audio_sample)/16000:.2f} seconds)")
    print(f"  Feature shape: {features.shape}")
    print(f"  Feature dimensions: {features.shape[-1]}")
    print(f"  Temporal resolution: {features.shape[1]} frames")
    
    # Convert to numpy for analysis
    features_np = np.array(features)
    
    # Example 1: Get utterance-level representation
    print("\n1. Utterance-level representation (mean pooling):")
    utterance_embedding = features_np.mean(axis=1)
    print(f"   Shape: {utterance_embedding.shape}")
    print(f"   Norm: {np.linalg.norm(utterance_embedding):.4f}")
    
    # Example 2: Frame-level features for alignment
    print("\n2. Frame-level features:")
    print(f"   Features per frame: {features.shape[-1]}")
    print(f"   Total frames: {features.shape[1]}")
    print(f"   Frame rate: ~{features.shape[1] / (len(audio_sample)/16000):.1f} frames/second")
    
    # Example 3: Use specific layers (if available)
    if hasattr(outputs, 'hidden_states') and outputs.hidden_states:
        print(f"\n3. Layer-wise features available: {len(outputs.hidden_states)} layers")
        # Use features from middle layer
        middle_layer = len(outputs.hidden_states) // 2
        middle_features = outputs.hidden_states[middle_layer]
        print(f"   Middle layer ({middle_layer}) shape: {middle_features.shape}")
    
    return features


def compare_utterances():
    """Compare features from different utterances."""
    
    print("\n" + "="*60)
    print("Comparing utterances using HuBERT features")
    print("="*60)
    
    # Load model
    model_id = "mzbac/hubert-base-ls960"
    model, config = load_model(model_id)
    model.eval()
    
    processor = HubertProcessor.from_pretrained(model_id)
    
    # Load multiple utterances
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    
    embeddings = []
    for i in range(3):
        audio = ds[i]["audio"]["array"]
        inputs = processor(audio)
        input_values = inputs["input_values"]
        
        # Extract features
        features = model(input_values).last_hidden_state
        
        # Mean pool to get utterance embedding
        embedding = mx.mean(features, axis=1)
        embeddings.append(embedding)
        
        print(f"\nUtterance {i+1}:")
        print(f"  Text: '{ds[i]['text']}'")
        print(f"  Duration: {len(audio)/16000:.2f}s")
    
    # Compute similarities
    print("\nCosine similarities between utterances:")
    embeddings_stacked = mx.concatenate(embeddings, axis=0)
    
    # Normalize
    norms = mx.sqrt(mx.sum(embeddings_stacked * embeddings_stacked, axis=1, keepdims=True))
    normalized = embeddings_stacked / norms
    
    # Compute similarity matrix
    similarity = normalized @ normalized.T
    similarity_np = np.array(similarity)
    
    for i in range(3):
        for j in range(i+1, 3):
            print(f"  Utterance {i+1} vs {j+1}: {similarity_np[i, j]:.4f}")


def temporal_analysis():
    """Analyze temporal properties of features."""
    
    print("\n" + "="*60)
    print("Temporal analysis of HuBERT features")
    print("="*60)
    
    # Load model
    model_id = "mzbac/hubert-base-ls960"
    model, config = load_model(model_id)
    model.eval()
    
    processor = HubertProcessor()
    
    # Create audio of different lengths
    sample_rates = 16000
    durations = [0.5, 1.0, 2.0]  # seconds
    
    print("\nFeature extraction at different durations:")
    for duration in durations:
        num_samples = int(duration * sample_rates)
        audio = np.random.randn(num_samples).astype(np.float32)
        
        inputs = processor(audio)
        input_values = inputs["input_values"]
        
        features = model(input_values).last_hidden_state
        
        print(f"\nDuration: {duration}s ({num_samples} samples)")
        print(f"  Output shape: {features.shape}")
        print(f"  Frames: {features.shape[1]}")
        print(f"  Frame rate: {features.shape[1]/duration:.1f} Hz")
        print(f"  Stride: ~{num_samples/features.shape[1]:.1f} samples/frame")


if __name__ == "__main__":
    # Basic feature extraction
    features = main()
    
    # Compare utterances
    compare_utterances()
    
    # Temporal analysis
    temporal_analysis()
    
    print("\n✅ Base model example completed successfully!")