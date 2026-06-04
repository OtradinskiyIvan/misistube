from collections.abc import AsyncGenerator
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from .core.logging import configure_logging, get_logger
from .core.settings import settings, InteractionSettings
from .infrastructure.database.manager import DatabaseManager
from .infrastructure.database.uow import UnitOfWorkImpl
from .infrastructure.repositories.comment_repository import CommentRepositoryImpl
from .infrastructure.repositories.like_repository import LikeRepositoryImpl
from .services.comment_service import CommentService
from .services.like_service import LikeService
from .infrastructure.clients.user_service_client import UserServiceClient

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


def get_settings() -> InteractionSettings:
    return settings


def get_logger_dep():
    return get_logger(settings.APP_NAME, settings.LOG_LEVEL)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    manager = get_db_manager()
    async for session in manager.get_async_session():
        yield session


async def get_like_service(
    session: AsyncSession = Depends(get_session),
) -> LikeService:
    return LikeService(
        LikeRepositoryImpl(session),
        UnitOfWorkImpl(session),
    )


async def get_comment_service(
    session: AsyncSession = Depends(get_session),
) -> CommentService:
    return CommentService(
        CommentRepositoryImpl(session),
        UnitOfWorkImpl(session),
    )


async def get_user_service_client(
    s: InteractionSettings = Depends(get_settings),
) -> UserServiceClient:
    return UserServiceClient(base_url=s.USER_SERVICE_URL)


async def get_current_user_id(
    authorization: str = Header(..., alias="Authorization"),
) -> UUID:
    from .core.settings import settings as s
    from shared.security import decode_jwt_token

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    token = authorization[len(prefix):]
    try:
        payload = decode_jwt_token(
            token,
            secret=s.JWT_SECRET.get_secret_value(),
            algorithm=s.JWT_ALGORITHM,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )
    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )


async def get_current_user_payload(
    authorization: str = Header(..., alias="Authorization"),
) -> dict:
    from .core.settings import settings as s
    from shared.security import decode_jwt_token

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    token = authorization[len(prefix):]
    try:
        return decode_jwt_token(
            token,
            secret=s.JWT_SECRET.get_secret_value(),
            algorithm=s.JWT_ALGORITHM,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def require_admin(payload: dict = Depends(get_current_user_payload)) -> dict:
    roles = payload.get("roles", [])
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return payload
