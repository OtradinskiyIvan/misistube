from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.session import get_async_session

from ..core.settings import AuthSettings
from ..infrastructure.repositories import UserRepository
from ..services.auth import AuthService
from ..infrastructure.clients.user_service_client import UserServiceClient


def get_settings() -> AuthSettings:
    return AuthSettings()

def get_user_service_client(
    settings: AuthSettings = Depends(get_settings)
) -> UserServiceClient:
    return UserServiceClient(
        base_url=settings.USER_SERVICE_URL,
        internal_api_key=settings.INTERNAL_API_KEY,
    )

def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    settings: AuthSettings = Depends(get_settings),
    user_svc_client: UserServiceClient = Depends(get_user_service_client),
) -> AuthService:
    repo = UserRepository(session)
    return AuthService(user_repo=repo, settings=settings, user_svc_client=user_svc_client)
