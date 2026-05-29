import uuid
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from .core.logging import bind_correlation_id, configure_structlog, get_logger
from .core.settings import settings, UserServiceSettings
from .infrastructure.database.manager import DatabaseManager
from .infrastructure.repositories import UserRepositoryImpl
from .services.user_service import UserService

configure_structlog(log_level=settings.LOG_LEVEL, service_name=settings.APP_NAME)

db_manager: Optional[DatabaseManager] = None


def init_db_manager(database_url: str, echo: bool = False) -> DatabaseManager:
    global db_manager
    db_manager = DatabaseManager(database_url, echo=echo)
    return db_manager


def get_db_manager() -> DatabaseManager:
    if db_manager is None:
        raise RuntimeError("DatabaseManager not initialized. Call init_db_manager() first.")
    return db_manager


def get_settings() -> UserServiceSettings:
    return settings


async def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID"),
) -> str:
    correlation_id = x_correlation_id or str(uuid.uuid4())
    bind_correlation_id(correlation_id)
    return correlation_id


def get_logger_dep(correlation_id: str = Depends(get_correlation_id)):
    return get_logger().bind(correlation_id=correlation_id)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    manager = get_db_manager()
    async for session in manager.get_async_session():
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepositoryImpl:
    return UserRepositoryImpl(session)


async def get_user_service(
    repository: UserRepositoryImpl = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)
