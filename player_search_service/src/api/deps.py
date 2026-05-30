from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.cache.redis import RedisCacheAdapter
from src.infrastructure.storage.s3 import S3StorageAdapter
from src.infrastructure.search.repository import SQLAlchemyVideoRepository
from src.usecases.search import SearchVideoUseCase
from src.usecases.playback import GetPlaybackUrlUseCase

@lru_cache
def get_cache_adapter():
    return RedisCacheAdapter()

@lru_cache
def get_storage_adapter():
    return S3StorageAdapter()

def get_search_repository():
    """
    Фабрика репозитория поиска.
    Для тестов передаём session=None — моки подменят БД.
    В продакшене здесь будет: session: AsyncSession = Depends(get_async_session)
    """
    return SQLAlchemyVideoRepository(session=None)

def get_search_usecase():
    return SearchVideoUseCase(
        cache=get_cache_adapter(),
        search_port=get_search_repository()
    )

def get_playback_usecase():
    return GetPlaybackUrlUseCase(storage=get_storage_adapter())