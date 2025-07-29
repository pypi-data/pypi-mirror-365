"""Simple transcription example using MLX-HuBERT.

This is the MLX equivalent of transformer_hubert_example.py
"""

import time
import mlx.core as mx
import numpy as np
from mlx_hubert import load_model, HubertProcessor
from datasets import load_dataset

# You can use either HuggingFace model ID or local path
MODEL_ID = "mzbac/hubert-large-ls960-ft"  # HuggingFace model

# Load model and processor
model, config = load_model(MODEL_ID)
processor = HubertProcessor.from_pretrained(MODEL_ID)
model.eval()

# Load dataset
ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
audio = ds[0]["audio"]["array"]
audio_duration = len(audio) / 16000  # seconds

# Track transcription generation time
start_time = time.time()

# Process audio
inputs = processor(audio)
input_values = inputs["input_values"]

# Get model output
logits = model(input_values).logits
predicted_ids = mx.argmax(logits, axis=-1)

# Decode
transcription = processor.decode(np.array(predicted_ids[0]))

# Measure total time
total_time = time.time() - start_time

print(f"Audio duration: {audio_duration:.2f}s")
print(f"Transcription time: {total_time*1000:.1f}ms")
print(f"Real-time factor: {audio_duration/total_time:.1f}x")
print(f"\nTranscription: {transcription}")