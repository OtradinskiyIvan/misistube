from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.role import UserRoleModel


class RoleRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_roles_by_user_id(self, user_id: UUID) -> list[str]:
        stmt = select(UserRoleModel).where(UserRoleModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [r.role for r in result.scalars().all()]

    async def assign_role(self, user_id: UUID, role: str, assigned_by: Optional[UUID] = None) -> UserRoleModel:
        stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == user_id,
            UserRoleModel.role == role,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        model = UserRoleModel(user_id=user_id, role=role, assigned_by=assigned_by)
        self._session.add(model)
        await self._session.flush()
        return model

    async def revoke_role(self, user_id: UUID, role: str) -> bool:
        stmt = sa_delete(UserRoleModel).where(
            UserRoleModel.user_id == user_id,
            UserRoleModel.role == role,
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def has_role(self, user_id: UUID, role: str) -> bool:
        stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == user_id,
            UserRoleModel.role == role,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
