import sys
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session as SyncSession

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from ..domain.entities import User
from ..domain.exceptions import (
    UserAlreadyExistsError,
    UserDeletionError,
    UserNotFoundError,
)
from ..domain.interfaces import UserRepository
from ..infrastructure.models import UserModel
from shared.exceptions import InfrastructureError


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            return await self.session.run_sync(self._get_by_id_sync, user_id)
        except (UserNotFoundError, InfrastructureError):
            raise
        except Exception as e:
            raise InfrastructureError(f"Failed to get user by id: {str(e)}")

    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            return await self.session.run_sync(self._get_by_username_sync, username)
        except Exception as e:
            raise InfrastructureError(f"Failed to get user by username: {str(e)}")

    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            return await self.session.run_sync(self._get_by_email_sync, email)
        except Exception as e:
            raise InfrastructureError(f"Failed to get user by email: {str(e)}")

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        try:
            return await self.session.run_sync(self._get_all_sync, skip, limit)
        except Exception as e:
            raise InfrastructureError(f"Failed to get all users: {str(e)}")

    async def create(self, user: User) -> User:
        try:
            return await self.session.run_sync(self._create_sync, user)
        except (UserAlreadyExistsError, InfrastructureError):
            raise
        except Exception as e:
            raise InfrastructureError(f"Failed to create user: {str(e)}")

    async def update(self, user: User) -> User:
        try:
            return await self.session.run_sync(self._update_sync, user)
        except (UserNotFoundError, UserAlreadyExistsError, InfrastructureError):
            raise
        except Exception as e:
            raise InfrastructureError(f"Failed to update user: {str(e)}")

    async def delete(self, user_id: UUID) -> bool:
        try:
            return await self.session.run_sync(self._delete_sync, user_id)
        except UserNotFoundError:
            raise
        except Exception as e:
            raise UserDeletionError(f"Failed to delete user: {str(e)}")

    # ========== Sync implementations (called via run_sync) ==========

    @staticmethod
    def _get_by_id_sync(session: SyncSession, user_id: UUID) -> Optional[User]:
        db_user = session.get(UserModel, user_id)
        if not db_user:
            raise UserNotFoundError(str(user_id))
        return UserRepositoryImpl._to_entity(db_user)

    @staticmethod
    def _get_by_username_sync(session: SyncSession, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        db_user = session.scalars(stmt).first()
        return UserRepositoryImpl._to_entity(db_user) if db_user else None

    @staticmethod
    def _get_by_email_sync(session: SyncSession, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        db_user = session.scalars(stmt).first()
        return UserRepositoryImpl._to_entity(db_user) if db_user else None

    @staticmethod
    def _get_all_sync(session: SyncSession, skip: int, limit: int) -> list[User]:
        stmt = select(UserModel).offset(skip).limit(limit)
        db_users = session.scalars(stmt).all()
        return [UserRepositoryImpl._to_entity(u) for u in db_users]

    @staticmethod
    def _create_sync(session: SyncSession, user: User) -> User:
        existing = session.scalars(
            select(UserModel).where(UserModel.username == user.username),
        ).first()
        if existing:
            raise UserAlreadyExistsError("username", user.username)

        existing = session.scalars(
            select(UserModel).where(UserModel.email == user.email),
        ).first()
        if existing:
            raise UserAlreadyExistsError("email", user.email)

        db_user = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            status=user.status,
        )
        session.add(db_user)
        session.flush()
        return UserRepositoryImpl._to_entity(db_user)

    @staticmethod
    def _update_sync(session: SyncSession, user: User) -> User:
        db_user = session.get(UserModel, user.id)
        if not db_user:
            raise UserNotFoundError(str(user.id))

        if user.username != db_user.username:
            existing = session.scalars(
                select(UserModel).where(
                    UserModel.username == user.username,
                    UserModel.id != user.id,
                ),
            ).first()
            if existing:
                raise UserAlreadyExistsError("username", user.username)

        if user.email != db_user.email:
            existing = session.scalars(
                select(UserModel).where(
                    UserModel.email == user.email,
                    UserModel.id != user.id,
                ),
            ).first()
            if existing:
                raise UserAlreadyExistsError("email", user.email)

        db_user.username = user.username
        db_user.email = user.email
        db_user.hashed_password = user.hashed_password
        db_user.status = user.status
        db_user.updated_at = user.updated_at

        session.flush()
        return UserRepositoryImpl._to_entity(db_user)

    @staticmethod
    def _delete_sync(session: SyncSession, user_id: UUID) -> bool:
        db_user = session.get(UserModel, user_id)
        if not db_user:
            raise UserNotFoundError(str(user_id))
        session.delete(db_user)
        session.flush()
        return True

    @staticmethod
    def _to_entity(db_user: UserModel) -> User:
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            status=db_user.status,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
