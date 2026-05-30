from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.cache.redis import RedisCacheAdapter
from src.infrastructure.cache.protocol import CachePort
from src.infrastructure.storage.s3 import S3StorageAdapter
from src.infrastructure.storage.protocol import StoragePort
from src.infrastructure.search.repository import SQLAlchemyVideoRepository
from src.infrastructure.search.protocol import SearchPort
from src.usecases.search import SearchVideoUseCase
from src.usecases.playback import GetPlaybackUrlUseCase

from shared.database.session import get_async_session

@lru_cache
def get_cache_adapter() -> CachePort:
    return RedisCacheAdapter()

@lru_cache
def get_storage_adapter() -> StoragePort:
    return S3StorageAdapter()

def get_search_repository(session: AsyncSession = Depends(get_async_session)) -> SearchPort:
    """
    Фабрика репозитория.
    Сессия инжектируется через FastAPI DI для каждого запроса.
    """
    return SQLAlchemyVideoRepository(session=session)

def get_search_usecase(
    search_port: SearchPort = Depends(get_search_repository)
) -> SearchVideoUseCase:
    """Фабрика UseCase поиска"""
    return SearchVideoUseCase(
        cache=get_cache_adapter(),
        search_port=search_port
    )

def get_playback_usecase() -> GetPlaybackUrlUseCase:
    """Фабрика UseCase воспроизведения"""
    return GetPlaybackUrlUseCase(storage=get_storage_adapter())