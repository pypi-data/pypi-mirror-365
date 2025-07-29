"""
Batch Processing Example for MLX-HuBERT

This example demonstrates how to efficiently process multiple audio samples
in parallel using MLX-HuBERT, including handling variable-length inputs.
"""

import mlx.core as mx
import numpy as np
from datasets import load_dataset
from mlx_hubert import load_model, HubertProcessor
import time


def process_single_vs_batch():
    """Compare single vs batch processing performance."""
    print("=== Single vs Batch Processing Comparison ===\n")
    
    # Load model
    MODEL_ID = "mzbac/hubert-base-ls960"
    model, config = load_model(MODEL_ID)
    processor = HubertProcessor.from_pretrained(MODEL_ID)
    model.eval()
    
    # Load dataset
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    
    # Get 8 audio samples
    audio_samples = [ds[i]["audio"]["array"] for i in range(8)]
    
    # Single processing
    print("1. Processing samples individually:")
    start_time = time.time()
    single_results = []
    
    for i, audio in enumerate(audio_samples):
        inputs = processor(audio)
        input_values = inputs["input_values"]
        outputs = model(input_values)
        single_results.append(outputs.last_hidden_state)
        print(f"   Sample {i+1}: shape {outputs.last_hidden_state.shape}")
    
    single_time = time.time() - start_time
    print(f"   Total time: {single_time:.3f}s\n")
    
    # Batch processing
    print("2. Processing samples as a batch:")
    start_time = time.time()
    
    # Process all at once with padding
    inputs = processor(
        audio_samples, 
        padding=True, 
    )
    
    input_values = inputs["input_values"]
    attention_mask = inputs["attention_mask"]
    
    # Single forward pass
    outputs = model(input_values, attention_mask=attention_mask)
    batch_time = time.time() - start_time
    
    print(f"   Batch shape: {outputs.last_hidden_state.shape}")
    print(f"   Total time: {batch_time:.3f}s")
    print(f"   Speedup: {single_time/batch_time:.2f}x\n")


def handle_variable_lengths():
    """Demonstrate handling audio samples of different lengths."""
    print("=== Variable Length Audio Processing ===\n")
    
    # Load model
    MODEL_ID = "mzbac/hubert-base-ls960"
    model, config = load_model(MODEL_ID)
    processor = HubertProcessor.from_pretrained(MODEL_ID)
    model.eval()
    
    # Create audio samples of different lengths
    audio_samples = [
        np.random.randn(8000).astype(np.float32),   # 0.5 seconds
        np.random.randn(16000).astype(np.float32),  # 1.0 seconds
        np.random.randn(24000).astype(np.float32),  # 1.5 seconds
        np.random.randn(32000).astype(np.float32),  # 2.0 seconds
    ]
    
    print("Audio lengths:")
    for i, audio in enumerate(audio_samples):
        print(f"  Sample {i+1}: {len(audio)} samples ({len(audio)/16000:.1f}s)")
    
    # Process with padding and attention mask
    inputs = processor(
        audio_samples,
        padding=True,
    )
    
    input_values = inputs["input_values"]
    attention_mask = inputs["attention_mask"]
    
    print(f"\nPadded input shape: {input_values.shape}")
    print(f"Attention mask shape: {attention_mask.shape}")
    
    # Forward pass
    outputs = model(input_values, attention_mask=attention_mask)
    
    # Extract valid frames for each sample
    print(f"\nOutput shape (with padding): {outputs.last_hidden_state.shape}")
    
    # Calculate actual frame counts
    print("\nValid frames per sample:")
    for i in range(len(audio_samples)):
        # Get feature-level attention mask
        feature_mask = model._get_feature_vector_attention_mask(
            outputs.last_hidden_state.shape[1],
            attention_mask[i:i+1]
        )
        valid_frames = int(feature_mask.sum())
        print(f"  Sample {i+1}: {valid_frames} frames")


def extract_valid_features(features, attention_mask, model):
    """Extract only valid (non-padded) features from batch output."""
    batch_size = features.shape[0]
    valid_features = []
    
    for i in range(batch_size):
        # Get feature-level mask for this sample
        feature_mask = model._get_feature_vector_attention_mask(
            features.shape[1],
            attention_mask[i:i+1]
        )
        valid_length = int(feature_mask.sum())
        
        # Extract valid features
        valid_feat = features[i, :valid_length, :]
        valid_features.append(valid_feat)
    
    return valid_features


