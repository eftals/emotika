import os
import time
import platform
from pathlib import Path
from huggingface_hub import login, HfApi, snapshot_download
from llama_cpp import Llama

class EmotikaModel:
    def __init__(self):
        # Authenticate with Hugging Face
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            login(hf_token)
            try:
                api = HfApi()
                user = api.whoami()
                print(f"Logged in to Hugging Face as: {user['name']}")
            except Exception as e:
                print(f"Error authenticating with Hugging Face: {e}")
        else:
            print("Warning: HF_TOKEN not set in environment variables")

        self.model = self.load_model()

    def load_model(self):
        print("Loading Mistral Llama model...")

        model_id = "TheBloke/Mistral-7B-v0.1-GGUF"
        if os.getenv("MODEL_DIR"):
            mistral_models_path = Path(os.getenv("MODEL_DIR"))
        else:
            if platform.system() == "Windows":
                mistral_models_path = Path("D:/developer/mistral_models/Mistral-7B-v0.1-GGUF")
            else:
                mistral_models_path = Path.home().joinpath('mistral_models', 'Mistral-7B-v0.1-GGUF')

        mistral_models_path.mkdir(parents=True, exist_ok=True)
        print(f"Using model directory: {mistral_models_path}")

        if not any(mistral_models_path.glob("*.gguf")):
            print(f"Downloading model from {model_id} to {mistral_models_path}")
            snapshot_download(
                repo_id=model_id,
                allow_patterns=["mistral-7b-v0.1.Q4_K_M.gguf"],
                cache_dir="./hf_models",
                local_dir=mistral_models_path,
                local_dir_use_symlinks=False
            )

        model_file = next(mistral_models_path.glob("*.gguf"), None)
        if not model_file:
            raise FileNotFoundError("No GGUF model file found in the specified directory")

        print(f"Loading model from {model_file}")

        n_threads = int(os.getenv("N_THREADS", "4"))
        n_gpu_layers = int(os.getenv("N_GPU_LAYERS", "32"))

        print(f"Using {n_threads} CPU threads and {n_gpu_layers} GPU layers")

        start_time = time.time()
        model = Llama(
            model_path=str(model_file),
            n_ctx=2048,
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers
        )
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f} seconds")
        return model

    def generate(self, *args, **kwargs):
        return self.model(*args, **kwargs) 