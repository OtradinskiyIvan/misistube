import asyncio
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities.user import User
from ..domain.interfaces.repositories import IUserRepository
from .database.models import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if asyncio.iscoroutine(model):
            model = await model
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        if asyncio.iscoroutine(model):
            model = await model
        return self._to_domain(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalar_one_or_none()
        if asyncio.iscoroutine(model):
            model = await model
        return self._to_domain(model) if model else None

    async def save(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def exists_by_email(self, email: str) -> bool:
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == email).limit(1)
        )
        model = result.scalar_one_or_none()
        if asyncio.iscoroutine(model):
            model = await model
        return model is not None

    async def exists_by_username(self, username: str) -> bool:
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.username == username).limit(1)
        )
        model = result.scalar_one_or_none()
        if asyncio.iscoroutine(model):
            model = await model
        return model is not None

    async def deactivate_user(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if asyncio.iscoroutine(model):
            model = await model
        if not model:
            return None
        ts = int(datetime.now().timestamp())
        model.is_active = False
        model.username = f"{model.username}_deleted_{ts}"
        model.email = f"deleted_{ts}@deleted.local"
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def activate_user_by_email(self, email: str) -> None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email).limit(1))
        model = result.scalar_one_or_none()
        if asyncio.iscoroutine(model):
            model = await model
        if not model:
            return
        model.is_active = True
        await self._session.flush()

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            created_at=model.created_at or datetime.now(),
            updated_at=model.updated_at or datetime.now()
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
        )
