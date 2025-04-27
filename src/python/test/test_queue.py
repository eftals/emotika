#!/usr/bin/env python3
"""
Test script for writing messages to the Redis queue and reading responses.
This script adds test messages to the Redis queue and waits for responses from the LlamaQueueWorker.
"""

import os
import json
import redis
import uuid
import time
from datetime import datetime

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Queue names
input_queue = os.getenv("REDIS_QUEUE_NAME", "llama_queue")
response_queue = os.getenv("REDIS_RESPONSE_QUEUE", "llama_response_queue")

def clear_queues():
    """Clear all queues and related keys"""
    print("Clearing Redis queues and keys...")
    
    # Clear queues
    redis_client.delete(input_queue)
    redis_client.delete(response_queue)
    
    # Clear all chat and response keys
    for key in redis_client.keys("chat:*"):
        redis_client.delete(key)
    for key in redis_client.keys("response:*"):
        redis_client.delete(key)
    
    print("Queues and keys cleared successfully!")

def add_message_to_queue(user_message):
    """Add a message to the Redis queue"""
    message_id = str(uuid.uuid4())
    message = {
        "id": message_id,
        "userMessage": user_message
    }
    
    # Add to queue
    redis_client.rpush(input_queue, json.dumps(message))
    
    # Store message data separately for retrieval
    redis_client.set(f"chat:{message_id}", json.dumps(message))
    
    print(f"Added message to queue: {message_id}")
    return message_id

def wait_for_response(message_id, timeout=60):
    """Wait for a response for a specific message ID"""
    print(f"\nWaiting for response to message {message_id}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check response queue
        response_data = redis_client.blpop(response_queue, timeout=1)
        if response_data:
            _, response_json = response_data
            response = json.loads(response_json)
            
            if response["id"] == message_id:
                print("\nResponse received:")
                print("-" * 50)
                print(f"Message: {response['userMessage']}")
                print(f"Response: {response['response']}")
                print("-" * 50)
                return response
        
        # Also check direct response key
        response_key = f"response:{message_id}"
        response_data = redis_client.get(response_key)
        if response_data:
            response = json.loads(response_data)
            print("\nResponse received (from direct key):")
            print("-" * 50)
            print(f"Message: {response['userMessage']}")
            if 'response' in response:
                print(f"Response: {response['response']}")
            else:
                print(f"Error: {response['error']}")
            print("-" * 50)
            return response
        
        time.sleep(1)
    
    print(f"Timeout waiting for response to message {message_id}")
    return None

def main():
    """Main function to add test messages to the queue and wait for responses"""
    # Clear queues before starting
    clear_queues()
    
    print("Adding test messages to Redis queue...")
    
    # Test messages
    test_messages = [
        "Hello, how are you?",
        "Tell me about artificial intelligence",
        "What is machine learning?",
        "Explain neural networks in simple terms",
        "What are the applications of natural language processing?"
    ]
    
    # Add each message to the queue and wait for response
    for message in test_messages:
        message_id = add_message_to_queue(message)
        print(f"Message: '{message[:30]}...' -> ID: {message_id}")
        
        # Wait for response before sending next message
        response = wait_for_response(message_id)
        if response:
            print(f"Response received for message {message_id}")
        else:
            print(f"No response received for message {message_id}")
        
        time.sleep(1)  # Small delay between messages
    
    print("\nAll test messages processed.")

if __name__ == "__main__":
    try:
        # Test Redis connection
        redis_client.ping()
        print("Connected to Redis successfully.")
        main()
    except redis.ConnectionError:
        print("Error: Could not connect to Redis. Make sure Redis is running.")
    except Exception as e:
        print(f"Error: {str(e)}") 