def batch_transcription_example():
    """Demonstrate batch transcription with CTC model."""
    print("=== Batch Transcription Example ===\n")
    
    # Load CTC model for transcription
    MODEL_ID = "mzbac/hubert-large-ls960-ft"
    model, config = load_model(MODEL_ID)
    processor = HubertProcessor.from_pretrained(MODEL_ID)
    model.eval()
    
    # Load dataset
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    
    # Get 4 samples
    batch_size = 4
    audio_samples = []
    texts = []
    
    for i in range(batch_size):
        audio_samples.append(ds[i]["audio"]["array"])
        texts.append(ds[i]["text"])
    
    print("Reference texts:")
    for i, text in enumerate(texts):
        print(f"  {i+1}: {text}")
    
    # Batch processing
    inputs = processor(
        audio_samples,
        padding=True,
    )
    
    input_values = inputs["input_values"]
    attention_mask = inputs["attention_mask"]
    
    # Get predictions
    outputs = model(input_values, attention_mask=attention_mask)
    predicted_ids = mx.argmax(outputs.logits, axis=-1)
    
    # Decode each sample
    print("\nTranscriptions:")
    valid_features = extract_valid_features(outputs.logits, attention_mask, model.hubert)
    
    for i in range(batch_size):
        # Get valid predictions for this sample
        valid_length = valid_features[i].shape[0]
        valid_ids = predicted_ids[i, :valid_length]
        
        # Decode
        transcription = processor.decode(np.array(valid_ids))
        print(f"  {i+1}: {transcription}")


def dynamic_batching_example():
    """Show how to group similar-length audios for efficiency."""
    print("=== Dynamic Batching by Length ===\n")
    
    # Create samples of various lengths
    audio_lengths = [
        8000, 9000, 8500,      # Short (~0.5s)
        16000, 17000, 15000,   # Medium (~1s)
        32000, 30000, 33000,   # Long (~2s)
    ]
    
    audio_samples = [
        (i, np.random.randn(length).astype(np.float32)) 
        for i, length in enumerate(audio_lengths)
    ]
    
    # Sort by length
    sorted_samples = sorted(audio_samples, key=lambda x: len(x[1]))
    
    # Group into batches of similar length
    batch_size = 3
    batches = []
    
    for i in range(0, len(sorted_samples), batch_size):
        batch = sorted_samples[i:i+batch_size]
        batches.append(batch)
    
    # Show batching result
    print("Batches grouped by length:")
    for i, batch in enumerate(batches):
        lengths = [len(audio) for _, audio in batch]
        indices = [idx for idx, _ in batch]
        print(f"  Batch {i+1}: samples {indices}, lengths {lengths}")
        print(f"    Padding ratio: {max(lengths)/np.mean(lengths):.2f}")
    
    print("\nThis minimizes padding and improves efficiency!")


def memory_efficient_large_batch():
    """Process large batches in chunks to manage memory."""
    print("=== Memory-Efficient Large Batch Processing ===\n")
    
    # Load model
    MODEL_ID = "mzbac/hubert-base-ls960"
    model, config = load_model(MODEL_ID)
    processor = HubertProcessor.from_pretrained(MODEL_ID)
    model.eval()
    
    # Simulate 100 audio samples
    num_samples = 100
    print(f"Processing {num_samples} audio samples...")
    
    # Process in chunks
    chunk_size = 16
    all_features = []
    
    start_time = time.time()
    
    for chunk_start in range(0, num_samples, chunk_size):
        chunk_end = min(chunk_start + chunk_size, num_samples)
        chunk_size_actual = chunk_end - chunk_start
        
        # Generate chunk of audio (in practice, load from files)
        audio_chunk = [
            np.random.randn(16000).astype(np.float32) 
            for _ in range(chunk_size_actual)
        ]
        
        # Process chunk
        inputs = processor(
            audio_chunk,
            padding=True,
            )
        
        input_values = inputs["input_values"]
        attention_mask = inputs["attention_mask"]
        
        # Get features
        outputs = model(input_values, attention_mask=attention_mask)
        
        # Extract valid features
        valid_features = extract_valid_features(
            outputs.last_hidden_state, 
            attention_mask, 
            model
        )
        all_features.extend(valid_features)
        
        print(f"  Processed chunk {chunk_start//chunk_size + 1}/"
              f"{(num_samples + chunk_size - 1)//chunk_size}")
    
    total_time = time.time() - start_time
    print(f"\nTotal processing time: {total_time:.2f}s")
    print(f"Average per sample: {total_time/num_samples*1000:.1f}ms")
    print(f"Extracted {len(all_features)} feature tensors")


if __name__ == "__main__":
    # Run all examples
    process_single_vs_batch()
    print("\n" + "="*50 + "\n")
    
    handle_variable_lengths()
    print("\n" + "="*50 + "\n")
    
    batch_transcription_example()
    print("\n" + "="*50 + "\n")
    
    dynamic_batching_example()
    print("\n" + "="*50 + "\n")
    
    memory_efficient_large_batch()