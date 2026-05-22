import uuid
import sys
from pathlib import Path
from typing import Optional, AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import bind_correlation_id, configure_structlog, get_logger
from src.core.settings import settings, UserServiceSettings
from src.infrastructure.repositories import UserRepositoryImpl
from src.services.user_service import UserService

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.database.session import get_async_session

configure_structlog(log_level=settings.LOG_LEVEL, service_name=settings.APP_NAME)


def get_settings() -> UserServiceSettings:
    """Get application settings."""
    return settings


async def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID"),
) -> str:
    """Get or generate correlation ID from request headers."""
    correlation_id = x_correlation_id or str(uuid.uuid4())
    bind_correlation_id(correlation_id)
    return correlation_id


def get_logger_dep(correlation_id: str = Depends(get_correlation_id)):
    """Get logger with correlation ID binding."""
    return get_logger().bind(correlation_id=correlation_id)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async for session in get_async_session():
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepositoryImpl:
    """Get User Repository instance with injected session."""
    return UserRepositoryImpl(session)


async def get_user_service(
    repository: UserRepositoryImpl = Depends(get_user_repository),
) -> UserService:
    """Get User Service instance with injected repository."""
    return UserService(repository)
