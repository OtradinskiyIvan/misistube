"""User Service with business logic."""
from typing import Optional
from uuid import UUID, uuid4

from ..domain.entities import User
from ..domain.exceptions import InvalidUserDataError
from ..domain.interfaces import UserRepository


class UserService:
    """User Service containing business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(
        self,
        username: str,
        email: str,
        display_name: Optional[str] = None,
    ) -> User:
        """Create a new user with business logic validation."""
        # Business logic validation
        self._validate_username(username)
        self._validate_email(email)

        user = User(
            id=uuid4(),
            username=username,
            email=email,
            display_name=display_name,
            is_active=True,
        )

        return await self.repository.create(user)

    async def get_user(self, user_id: UUID) -> User:
        """Get user by ID."""
        return await self.repository.get_by_id(user_id)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        if limit > 1000:
            limit = 1000  # Max limit
        if skip < 0:
            skip = 0

        return await self.repository.get_all(skip=skip, limit=limit)

    async def update_user(
        self,
        user_id: UUID,
        username: Optional[str] = None,
        email: Optional[str] = None,
        display_name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> User:
        """Update user with business logic validation."""
        user = await self.repository.get_by_id(user_id)

        # Validate new values if provided
        if username is not None:
            self._validate_username(username)
            user.username = username

        if email is not None:
            self._validate_email(email)
            user.email = email

        if display_name is not None:
            user.display_name = display_name

        if is_active is not None:
            user.is_active = is_active

        return await self.repository.update(user)

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user by ID."""
        return await self.repository.delete(user_id)

    @staticmethod
    def _validate_username(username: str) -> None:
        """Validate username format."""
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
        """Validate email format (simple validation)."""
        if not email or "@" not in email:
            raise InvalidUserDataError("Invalid email format")
        if len(email) > 255:
            raise InvalidUserDataError("Email must not exceed 255 characters")
