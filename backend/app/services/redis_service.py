import redis.asyncio as redis
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.stream_name = "pdf_processing_stream"
        self.consumer_group = "pdf_consumers"
        self.consumer_name = "pdf_consumer_1"
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
            
            await self.redis_client.ping()
            logger.info("Redis connected")
            
            # Create consumer group
            try:
                await self.redis_client.xgroup_create(
                    self.stream_name, 
                    self.consumer_group, 
                    id="0", 
                    mkstream=True
                )
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise e
                    
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise e
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def ping(self):
        """Test Redis connection"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        return await self.redis_client.ping()
    
    async def add_to_stream(self, processing_id: str, data: Dict[str, Any]):
        """Add message to Redis stream"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        
        try:
            message_data = {
                "processing_id": processing_id,
                "data": json.dumps(data)
            }
            
            message_id = await self.redis_client.xadd(self.stream_name, message_data)
            return message_id
            
        except Exception as e:
            logger.error(f"Stream add failed: {e}")
            raise e
    
    async def read_messages(self, count: int = 1) -> list:
        """Read messages from stream"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        
        try:
            messages = await self.redis_client.xreadgroup(
                self.consumer_group,
                self.consumer_name,
                {self.stream_name: ">"},
                count=count,
                block=1000
            )
            return messages
            
        except Exception as e:
            logger.error(f"Stream read failed: {e}")
            return []
    
    async def acknowledge_message(self, message_id: str):
        """Acknowledge processed message"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        
        try:
            await self.redis_client.xack(
                self.stream_name,
                self.consumer_group,
                message_id
            )
        except Exception as e:
            logger.error(f"Message ack failed: {e}")
    
    async def store_result(self, processing_id: str, data: Dict[str, Any], expire_seconds: int = 86400):
        """Store results in Redis with expiration"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        
        try:
            key = f"result:{processing_id}"
            await self.redis_client.setex(key, expire_seconds, json.dumps(data))
        except Exception as e:
            logger.error(f"Result storage failed: {e}")
            raise e
    
    async def get_result(self, processing_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve results from Redis"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        
        try:
            key = f"result:{processing_id}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Result retrieval failed: {e}")
            return None
    
    async def get_stream_info(self) -> Dict[str, Any]:
        """Get information about the stream"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        
        try:
            info = await self.redis_client.xinfo_stream(self.stream_name)
            return info
        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            return {}
