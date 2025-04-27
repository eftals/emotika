#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Mistral LLM Runner for Linux${NC}"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3 with: sudo apt install python3 python3-pip"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}ERROR: pip3 is not installed${NC}"
    echo "Please install pip3 with: sudo apt install python3-pip"
    exit 1
fi

# Check if HF_TOKEN is set
if [ -z "$HF_TOKEN" ]; then
    echo -e "${YELLOW}WARNING: HF_TOKEN environment variable is not set${NC}"
    echo "Please set it with: export HF_TOKEN=your_token_here"
    echo "Or enter your token now (will not be saved):"
    read -s HF_TOKEN
    export HF_TOKEN
fi

# Create model directory if it doesn't exist
if [ -z "$MODEL_DIR" ]; then
    MODEL_DIR="$HOME/mistral_models/Mistral-7B-v0.1-GGUF"
    echo -e "${YELLOW}Using default model directory: $MODEL_DIR${NC}"
    echo "To use a different directory, set MODEL_DIR environment variable"
else
    echo -e "${GREEN}Using custom model directory: $MODEL_DIR${NC}"
fi

mkdir -p "$MODEL_DIR"

# Set number of threads and GPU layers
N_THREADS=${N_THREADS:-4}
N_GPU_LAYERS=${N_GPU_LAYERS:-32}

echo -e "${GREEN}Configuration:${NC}"
echo "- CPU Threads: $N_THREADS"
echo "- GPU Layers: $N_GPU_LAYERS"
echo "- Model Directory: $MODEL_DIR"

# Install dependencies if needed
echo -e "${GREEN}Checking dependencies...${NC}"
pip3 install -r requirements.txt

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export MODEL_DIR
export N_THREADS
export N_GPU_LAYERS

# Run the Python script
echo -e "${GREEN}Running Mistral model...${NC}"
python3 test_mistral_llama.py

echo -e "${GREEN}Done!${NC}" 