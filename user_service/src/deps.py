from collections.abc import AsyncGenerator
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import APIKeyHeader
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from .core.logging import configure_logging, get_logger
from .core.settings import settings, UserServiceSettings
from .infrastructure.database.manager import DatabaseManager
from .infrastructure.database.uow import UnitOfWorkImpl
from .infrastructure.repositories import UserRepositoryImpl, RoleRepositoryImpl, StatisticRepositoryImpl
from .services.create_user import CreateUserService
from .services.delete_user import DeleteUserService
from .services.get_user import GetUserService
from .services.sync_user import SyncUserService
from .services.update_user import UpdateUserService
from .services.assign_role import AssignRoleService
from .services.revoke_role import RevokeRoleService
from .services.get_user_roles import GetUserRolesService
from .services.statistic_service import StatisticService
from .services.subscription_service import SubscriptionService
from .services.brief_user import BriefUserService
from .infrastructure.repositories.subscription_repository import SubscriptionRepositoryImpl

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
    return GetUserService(UserRepositoryImpl(session), RoleRepositoryImpl(session))


async def get_update_user_service(
    session: AsyncSession = Depends(get_session),
) -> UpdateUserService:
    return UpdateUserService(UserRepositoryImpl(session), UnitOfWorkImpl(session))


async def get_sync_user_service(
    session: AsyncSession = Depends(get_session),
) -> SyncUserService:
    return SyncUserService(UserRepositoryImpl(session), UnitOfWorkImpl(session))


async def get_delete_user_service(
    session: AsyncSession = Depends(get_session),
) -> DeleteUserService:
    return DeleteUserService(UserRepositoryImpl(session), UnitOfWorkImpl(session))


async def get_assign_role_service(
    session: AsyncSession = Depends(get_session),
) -> AssignRoleService:
    return AssignRoleService(
        UserRepositoryImpl(session),
        RoleRepositoryImpl(session),
        UnitOfWorkImpl(session),
    )


async def get_revoke_role_service(
    session: AsyncSession = Depends(get_session),
) -> RevokeRoleService:
    return RevokeRoleService(
        UserRepositoryImpl(session),
        RoleRepositoryImpl(session),
        UnitOfWorkImpl(session),
    )


async def get_user_roles_service(
    session: AsyncSession = Depends(get_session),
) -> GetUserRolesService:
    return GetUserRolesService(
        UserRepositoryImpl(session),
        RoleRepositoryImpl(session),
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
            secret=s.JWT_SECRET,
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


async def get_subscription_service(
    session: AsyncSession = Depends(get_session),
) -> SubscriptionService:
    return SubscriptionService(SubscriptionRepositoryImpl(session), UnitOfWorkImpl(session))


async def get_brief_user_service(
    session: AsyncSession = Depends(get_session),
) -> BriefUserService:
    return BriefUserService(session)


async def get_statistic_service(
    session: AsyncSession = Depends(get_session),
) -> StatisticService:
    return StatisticService(StatisticRepositoryImpl(session), UnitOfWorkImpl(session))


_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_internal_api_key(
    x_api_key: str = Depends(_api_key_header),
    settings: UserServiceSettings = Depends(get_settings),
) -> bool:
    return bool(settings.INTERNAL_API_KEY) and x_api_key == settings.INTERNAL_API_KEY
