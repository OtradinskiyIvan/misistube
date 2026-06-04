from uuid import UUID

import httpx
from jwt import PyJWTError

from shared.security import create_jwt_token, decode_jwt_token, hash_password, verify_password

from typing import Optional

from ..core.settings import AuthSettings
from ..domain.entities.user import User
from ..domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError
from ..domain.interfaces.repositories import IUserRepository
from ..infrastructure.clients.user_service_client import UserServiceClient


class AuthService:
    def __init__(
        self,
        user_repo: IUserRepository,
        settings: AuthSettings,
        user_svc_client: Optional[UserServiceClient] = None,
    ):
        self._user_repo = user_repo
        self._settings = settings
        self._user_svc_client = user_svc_client

    async def _fetch_user_roles(self, user_id: UUID) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self._settings.USER_SERVICE_URL}/api/v1/users/{user_id}/roles"
                )
                if resp.status_code == 200:
                    return resp.json().get("roles", [])
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
            pass
        return []

    async def _check_user_banned(self, user_id: UUID) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self._settings.USER_SERVICE_URL}/api/v1/users/{user_id}/status"
                )
                if resp.status_code == 200:
                    return resp.json().get("status") == "banned"
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
            pass
        return False

    async def register(self, username: str, email: str, password: str, is_active: bool = True) -> User:
        if await self._user_repo.exists_by_email(email):
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        if await self._user_repo.exists_by_username(username):
            raise UserAlreadyExistsError(f"User with username {username} already exists")

        hashed_pwd = hash_password(password)
        user = User(
            id=UUID(int=0),  # Placeholder: DB will generate UUID on save
            username=username,
            email=email,
            hashed_password=hashed_pwd,
            is_active=is_active,
        )
        return await self._user_repo.save(user)

    async def activate_user(self, email: str) -> None:
        await self._user_repo.activate_user_by_email(email)

    async def login(self, login: str, password: str) -> dict[str, str]:
        # Try to get user by email first, then by username
        user = await self._user_repo.get_by_email(login)
        if not user:
            user = await self._user_repo.get_by_username(login)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid username/email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User account is deactivated")

        if await self._check_user_banned(user.id):
            raise InvalidCredentialsError("User account is banned")

        roles = await self._fetch_user_roles(user.id)

        access_token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_ACCESS_EXPIRE_MINUTES,
            username=user.username,
            email=user.email,
            token_type="access",
            roles=roles,
        )
        refresh_token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 60,
            username=user.username,
            email=user.email,
            token_type="refresh",
            roles=roles,
        )
        if self._user_svc_client is not None:
            await self._user_svc_client.sync_user(access_token)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}

    async def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_jwt_token(refresh_token, self._settings.JWT_SECRET, algorithm=self._settings.JWT_ALGORITHM)
        except PyJWTError as exc:
            raise InvalidCredentialsError("Invalid refresh token") from exc

        if payload.get("token_type") != "refresh":
            raise InvalidCredentialsError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError("Invalid refresh token")

        user = await self._user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise InvalidCredentialsError("Invalid refresh token")

        roles = payload.get("roles", [])

        access_token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_ACCESS_EXPIRE_MINUTES,
            username=user.username,
            email=user.email,
            token_type="access",
            roles=roles,
        )
        return {"access_token": access_token, "token_type": "Bearer"}

    async def get_user(self, user_id: UUID) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    async def sync_user_to_user_service(self, user: User) -> None:
        if self._user_svc_client is None:
            return
        token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=5,
            username=user.username,
            email=user.email,
            token_type="access",
        )
        await self._user_svc_client.sync_user(token)
