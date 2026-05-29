import hashlib
import secrets
from typing import Optional
from uuid import UUID, uuid4

from ..domain.entities import User
from ..domain.exceptions import InvalidUserDataError
from ..domain.interfaces import UserRepository


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${pwd_hash.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    salt, pwd_hash = stored.split("$", 1)
    computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return computed.hex() == pwd_hash


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        self._validate_username(username)
        self._validate_email(email)
        self._validate_password(password)

        user = User(
            id=uuid4(),
            username=username,
            email=email,
            hashed_password=_hash_password(password),
            status="active",
        )

        return await self.repository.create(user)

    async def get_user(self, user_id: UUID) -> User:
        return await self.repository.get_by_id(user_id)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        if limit > 1000:
            limit = 1000
        if skip < 0:
            skip = 0

        return await self.repository.get_all(skip=skip, limit=limit)

    async def update_user(
        self,
        user_id: UUID,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        status: Optional[str] = None,
    ) -> User:
        user = await self.repository.get_by_id(user_id)

        if username is not None:
            self._validate_username(username)
            user.username = username

        if email is not None:
            self._validate_email(email)
            user.email = email

        if password is not None:
            self._validate_password(password)
            user.hashed_password = _hash_password(password)

        if status is not None:
            user.status = status

        return await self.repository.update(user)

    async def delete_user(self, user_id: UUID) -> bool:
        return await self.repository.delete(user_id)

    @staticmethod
    def _validate_username(username: str) -> None:
        if not username or len(username) < 3:
            raise InvalidUserDataError("Username must be at least 3 characters long")
        if len(username) > 255:
            raise InvalidUserDataError("Username must not exceed 255 characters")
        if not username.isalnum() and not all(c.isalnum() or c in "_-" for c in username):
            raise InvalidUserDataError(
                "Username can only contain alphanumeric characters, underscores, and hyphens"
            )

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email or "@" not in email:
            raise InvalidUserDataError("Invalid email format")
        if len(email) > 255:
            raise InvalidUserDataError("Email must not exceed 255 characters")

    @staticmethod
    def _validate_password(password: str) -> None:
        if not password or len(password) < 8:
            raise InvalidUserDataError("Password must be at least 8 characters long")
        if len(password) > 128:
            raise InvalidUserDataError("Password must not exceed 128 characters")
