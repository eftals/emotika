from llama_cpp import Llama
import os
import time
import platform
from pathlib import Path
from huggingface_hub import login, HfApi, snapshot_download

# Set environment variable for verbose logging
os.environ["LLAMA_CPP_LOG_LEVEL"] = "INFO"

# Hugging Face authentication

if hf_token:
    login(hf_token)
else:
    print("ERROR: HF_TOKEN not set in environment variables")
    print("Please set it with: export HF_TOKEN=your_token_here")
    exit(1)

api = HfApi()
try:
    user = api.whoami()
    print("Logged in:", user['name'])
except Exception as e:
    print("Not logged in or error:", e)

# Define model path and create directory
model_id = "TheBloke/Mistral-7B-v0.1-GGUF"

# Use environment variable if set, otherwise use default paths
if os.getenv("MODEL_DIR"):
    mistral_models_path = Path(os.getenv("MODEL_DIR"))
else:
    # Default paths based on OS
    if platform.system() == "Windows":
        mistral_models_path = Path("D:/developer/mistral_models/Mistral-7B-v0.1-GGUF")
    else:
        mistral_models_path = Path.home().joinpath('mistral_models', 'Mistral-7B-v0.1-GGUF')

mistral_models_path.mkdir(parents=True, exist_ok=True)
print(f"Using model directory: {mistral_models_path}")

# Download the model
print(f"Downloading model from {model_id} to {mistral_models_path}")
snapshot_download(
    repo_id="TheBloke/Mistral-7B-v0.1-GGUF",
    allow_patterns=["mistral-7b-v0.1.Q4_K_M.gguf"],  # 🎯 Only this file
    cache_dir="./hf_models",
    local_dir=mistral_models_path,
    local_dir_use_symlinks=False
)

# Find the downloaded model file
model_file = None
for file in mistral_models_path.glob("*.gguf"):
    model_file = file
    break

if not model_file:
    raise FileNotFoundError("No GGUF model file found in the specified directory")

print(f"Loading model from {model_file}")

# Get number of CPU threads from environment or use default
n_threads = int(os.getenv("N_THREADS", "4"))
n_gpu_layers = int(os.getenv("N_GPU_LAYERS", "32"))

print(f"Using {n_threads} CPU threads and {n_gpu_layers} GPU layers")

# Load the model with llama-cpp-python
start_time = time.time()
model = Llama(
    model_path=str(model_file),
    n_ctx=2048,  # Context window
    n_threads=n_threads,  # Number of CPU threads to use
    n_gpu_layers=n_gpu_layers  # Set to 0 for CPU-only, increase for GPU acceleration
)
load_time = time.time() - start_time
print(f"Model loaded in {load_time:.2f} seconds")

# Test the model
prompt = "Explain Machine Learning to me in a nutshell."
print("\nPrompt:", prompt)
print("\nGenerating response...")
start_time = time.time()
response = model(
    prompt,
    max_tokens=100,
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    repeat_penalty=1.18,
    stop=["</s>"]
)
generation_time = time.time() - start_time
print(f"Response generated in {generation_time:.2f} seconds")
print("\nResponse:")
print(response["choices"][0]["text"])

# Print total time (excluding download)
total_time = load_time + generation_time
print(f"\nTotal time (excluding download): {total_time:.2f} seconds")

