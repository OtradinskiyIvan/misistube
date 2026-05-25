"""User repository implementation."""
import sys
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import User
from ..domain.exceptions import UserNotFoundError, UserAlreadyExistsError, UserDeletionError
from ..domain.interfaces import UserRepository
from ..infrastructure.models import UserModel

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.exceptions import InfrastructureError


class UserRepositoryImpl(UserRepository):
    """SQLAlchemy-based User Repository implementation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            db_user = result.scalars().first()
            if not db_user:
                raise UserNotFoundError(str(user_id))
            return self._to_entity(db_user)
        except UserNotFoundError:
            raise
        except Exception as e:
            raise InfrastructureError(f"Failed to get user by id: {str(e)}")

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            stmt = select(UserModel).where(UserModel.username == username)
            result = await self.session.execute(stmt)
            db_user = result.scalars().first()
            return self._to_entity(db_user) if db_user else None
        except Exception as e:
            raise InfrastructureError(f"Failed to get user by username: {str(e)}")

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await self.session.execute(stmt)
            db_user = result.scalars().first()
            return self._to_entity(db_user) if db_user else None
        except Exception as e:
            raise InfrastructureError(f"Failed to get user by email: {str(e)}")

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        try:
            stmt = select(UserModel).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            db_users = result.scalars().all()
            return [self._to_entity(user) for user in db_users]
        except Exception as e:
            raise InfrastructureError(f"Failed to get all users: {str(e)}")

    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            # Check if user already exists
            existing = await self.get_by_username(user.username)
            if existing:
                raise UserAlreadyExistsError("username", user.username)

            existing_email = await self.get_by_email(user.email)
            if existing_email:
                raise UserAlreadyExistsError("email", user.email)

            # Create new user
            db_user = UserModel(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                is_active=user.is_active,
            )
            self.session.add(db_user)
            await self.session.flush()
            return self._to_entity(db_user)
        except (UserAlreadyExistsError, InfrastructureError):
            raise
        except Exception as e:
            raise InfrastructureError(f"Failed to create user: {str(e)}")

    async def update(self, user: User) -> User:
        """Update an existing user."""
        try:
            stmt = select(UserModel).where(UserModel.id == user.id)
            result = await self.session.execute(stmt)
            db_user = result.scalars().first()

            if not db_user:
                raise UserNotFoundError(str(user.id))

            # Check if new username is taken by another user
            if user.username != db_user.username:
                existing = await self.get_by_username(user.username)
                if existing:
                    raise UserAlreadyExistsError("username", user.username)

            # Check if new email is taken by another user
            if user.email != db_user.email:
                existing = await self.get_by_email(user.email)
                if existing:
                    raise UserAlreadyExistsError("email", user.email)

            # Update fields
            db_user.username = user.username
            db_user.email = user.email
            db_user.display_name = user.display_name
            db_user.is_active = user.is_active
            db_user.updated_at = user.updated_at

            await self.session.flush()
            return self._to_entity(db_user)
        except (UserNotFoundError, UserAlreadyExistsError, InfrastructureError):
            raise
        except Exception as e:
            raise InfrastructureError(f"Failed to update user: {str(e)}")

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            db_user = result.scalars().first()

            if not db_user:
                raise UserNotFoundError(str(user_id))

            await self.session.delete(db_user)
            await self.session.flush()
            return True
        except UserNotFoundError:
            raise
        except Exception as e:
            raise UserDeletionError(f"Failed to delete user: {str(e)}")

    @staticmethod
    def _to_entity(db_user: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            display_name=db_user.display_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
