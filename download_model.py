"""
Script to download Phi-3-mini-4k-instruct-q4.gguf model
"""
import os

# Create directory
model_dir = os.path.expanduser("~/.studyai_models")
os.makedirs(model_dir, exist_ok=True)

# Model info
model_name = "Phi-3-mini-4k-instruct-q4.gguf"
model_path = os.path.join(model_dir, model_name)

print(f"Model should be placed at: {model_path}")
print("\nTo download the model:")
print("1. Visit: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf")
print(f"2. Download: {model_name}")
print(f"3. Place it in: {model_dir}")
print("\nOr use direct link:")
print("https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf")
print("\nNote: Phi-3 is smaller (3.8GB) and faster than Llama-3-8B!")
