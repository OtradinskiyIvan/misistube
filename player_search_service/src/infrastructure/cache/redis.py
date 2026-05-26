import json
import redis.asyncio as redis
from typing import Any, Optional
from .protocol import CachePort

class RedisCacheAdapter(CachePort):
    def __init__(self, redis_url: str):
        self.client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        data = await self.client.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        await self.client.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str) -> None:
        await self.client.delete(key)