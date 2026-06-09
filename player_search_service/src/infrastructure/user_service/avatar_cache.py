import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AvatarCacheService:
    """
    In-memory кэш для URL аватарок пользователей.
    Избегает повторных запросов к user service.
    """
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[Optional[str], float]] = {}
    
    def get(self, user_id: str) -> Optional[str]:
        """
        Получает avatar_url из кэша.
        Возвращает None, если запись отсутствует или устарела.
        """
        if user_id not in self._cache:
            return None
        
        avatar_url, timestamp = self._cache[user_id]
        
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[user_id]
            return None
        
        return avatar_url
    
    def has(self, user_id: str) -> bool:
        """
        Проверяет, есть ли user_id в кэше (независимо от значения).
        Нужно, чтобы различать "нет в кэше" и "в кэше со значением None".
        """
        if user_id not in self._cache:
            return False
        
        _, timestamp = self._cache[user_id]
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[user_id]
            return False
        
        return True
    
    def set(self, user_id: str, avatar_url: Optional[str]) -> None:
        """Сохраняет avatar_url в кэш (можно None — если у пользователя нет аватарки)"""
        self._cache[user_id] = (avatar_url, time.time())
    
    def set_many(self, user_id_to_avatar: dict[str, Optional[str]]) -> None:
        """Сохраняет несколько avatar_url в кэш"""
        now = time.time()
        for user_id, avatar_url in user_id_to_avatar.items():
            self._cache[user_id] = (avatar_url, now)
    
    def clear(self) -> None:
        """Очищает весь кэш"""
        self._cache.clear()
    
    def size(self) -> int:
        """Возвращает количество записей в кэше"""
        return len(self._cache)