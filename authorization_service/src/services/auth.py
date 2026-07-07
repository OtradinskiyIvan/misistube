import logging
from uuid import UUID

import httpx
from jwt import PyJWTError

from shared.security import create_jwt_token, decode_jwt_token, hash_password, verify_password

from ..core.settings import AuthSettings
from ..domain.entities.user import User
from ..domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError
from ..domain.interfaces.repositories import IUserRepository
from ..infrastructure.clients.user_service_client import UserServiceClient

logger = logging.getLogger("Authorization Service")


class AuthService:
    def __init__(
        self,
        user_repo: IUserRepository,
        settings: AuthSettings,
        user_svc_client: UserServiceClient | None = None,
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
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
            logger.warning("Failed to fetch roles for user %s: %s", user_id, exc)
        return []

    async def _check_user_banned(self, user_id: UUID) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self._settings.USER_SERVICE_URL}/api/v1/users/{user_id}/status"
                )
                if resp.status_code == 200:
                    return resp.json().get("status") == "banned"
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
            logger.warning("Failed to check ban status for user %s: %s", user_id, exc)
        return False

    async def register(self, username: str, email: str, password: str, is_active: bool = True) -> User:
        if await self._user_repo.exists_by_email(email):
            logger.warning("Registration failed: email %s already exists", email)
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        if await self._user_repo.exists_by_username(username):
            logger.warning("Registration failed: username %s already exists", username)
            raise UserAlreadyExistsError(f"User with username {username} already exists")

        hashed_pwd = hash_password(password)
        user = User(
            id=UUID(int=0),  # Placeholder: DB will generate UUID on save
            username=username,
            email=email,
            hashed_password=hashed_pwd,
            is_active=is_active,
        )
        saved = await self._user_repo.save(user)
        logger.info("User registered: %s (%s)", username, email)
        return saved

    async def activate_user(self, email: str) -> None:
        await self._user_repo.activate_user_by_email(email)
        logger.info("User activated: %s", email)

    async def _find_and_validate_user(self, login: str, password: str) -> User:
        user = await self._user_repo.get_by_email(login)

        if not user:
            user = await self._user_repo.get_by_username(login)

        if not user:
            logger.warning("Login failed: user not found: %s", login)
            raise InvalidCredentialsError("Invalid username/email or password")

        if not verify_password(password, user.hashed_password):
            logger.warning("Login failed: wrong password for user %s (%s)", user.username, login)
            raise InvalidCredentialsError("Invalid username/email or password")

        if not user.is_active:
            logger.warning("Login failed: user %s is deactivated", user.username)
            raise InvalidCredentialsError("User account is deactivated")

        return user


    async def login(self, login: str, password: str, admin_key: str | None = None) -> dict[str, str]:
        user = await self._find_and_validate_user(login=login, password=password)

        if admin_key:
            if admin_key != self._settings.ADMIN_KEY:
                logger.warning("Login failed: invalid admin key for user %s (%s)", user.username, login)
                raise InvalidCredentialsError("Invalid admin key")
            token = create_jwt_token(
                subject=str(user.id),
                secret=self._settings.JWT_SECRET,
                algorithm=self._settings.JWT_ALGORITHM,
                expires_minutes=5,
                scope="assign_role",
                roles=["admin"],
            )
            if self._user_svc_client is not None:
                await self._user_svc_client.assign_role(str(user.id), "admin", token)

        if await self._check_user_banned(user.id):
            logger.warning("Login failed: user %s is banned", user.username)
            raise InvalidCredentialsError("User account is banned")

        logger.info("User logged in: %s (%s)", user.username, login)

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
            try:
                await self._user_svc_client.sync_user(access_token)
            except Exception as exc:
                logger.warning("Failed to sync user after login: %s", exc)
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
