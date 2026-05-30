from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.session import get_async_session

from ..core.settings import AuthSettings
from ..infrastructure.repositories import UserRepository
from ..services.auth import AuthService


def get_settings() -> AuthSettings:
    return AuthSettings()

def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    settings: AuthSettings = Depends(get_settings)
) -> AuthService:
    repo = UserRepository(session)
    return AuthService(user_repo=repo, settings=settings)
