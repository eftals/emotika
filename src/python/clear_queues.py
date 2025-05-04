#!/usr/bin/env python3
"""
Script to clear Redis queues for Emotika.
"""

import os
import redis
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_queues():
    """Clear all Emotika queues in Redis."""
    try:
        # Redis connection
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        
        # Queue names
        queues = [
            "emotika_incoming",
            "emotika_response",
            "llama_queue",
            "llama_response_queue"
        ]
        
        # Clear each queue
        for queue in queues:
            count = redis_client.delete(queue)
            logger.info(f"Cleared queue '{queue}': {count} items removed")
            
        # Clear all conversation sessions
        pattern = "conversation:*"
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
            logger.info(f"Cleared conversation session: {key}")
            
        # Clear all response keys
        pattern = "response:*"
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
            logger.info(f"Cleared response: {key}")
            
        logger.info("All queues and sessions cleared successfully")
        
    except Exception as e:
        logger.error(f"Error clearing queues: {e}")

if __name__ == "__main__":
    clear_queues() 