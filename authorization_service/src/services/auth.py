from uuid import UUID

from shared.security import create_jwt_token, hash_password, verify_password

from ..core.settings import AuthSettings
from ..domain.entities.user import User
from ..domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError
from ..domain.interfaces.repositories import IUserRepository


class AuthService:
    def __init__(self, user_repo: IUserRepository, settings: AuthSettings):
        self._user_repo = user_repo
        self._settings = settings

    async def register(self, username: str, email: str, password: str) -> User:
        if await self._user_repo.exists_by_email(email):
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        if await self._user_repo.exists_by_username(username):
            raise UserAlreadyExistsError(f"User with username {username} already exists")

        hashed_pwd = hash_password(password)
        user = User(
            id=UUID(int=0),  # Placeholder: DB сгенерирует UUID при сохранении
            username=username,
            email=email,
            hashed_password=hashed_pwd
        )
        return await self._user_repo.save(user)

    async def login(self, login: str, password: str) -> dict[str, str]:
        # Try to get user by email first, then by username
        user = await self._user_repo.get_by_email(login)
        if not user:
            user = await self._user_repo.get_by_username(login)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid username/email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User account is deactivated")

        access_token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_ACCESS_EXPIRE_MINUTES,
            username=user.username,
            email=user.email
        )
        refresh_token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 60,
            username=user.username,
            email=user.email
        )
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}

    async def get_user(self, user_id: UUID) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
