from uuid import UUID
from shared.security import hash_password, verify_password, create_jwt_token
from ..domain.entities.user import User
from ..domain.interfaces.repositories import IUserRepository
from ..domain.exceptions import UserNotFoundError, UserAlreadyExistsError, InvalidCredentialsError
from ..core.settings import AuthSettings

class AuthService:
    def __init__(self, user_repo: IUserRepository, settings: AuthSettings):
        self._user_repo = user_repo
        self._settings = settings

    async def register(self, email: str, password: str) -> User:
        if await self._user_repo.exists_by_email(email):
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        hashed_pwd = hash_password(password)
        user = User(
            id=UUID(int=0),  # Placeholder: DB сгенерирует UUID при сохранении
            email=email,
            hashed_password=hashed_pwd
        )
        return await self._user_repo.save(user)

    async def login(self, email: str, password: str) -> dict[str, str]:
        user = await self._user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User account is deactivated")

        access_token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_ACCESS_EXPIRE_MINUTES
        )
        refresh_token = create_jwt_token(
            subject=str(user.id),
            secret=self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=self._settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 60
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def get_user(self, user_id: UUID) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user