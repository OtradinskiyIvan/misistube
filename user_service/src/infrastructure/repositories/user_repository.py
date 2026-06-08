from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities import User
from ...domain.exceptions import UserNotFoundError, UserAlreadyExistsError, UserDeletionError
from ..models.profile import UserProfileModel
from ..models.user import UserModel


class UserRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self._session.run_sync(
            lambda sync_session: self._get_by_id_sync(sync_session, user_id)
        )

    def _get_by_id_sync(self, sync_session, user_id: UUID) -> Optional[User]:
        model = sync_session.get(UserModel, user_id)
        if model is None:
            raise UserNotFoundError(str(user_id))
        return self._to_domain(model)

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self._session.run_sync(
            lambda sync_session: self._get_by_username_sync(sync_session, username)
        )

    def _get_by_username_sync(self, sync_session, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        model = sync_session.scalar(stmt)
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self._session.run_sync(
            lambda sync_session: self._get_by_email_sync(sync_session, email)
        )

    def _get_by_email_sync(self, sync_session, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        model = sync_session.scalar(stmt)
        if model is None:
            return None
        return self._to_domain(model)

    async def search_by_username(self, query: str, skip: int = 0, limit: int = 100) -> list[User]:
        return await self._session.run_sync(
            lambda sync_session: self._search_by_username_sync(sync_session, query, skip, limit)
        )

    def _search_by_username_sync(self, sync_session, query: str, skip: int, limit: int) -> list[User]:
        stmt = (
            select(UserModel)
            .where(UserModel.username.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.username)
        )
        models = sync_session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self._session.run_sync(
            lambda sync_session: self._get_all_sync(sync_session, skip, limit)
        )

    def _get_all_sync(self, sync_session, skip: int, limit: int) -> list[User]:
        stmt = select(UserModel).offset(skip).limit(limit).order_by(UserModel.created_at)
        models = sync_session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    async def create(self, user: User) -> User:
        return await self._session.run_sync(
            lambda sync_session: self._create_sync(sync_session, user)
        )

    def _create_sync(self, sync_session, user: User) -> User:
        existing_username = sync_session.scalar(
            select(UserModel).where(UserModel.username == user.username)
        )
        if existing_username is not None:
            raise UserAlreadyExistsError("username", user.username)

        existing_email = sync_session.scalar(
            select(UserModel).where(UserModel.email == user.email)
        )
        if existing_email is not None:
            raise UserAlreadyExistsError("email", user.email)

        model = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            status=user.status,
        )
        sync_session.add(model)
        sync_session.flush()
        profile = UserProfileModel(id=uuid4(), user_id=model.id)
        sync_session.add(profile)
        sync_session.flush()
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        return await self._session.run_sync(
            lambda sync_session: self._update_sync(sync_session, user)
        )

    def _update_sync(self, sync_session, user: User) -> User:
        model = sync_session.get(UserModel, user.id)
        if model is None:
            raise UserNotFoundError(str(user.id))

        model.username = user.username
        model.email = user.email
        model.status = user.status
        sync_session.flush()
        return self._to_domain(model)

    async def delete(self, user_id: UUID) -> bool:
        return await self._session.run_sync(
            lambda sync_session: self._delete_sync(sync_session, user_id)
        )

    def _delete_sync(self, sync_session, user_id: UUID) -> bool:
        model = sync_session.get(UserModel, user_id)
        if model is None:
            raise UserNotFoundError(str(user_id))

        sync_session.delete(model)
        sync_session.flush()
        return True

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
