import asyncio
import json
import logging
import time
from typing import Any

import redis.asyncio as redis

from src.core.config import get_settings

from .protocol import CachePort

logger = logging.getLogger(__name__)


class RedisCacheAdapter(CachePort):
    """Redis-адаптер с graceful degradation и thread-safe circuit breaker"""

    def __init__(self, redis_url: str | None = None):
        settings = get_settings()
        self.redis_url = redis_url or settings.REDIS_URL
        self.default_ttl = settings.REDIS_CACHE_TTL
        self._client: redis.Redis | None = None

        self._failures = 0
        self._last_failure_time = 0.0
        self._circuit_open = False
        self._failure_threshold = 3
        self._recovery_timeout = 60.0

        self._lock = asyncio.Lock()

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
                retry_on_timeout=False,
            )
        return self._client

    async def _is_circuit_open(self) -> bool:
        """Проверяем, открыт ли circuit breaker (thread-safe)"""
        async with self._lock:
            if not self._circuit_open:
                return False

            if time.time() - self._last_failure_time > self._recovery_timeout:
                logger.info("Redis circuit breaker: attempting recovery")
                self._circuit_open = False
                self._failures = 0
                return False

            return True

    async def _record_failure(self):
        """Записываем неудачу и возможно открываем circuit breaker (thread-safe)"""
        async with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()

            if self._failures >= self._failure_threshold:
                self._circuit_open = True
                logger.warning(
                    "Redis circuit breaker OPEN: %d failures, will retry in %.1fs",
                    self._failures,
                    self._recovery_timeout,
                )

    async def _record_success(self):
        """Записываем успех и сбрасываем счётчик (thread-safe)"""
        async with self._lock:
            if self._failures > 0:
                logger.info("Redis recovered after %d failures", self._failures)
            self._failures = 0
            self._circuit_open = False

    async def get(self, key: str) -> Any | None:
        """Получить и десериализовать JSON"""
        if await self._is_circuit_open():
            return None

        try:
            # 🔹 Вызов Redis БЕЗ лока — не блокируем I/O
            data = await self.client.get(key)
            await self._record_success()

            if data is None:
                return None
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        except redis.RedisError as e:
            logger.warning("Redis GET failed for key=%s: %s", key, e)
            await self._record_failure()
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Сохранить значение с указанием TTL"""
        if await self._is_circuit_open():
            return

        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value) if not isinstance(value, str) else value
            await self.client.setex(key, ttl, serialized)
            await self._record_success()
        except redis.RedisError as e:
            logger.warning("Redis SET failed for key=%s: %s", key, e)
            await self._record_failure()

    async def delete(self, key: str) -> None:
        if await self._is_circuit_open():
            return
        try:
            await self.client.delete(key)
            await self._record_success()
        except redis.RedisError as e:
            logger.warning("Redis DELETE failed for key=%s: %s", key, e)
            await self._record_failure()

    async def exists(self, key: str) -> bool:
        if await self._is_circuit_open():
            return False
        try:
            result: bool = await self.client.exists(key) > 0
            await self._record_success()
            return result
        except redis.RedisError as e:
            logger.warning("Redis EXISTS failed for key=%s: %s", key, e)
            await self._record_failure()
            return False

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.close()
            except redis.RedisError as e:
                logger.warning("Redis CLOSE failed: %s", e)
