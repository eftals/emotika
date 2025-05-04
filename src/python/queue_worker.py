#!/usr/bin/env python3
"""
Kobolt Queue Worker for Emotika
Processes messages from Redis queue using the KoboldCpp API.
"""

import os
import json
import time
import redis
import logging
from emotika_kobolt import EmotikaKobolt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KoboltQueueWorker:
    def __init__(self):
        # Redis connection
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        
        # Initialize EmotikaKobolt API
        kobolt_url = os.getenv("KOBOLT_API_URL", "http://localhost:5001")
        self.kobolt_api = EmotikaKobolt(base_url=kobolt_url)
        
        # Queue names
        self.input_queue = "emotika_incoming"
        self.response_queue = "emotika_response"
        self.session_expiry = 12 * 60 * 60  # 12 hours

    def get_conversation_session(self, session_token: str) -> str:
        """Get or create a conversation session from Redis."""
        session_key = f"conversation:{session_token}"
        session = self.redis_client.get(session_key)
        
        if not session:
            session =""
            self.redis_client.setex(session_key, self.session_expiry, session)
        else:
            self.redis_client.expire(session_key, self.session_expiry)
            
        return session

    def update_conversation_session(self, session_token: str, updated_session: str):
        """Update the conversation session in Redis with pruning."""
        pruned_conversation = self.kobolt_api.prune_conversation(updated_session)
        session_key = f"conversation:{session_token}"
        self.redis_client.setex(session_key, self.session_expiry, pruned_conversation)

    def generate_response(self, user_message: str, session_token: str) -> str:
        """Generate a response using the KoboldCpp API."""
        conversation = self.get_conversation_session(session_token)
        updated_conversation, response_text = self.kobolt_api.generate_response(user_message, conversation)
        self.update_conversation_session(session_token, updated_conversation)
        return response_text
    
    def process_message(self, message_data: str):
        """Process a single message from the queue."""
        try:
            message = json.loads(message_data)
            message_id = message.get("id")
            session_token = message.get("sessionToken")
            
            if not message_id:
                return
                
            response = self.generate_response(message["userMessage"], session_token)
            response_message = {
                "id": message_id,
                "userMessage": message["userMessage"],
                "response": response
            }
            
            if session_token:
                response_message["sessionToken"] = session_token
            
            # Store response in Redis
            response_key = f"response:{message_id}"
            self.redis_client.set(response_key, json.dumps(response_message))
            self.redis_client.rpush(self.response_queue, json.dumps(response_message))
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            if message_id:
                error_response = {
                    "id": message_id,
                    "userMessage": message.get("userMessage", ""),
                    "error": str(e)
                }
                if session_token:
                    error_response["sessionToken"] = session_token
                self.redis_client.rpush(self.response_queue, json.dumps(error_response))
    
    def run(self):
        """Main worker loop."""
        logger.info("Starting KoboltQueueWorker...")
        while True:
            try:
                message = self.redis_client.blpop(self.input_queue, timeout=1)
                if message:
                    _, message_data = message
                    self.process_message(message_data)
                time.sleep(0.1)
            except redis.ConnectionError:
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)

if __name__ == "__main__":
    worker = KoboltQueueWorker()
    worker.run() 