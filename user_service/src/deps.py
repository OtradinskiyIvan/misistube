from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .core.logging import configure_logging, get_logger
from .core.settings import settings, UserServiceSettings
from .infrastructure.database.manager import DatabaseManager
from .infrastructure.database.uow import UnitOfWorkImpl
from .infrastructure.repositories import UserRepositoryImpl
from .services.create_user import CreateUserService
from .services.delete_user import DeleteUserService
from .services.get_user import GetUserService
from .services.update_user import UpdateUserService

configure_logging(log_level=settings.LOG_LEVEL, service_name=settings.APP_NAME)

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


def get_logger_dep():
    return get_logger(settings.APP_NAME, settings.LOG_LEVEL)


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
