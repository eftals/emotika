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
from emotika_model import EmotikaModel

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

        self.session = "<|system|>You are a helpful assistant named Emotika Lois, with god level intelligence.Respond as humanly, as naturally as possible. Never mention you are an AI or a bot. Never use emojis.<|end|>"
        
        # Initialize EmotikaModel
        self.emotika_model = EmotikaModel()
        
        # Queue names
        self.input_queue = os.getenv("REDIS_QUEUE_NAME", "llama_queue")
        self.response_queue = os.getenv("REDIS_RESPONSE_QUEUE", "llama_response_queue")
        
        print(f"LlamaQueueWorker initialized. Listening on queue: {self.input_queue}")
        print(f"Writing responses to queue: {self.response_queue}")

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
        response = self.emotika_model.generate(
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
    
    def process_message(self, message_data: str):
        """Process a single message from the queue."""
        try:
            # Parse the message from the queue
            message = json.loads(message_data)
            message_id = message.get("id")
            
            if not message_id:
                print("Message missing ID")
                return
            
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
            print(f"Error processing message: {error_message}")
            
            # Store error in Redis if we have a message ID
            if message_id:
                error_response = {
                    "id": message_id,
                    "userMessage": message.get("userMessage", ""),
                    "error": error_message
                }
                
                response_key = f"response:{message_id}"
                self.redis_client.set(response_key, json.dumps(error_response))
                self.redis_client.rpush(self.response_queue, json.dumps(error_response))
    
    def run(self):
        print("Starting LlamaQueueWorker...")
        while True:
            try:
                # Get message from queue
                message = self.redis_client.blpop(self.input_queue, timeout=1)
                if message:
                    _, message_data = message
                    self.process_message(message_data)
                time.sleep(0.1)  # Small delay to prevent CPU overuse
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)  # Longer delay on error

if __name__ == "__main__":
    worker = LlamaQueueWorker()
    worker.run() 