import json
import redis.asyncio as redis
from typing import Any, Optional
from src.core.config import get_settings
from .protocol import CachePort

class RedisCacheAdapter(CachePort):
    """Redis-адаптер для кеширования"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or get_settings().redis_url
        self.default_ttl = get_settings().redis_cache_ttl
        self._client: Optional[redis.Redis] = None
    
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить и десериализовать JSON"""
        data = await self.client.get(key)
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Сериализовать и сохранить с TTL"""
        ttl = ttl or self.default_ttl
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await self.client.setex(key, ttl, serialized)
    
    async def delete(self, key: str) -> None:
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0
    
    async def close(self) -> None:
        if self._client:
            await self._client.close()