from fastapi import Depends
from shared.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.settings import AuthSettings
from ..services.auth import AuthService
from ..infrastructure.repositories import UserRepository

def get_settings() -> AuthSettings:
    return AuthSettings()

def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    settings: AuthSettings = Depends(get_settings)
) -> AuthService:
    repo = UserRepository(session)
    return AuthService(user_repo=repo, settings=settings)