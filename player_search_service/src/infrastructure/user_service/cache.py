import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class UserCacheService:
    """
    Простой in-memory кэш для username.
    Избегает повторных запросов к user service для одних и тех же пользователей.
    """
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[str, float]] = {}
    
    def get(self, user_id: str) -> Optional[str]:
        """
        Получает username из кэша.
        Возвращает None, если запись отсутствует или устарела.
        """
        if user_id not in self._cache:
            return None
        
        username, timestamp = self._cache[user_id]
        
        # 🔹 Проверяем, не устарела ли запись
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[user_id]
            return None
        
        return username
    
    def set(self, user_id: str, username: str) -> None:
        """Сохраняет username в кэш"""
        self._cache[user_id] = (username, time.time())
    
    def set_many(self, user_id_to_username: dict[str, str]) -> None:
        """Сохраняет несколько username в кэш"""
        now = time.time()
        for user_id, username in user_id_to_username.items():
            self._cache[user_id] = (username, now)
    
    def clear(self) -> None:
        """Очищает весь кэш"""
        self._cache.clear()
    
    def size(self) -> int:
        """Возвращает количество записей в кэше"""
        return len(self._cache)