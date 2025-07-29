"""Example of using MLX-HuBERT for speech recognition.

This example demonstrates how to:
1. Load a pretrained HuBERT model
2. Process audio input
3. Generate transcriptions using CTC decoding

Requirements:
    pip install mlx-hubert datasets soundfile
"""

import mlx.core as mx
import numpy as np
from mlx_hubert import HubertForCTC, HubertProcessor, load_model
from datasets import load_dataset

# Model configuration - change this to use different models
MODEL_ID = "mzbac/hubert-large-ls960-ft"


def main():
    """Run speech recognition example."""
    
    # Load pretrained model
    # Replace with your model path or HuggingFace model ID
    print("Loading model...")
    model, config = load_model(MODEL_ID)
    model.eval()  # Set to evaluation mode
    
    # Load processor with correct vocabulary
    processor = HubertProcessor.from_pretrained(MODEL_ID)
    
    # Load example dataset
    print("Loading dataset...")
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    
    # Process first example
    print("Processing audio...")
    audio_sample = ds[0]["audio"]["array"]
    
    # Prepare input
    inputs = processor(audio_sample)
    input_values = inputs["input_values"]
    
    # Generate predictions
    print("Generating transcription...")
    outputs = model(input_values)
    logits = outputs.logits
    
    # Decode predictions
    predicted_ids = mx.argmax(logits, axis=-1)
    transcription = processor.decode(np.array(predicted_ids[0]))
    
    print(f"\nTranscription: {transcription}")
    # Expected output: "A MAN SAID TO THE UNIVERSE SIR I EXIST"
    
    # Process multiple examples
    print("\nProcessing multiple examples:")
    for i in range(min(3, len(ds))):
        audio_sample = ds[i]["audio"]["array"]
        inputs = processor(audio_sample)
        input_values = inputs["input_values"]
        
        outputs = model(input_values)
        predicted_ids = mx.argmax(outputs.logits, axis=-1)
        transcription = processor.decode(np.array(predicted_ids[0]))
        
        print(f"Example {i+1}: {transcription}")


def advanced_example():
    """Advanced example with batch processing."""
    
    # Load model
    model, config = load_model(
        MODEL_ID,
        from_pretrained=True
    )
    model.eval()
    
    # Load processor with model's vocabulary
    processor = HubertProcessor.from_pretrained(MODEL_ID)
    
    # Load dataset
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    
    # Batch processing
    batch_size = 2
    audio_samples = [ds[i]["audio"]["array"] for i in range(batch_size)]
    
    # Process batch
    inputs = processor(audio_samples, padding=True)
    input_values = inputs["input_values"]
    
    # Generate predictions
    outputs = model(input_values)
    predicted_ids = mx.argmax(outputs.logits, axis=-1)
    
    # Decode batch
    transcriptions = processor.batch_decode(np.array(predicted_ids))
    
    print("\nBatch processing results:")
    for i, transcription in enumerate(transcriptions):
        print(f"Example {i+1}: {transcription}")


def streaming_example():
    """Example of processing audio in chunks (pseudo-streaming)."""
    
    model, config = load_model(
        MODEL_ID,
        from_pretrained=True
    )
    model.eval()
    
    processor = HubertProcessor.from_pretrained(MODEL_ID)
    
    # Load a longer audio sample
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    audio_sample = ds[0]["audio"]["array"]
    
    # Process in chunks (simplified example)
    chunk_size = 16000  # 1 second chunks at 16kHz
    overlap = 3200      # 0.2 seconds overlap
    
    chunks = []
    for i in range(0, len(audio_sample) - chunk_size + 1, chunk_size - overlap):
        chunk = audio_sample[i:i + chunk_size]
        chunks.append(chunk)
    
    # Process each chunk
    chunk_transcriptions = []
    for i, chunk in enumerate(chunks):
        inputs = processor(chunk)
        input_values = inputs["input_values"]
        
        outputs = model(input_values)
        predicted_ids = mx.argmax(outputs.logits, axis=-1)
        transcription = processor.decode(np.array(predicted_ids[0]))
        
        chunk_transcriptions.append(transcription)
        print(f"Chunk {i+1}: {transcription}")
    
    # Simple concatenation (in practice, you'd want smarter merging)
    full_transcription = " ".join(chunk_transcriptions)
    print(f"\nFull transcription: {full_transcription}")


if __name__ == "__main__":
    print("=== Basic Example ===")
    main()
    
    print("\n=== Advanced Example ===")
    advanced_example()
    
    print("\n=== Streaming Example ===")
    streaming_example()