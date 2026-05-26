from typing import Protocol, Optional, Any
from abc import abstractmethod

class CachePort(Protocol):
    """Интерфейс кеш-хранилища"""
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass