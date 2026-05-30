from functools import lru_cache

from src.infrastructure.cache.protocol import CachePort
from src.infrastructure.cache.redis import RedisCacheAdapter
from src.infrastructure.storage.protocol import StoragePort
from src.infrastructure.storage.s3 import S3StorageAdapter
from src.usecases.playback import GetPlaybackUrlUseCase
from src.usecases.search import SearchVideoUseCase


@lru_cache
def get_cache_adapter() -> CachePort:
    """Singleton кеш-адаптера"""
    return RedisCacheAdapter()

@lru_cache
def get_storage_adapter() -> StoragePort:
    """Singleton S3-адаптера"""
    return S3StorageAdapter()

def get_search_usecase() -> SearchVideoUseCase:
    return SearchVideoUseCase(RedisCacheAdapter())

def get_playback_usecase() -> GetPlaybackUrlUseCase:
    return GetPlaybackUrlUseCase(S3StorageAdapter())
