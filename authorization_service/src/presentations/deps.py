from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.session import get_async_session
from shared.security import decode_jwt_token

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

async def get_current_token(
    authorization: str = Header(..., alias="Authorization"),
) -> str:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    return authorization[len(prefix):]


async def get_current_user_id(
    authorization: str = Header(..., alias="Authorization"),
) -> UUID:
    from ..core.settings import AuthSettings as S

    settings = S()
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
            secret=settings.JWT_SECRET.get_secret_value(),
            algorithm=settings.JWT_ALGORITHM,
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


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    settings: AuthSettings = Depends(get_settings),
    user_svc_client: UserServiceClient = Depends(get_user_service_client),
) -> AuthService:
    repo = UserRepository(session)
    return AuthService(user_repo=repo, settings=settings, user_svc_client=user_svc_client)
