import uuid
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from .core.logging import bind_correlation_id, configure_structlog, get_logger
from .core.settings import settings, UserServiceSettings
from .infrastructure.database.manager import DatabaseManager
from .infrastructure.database.uow import UnitOfWorkImpl
from .infrastructure.repositories import UserRepositoryImpl
from .services.create_user import CreateUserService
from .services.delete_user import DeleteUserService
from .services.get_user import GetUserService
from .services.update_user import UpdateUserService

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


async def get_create_user_service(
    session: AsyncSession = Depends(get_session),
) -> CreateUserService:
    return CreateUserService(UserRepositoryImpl(session), UnitOfWorkImpl(session))


async def get_get_user_service(
    session: AsyncSession = Depends(get_session),
) -> GetUserService:
    return GetUserService(UserRepositoryImpl(session))


async def get_update_user_service(
    session: AsyncSession = Depends(get_session),
) -> UpdateUserService:
    return UpdateUserService(UserRepositoryImpl(session), UnitOfWorkImpl(session))


async def get_delete_user_service(
    session: AsyncSession = Depends(get_session),
) -> DeleteUserService:
    return DeleteUserService(UserRepositoryImpl(session), UnitOfWorkImpl(session))
