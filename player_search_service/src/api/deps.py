from functools import lru_cache

from fastapi import Depends
from shared.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import PlayerSearchSettings, get_settings
from src.infrastructure.cache.protocol import CachePort
from src.infrastructure.cache.redis import RedisCacheAdapter
from src.infrastructure.search.protocol import SearchPort
from src.infrastructure.search.repository import SQLAlchemyVideoRepository
from src.infrastructure.storage.protocol import StoragePort
from src.infrastructure.storage.s3 import S3StorageAdapter
from src.infrastructure.user_service.client import UserServiceClient
from src.infrastructure.user_service.cache import UserCacheService
from src.usecases.playback import GetPlaybackUrlUseCase
from src.usecases.search import SearchVideoUseCase


@lru_cache
def get_cache_adapter() -> CachePort:
    return RedisCacheAdapter()

@lru_cache
def get_storage_adapter() -> StoragePort:
    return S3StorageAdapter()

@lru_cache
def get_user_service_client() -> UserServiceClient:
    """Фабрика клиента User сервиса"""
    settings = get_settings()
    return UserServiceClient(base_url=settings.USER_SERVICE_URL)

@lru_cache
def get_user_cache() -> UserCacheService:
    """Кэш username пользователей (in-memory, TTL 5 минут)"""
    return UserCacheService(ttl_seconds=300)


def get_search_repository(session: AsyncSession = Depends(get_async_session)) -> SearchPort: # noqa: B008
    """
    Фабрика репозитория.
    Сессия инжектируется через FastAPI DI для каждого запроса.
    """
    return SQLAlchemyVideoRepository(session=session)

def get_search_usecase(
    search_port: SearchPort = Depends(get_search_repository), # noqa: B008
    cache: CachePort = Depends(get_cache_adapter), # noqa: B008
    storage: StoragePort = Depends(get_storage_adapter), # noqa: B008
    user_service_client: UserServiceClient = Depends(get_user_service_client), # noqa: B008
    user_cache: UserCacheService = Depends(get_user_cache), # noqa: B008
) -> SearchVideoUseCase:
    return SearchVideoUseCase(
        cache=cache,
        search_port=search_port,
        storage=storage,
        user_service_client=user_service_client,
        user_cache=user_cache,
    )

async def get_playback_usecase(
    session: AsyncSession = Depends(get_async_session),
    storage: StoragePort = Depends(get_storage_adapter),
    settings: PlayerSearchSettings = Depends(get_settings)
) -> GetPlaybackUrlUseCase:
    search_port = SQLAlchemyVideoRepository(session=session)

    return GetPlaybackUrlUseCase(
        storage=storage,
        search_port=search_port,
        bucket_name=settings.S3_BUCKET_NAME,
        expires_in=settings.S3_PRESIGNED_URL_EXPIRES
    )
