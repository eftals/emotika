from ctransformers import AutoModelForCausalLM
import os
import time
from pathlib import Path
from huggingface_hub import login, HfApi, snapshot_download

# Hugging Face authentication

if hf_token:
    login(hf_token)
else:
    print("ERROR: HF_TOKEN not set in environment variables")

api = HfApi()
try:
    user = api.whoami()
    print("Logged in:", user['name'])
except Exception as e:
    print("Not logged in or error:", e)

# Define model path and create directory
model_id = "TheBloke/Mistral-7B-v0.1-GGUF"
mistral_models_path = Path("D:/developer/mistral_models/Mistral-7B-v0.1-GGUF")
mistral_models_path.mkdir(parents=True, exist_ok=True)

# Download the model
print(f"Downloading model from {model_id} to {mistral_models_path}")
snapshot_download(
    repo_id="TheBloke/Mistral-7B-v0.1-GGUF",
    allow_patterns=["mistral-7b-v0.1.Q4_K_M.gguf"],  # 🎯 Only this file
    cache_dir="./hf_models",
    local_dir=mistral_models_path,
    local_dir_use_symlinks=False
)

print(f"Loading model from {mistral_models_path}")
# Load the model with 4-bit quantization
start_time = time.time()
model = AutoModelForCausalLM.from_pretrained(
    str(mistral_models_path),
    model_type="mistral",
    gpu_layers=32,  # Set to 0 for CPU-only, increase for GPU acceleration
    context_length=2048,
)
load_time = time.time() - start_time
print(f"Model loaded in {load_time:.2f} seconds")

# Test the model
prompt = "Explain Machine Learning to me in a nutshell."
print("\nPrompt:", prompt)
print("\nGenerating response...")
start_time = time.time()
response = model(prompt, max_new_tokens=100, temperature=0.7, top_p=0.9, top_k=40, repetition_penalty=1.18, stop=["</s>"])
generation_time = time.time() - start_time
print(f"Response generated in {generation_time:.2f} seconds")
print("\nResponse:")
print(response)

# Print total time (excluding download)
total_time = load_time + generation_time
print(f"\nTotal time (excluding download): {total_time:.2f} seconds") 