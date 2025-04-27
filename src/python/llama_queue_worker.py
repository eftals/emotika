#!/usr/bin/env python3
"""
Llama Queue Worker for Emotika
This script processes messages from a Redis queue using the Mistral Llama model.
It reads from the input queue and writes responses to a response queue.
"""

import os
import json
import time
import redis
import threading
from pathlib import Path
from huggingface_hub import login, HfApi, snapshot_download
from llama_cpp import Llama
import platform

# Set environment variable for verbose logging
os.environ["LLAMA_CPP_LOG_LEVEL"] = "INFO"

class LlamaQueueWorker:
    def __init__(self):
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )

        self.session = "<|system|>Respond as humanly, as naturally as possible. Never mention you are an AI or a bot. Never use emojis.<|end|>"
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
        
        # Load the Mistral model
        self.load_model()
        
        # Queue names
        self.input_queue = os.getenv("REDIS_QUEUE_NAME", "llama_queue")
        self.response_queue = os.getenv("REDIS_RESPONSE_QUEUE", "llama_response_queue")
        
        print(f"LlamaQueueWorker initialized. Listening on queue: {self.input_queue}")
        print(f"Writing responses to queue: {self.response_queue}")
    
    def load_model(self):
        """Load the Mistral Llama model."""
        print("Loading Mistral Llama model...")
        
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
        
        # Download the model if not already present
        if not any(mistral_models_path.glob("*.gguf")):
            print(f"Downloading model from {model_id} to {mistral_models_path}")
            snapshot_download(
                repo_id="TheBloke/Mistral-7B-v0.1-GGUF",
                allow_patterns=["mistral-7b-v0.1.Q4_K_M.gguf"],  # Only this file
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
        self.model = Llama(
            model_path=str(model_file),
            n_ctx=2048,  # Context window
            n_threads=n_threads,  # Number of CPU threads to use
            n_gpu_layers=n_gpu_layers  # Set to 0 for CPU-only, increase for GPU acceleration
        )
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f} seconds")

    def dynamic_max_tokens(self, user_message: str) -> int:
        """Determine the maximum number of tokens to use based on the user's message."""
        if any(keyword in user_message.lower() for keyword in ["story", "novel", "explain in detail", "long answer", "full description"]):            
            return 100
        elif any(keyword in user_message.lower() for keyword in ["why", "explain", "tell me about", "describe"]):            
            return 100
        else:            
            return 50

    
    def generate_response(self, user_message: str) -> str:
        """Generate a response using the Mistral Llama model."""
        print(f"Generating response for: {user_message[:50]}...")

        
        self.session += "<|start|><|user|>" + user_message + "<|assistant|>"        
        temperature = 0.3
        top_p = 0.85
        top_k = 30
        repeat_penalty = 1.2
        stop=["<|end|>", "<|user|>", "<|system|>", "<|assistant|>", "##"]
        max_tokens = self.dynamic_max_tokens(user_message)
        print(f"Prompt: {self.session}")
        start_time = time.time()
        response = self.model(
            prompt=self.session,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repeat_penalty=repeat_penalty,
            stop=stop
        )                
        generation_time = time.time() - start_time
        
        print(f"Response generated in {generation_time:.2f} seconds")        
        
        self.session += response["choices"][0]["text"] + "<|end|>"        
        return response["choices"][0]["text"]
    
    def process_message(self, message_id: str):
        """Process a single message from the queue."""
        message_key = f"chat:{message_id}"
        try:
            # Get the message from Redis
            message_data = self.redis_client.get(message_key)
            
            if not message_data:
                print(f"Message {message_id} not found in Redis")
                return
            
            # Parse the message
            message = json.loads(message_data)
            
            # Generate AI response
            print(f"Processing message {message_id}...")
            response = self.generate_response(message["userMessage"])
            
            # Create response message
            response_message = {
                "id": message_id,
                "userMessage": message["userMessage"],
                "response": response
            }
            
            # Store response in Redis
            response_key = f"response:{message_id}"
            self.redis_client.set(response_key, json.dumps(response_message))
            
            # Add to response queue
            self.redis_client.rpush(self.response_queue, json.dumps(response_message))
            
            # Print the response
            print(f"Response for message {message_id}")
            
        except Exception as e:
            error_message = str(e)
            print(f"Error processing message {message_id}: {error_message}")
            
            # Store error in Redis
            error_response = {
                "id": message_id,
                "userMessage": message.get("userMessage", ""),
                "error": error_message
            }
            
            response_key = f"response:{message_id}"
            self.redis_client.set(response_key, json.dumps(error_response))
            self.redis_client.rpush(self.response_queue, json.dumps(error_response))
    
    def start(self):
        """Start the worker to process messages from the queue."""
        print("Starting Llama queue worker...")
        
        while True:
            try:
                # Use Redis BLPOP for blocking operation (waits for new messages)
                # This is more efficient than polling with sleep
                # BLPOP returns a tuple of (list_name, value) or None if timeout
                result = self.redis_client.blpop(self.input_queue, timeout=5)
                
                if result:
                    # Unpack the result
                    _, message_data = result
                    
                    try:
                        # Parse the message
                        message = json.loads(message_data)
                        message_id = message.get("id")
                        
                        if message_id:
                            # Process in a separate thread
                            threading.Thread(
                                target=self.process_message,
                                args=(message_id,),
                                daemon=True
                            ).start()
                    
                    except json.JSONDecodeError as e:
                        print(f"Error decoding message: {e}")
                    except Exception as e:
                        print(f"Error processing message: {e}")
            
            except redis.ConnectionError as e:
                print(f"Redis connection error: {e}")
                time.sleep(5)  # Wait before retrying
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    worker = LlamaQueueWorker()
    worker.start() 