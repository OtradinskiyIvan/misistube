from functools import lru_cache

from fastapi import Depends
from shared.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.cache.protocol import CachePort
from src.infrastructure.cache.redis import RedisCacheAdapter
from src.infrastructure.search.protocol import SearchPort
from src.infrastructure.search.repository import SQLAlchemyVideoRepository
from src.infrastructure.storage.protocol import StoragePort
from src.infrastructure.storage.s3 import S3StorageAdapter
from src.usecases.playback import GetPlaybackUrlUseCase
from src.usecases.search import SearchVideoUseCase


@lru_cache
def get_cache_adapter() -> CachePort:
    return RedisCacheAdapter()

@lru_cache
def get_storage_adapter() -> StoragePort:
    return S3StorageAdapter()

def get_search_repository(session: AsyncSession = Depends(get_async_session)) -> SearchPort: # noqa: B008
    """
    Фабрика репозитория.
    Сессия инжектируется через FastAPI DI для каждого запроса.
    """
    return SQLAlchemyVideoRepository(session=session)

def get_search_usecase(
    search_port: SearchPort = Depends(get_search_repository) # noqa: B008
) -> SearchVideoUseCase:
    """Фабрика UseCase поиска"""
    return SearchVideoUseCase(
        cache=get_cache_adapter(),
        search_port=search_port
    )

def get_playback_usecase(
    storage: StoragePort = Depends(get_storage_adapter)
) -> GetPlaybackUrlUseCase:
    """Фабрика UseCase воспроизведения с инъекцией настроек"""
    settings = get_settings()
    return GetPlaybackUrlUseCase(
        storage=storage,
        bucket_name=settings.S3_BUCKET_NAME,
        expires_in=settings.S3_PRESIGNED_URL_EXPIRES
    )
