import os
import json
import time
import redis
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from threading import Thread
from enum import Enum
from huggingface_hub import login

class MessageStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

class ChatWorker:
    def __init__(self):
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # Authenticate with Hugging Face
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            login(hf_token)
        else:
            print("Warning: HF_TOKEN not set in environment variables")
        
        # Load Mistral model and tokenizer
        print("Loading Mistral 7B model...")
        self.model_name = "mistralai/Mistral-7B-v0.1"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("Model loaded successfully!")

    def update_message_status(self, message_key: str, status: MessageStatus, error_message: str = None):
        try:
            message_data = self.redis_client.get(message_key)
            if message_data:
                message = json.loads(message_data)
                message["status"] = status
                if error_message:
                    message["errorMessage"] = error_message
                self.redis_client.set(message_key, json.dumps(message))
        except Exception as e:
            print(f"Error updating message status: {str(e)}")

    def generate_response(self, user_message: str) -> str:
        # Prepare the prompt
        prompt = f"<s>[INST] {user_message} [/INST]"
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=512,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )
        
        # Decode and clean up the response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.replace(prompt, "").strip()
        
        return response

    def process_message(self, message_id: str):
        message_key = f"chat:{message_id}"
        try:
            # Get the message from Redis
            message_data = self.redis_client.get(message_key)
            
            if not message_data:
                print(f"Message {message_id} not found in Redis")
                return
            
            # Parse the message
            message = json.loads(message_data)
            
            # Skip if already processed
            if message.get("status") == MessageStatus.COMPLETED:
                return
            
            # Update status to processing
            self.update_message_status(message_key, MessageStatus.PROCESSING)
            
            # Generate AI response
            print(f"Processing message {message_id}...")
            response = self.generate_response(message["userMessage"])
            
            # Update the message with the response and completed status
            message["response"] = response
            message["status"] = MessageStatus.COMPLETED
            self.redis_client.set(message_key, json.dumps(message))
            
            print(f"Processed message {message_id}")
            
        except Exception as e:
            error_message = str(e)
            print(f"Error processing message {message_id}: {error_message}")
            self.update_message_status(message_key, MessageStatus.FAILED, error_message)

    def start(self):
        print("Starting chat worker...")
        while True:
            try:
                # Scan for unprocessed messages
                for key in self.redis_client.scan_iter("chat:*"):
                    message_data = self.redis_client.get(key)
                    if message_data:
                        message = json.loads(message_data)
                        if message.get("status") == MessageStatus.PENDING:
                            # Process in a separate thread
                            Thread(target=self.process_message, args=(message["id"],)).start()
                
                time.sleep(1)  # Avoid busy waiting
                
            except Exception as e:
                print(f"Error in worker loop: {str(e)}")
                time.sleep(5)  # Wait longer on error

if __name__ == "__main__":
    worker = ChatWorker()
    worker.start() 