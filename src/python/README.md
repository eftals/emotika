# Mistral LLM Runner

This project provides a simple way to run the Mistral-7B model locally using either ctransformers or llama-cpp-python.

## Requirements

- Python 3.8+
- pip
- Hugging Face account and token
- (Optional) NVIDIA GPU with CUDA support

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>/src/python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running on Linux

### Using the Shell Script (Recommended)

1. Make the script executable:
   ```bash
   chmod +x run_mistral.sh
   ```

2. Set your Hugging Face token (optional, the script will prompt if not set):
   ```bash
   export HF_TOKEN=your_huggingface_token_here
   ```

3. Run the script:
   ```bash
   ./run_mistral.sh
   ```

### Manual Setup

1. Set environment variables:
   ```bash
   export HF_TOKEN=your_huggingface_token_here
   export MODEL_DIR=$HOME/mistral_models/Mistral-7B-v0.1-GGUF  # Optional
   export N_THREADS=4  # Optional, default is 4
   export N_GPU_LAYERS=32  # Optional, default is 32 (0 for CPU-only)
   ```

2. Run the Python script:
   ```bash
   python3 test_mistral_llama.py
   ```

## Configuration Options

- `HF_TOKEN`: Your Hugging Face API token
- `MODEL_DIR`: Directory to store the model (default: `$HOME/mistral_models/Mistral-7B-v0.1-GGUF`)
- `N_THREADS`: Number of CPU threads to use (default: 4)
- `N_GPU_LAYERS`: Number of layers to offload to GPU (default: 32, set to 0 for CPU-only)

## Troubleshooting

### GPU Not Being Used

If the model is not using your GPU:

1. Make sure you have the CUDA-enabled version of llama-cpp-python:
   ```bash
   pip uninstall llama-cpp-python
   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/cu121
   ```

2. Check that your NVIDIA drivers are installed:
   ```bash
   nvidia-smi
   ```

3. Set `N_GPU_LAYERS` to a value greater than 0:
   ```bash
   export N_GPU_LAYERS=32
   ```

### Missing Dependencies

If you encounter missing dependencies:

```bash
pip install -r requirements.txt
```

## License

[Your License Here] 