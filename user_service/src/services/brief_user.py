from uuid import UUID

from sqlalchemy import String, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..infrastructure.models.user import UserModel


class BriefUser:
    def __init__(self, id: UUID, username: str, avatar_url: str | None, status: str) -> None:
        self.id = id
        self.username = username
        self.avatar_url = avatar_url
        self.status = status


class BriefUserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_brief(self, user_id: UUID) -> BriefUser | None:
        return await self._session.run_sync(
            lambda sync_session: self._get_brief_sync(sync_session, user_id)
        )

    def _get_brief_sync(self, sync_session, user_id: UUID) -> BriefUser | None:
        stmt = (
            select(UserModel)
            .options(joinedload(UserModel.profile))
            .where(UserModel.id == user_id)
        )
        model = sync_session.execute(stmt).unique().scalar_one_or_none()
        if model is None:
            return None
        return BriefUser(
            id=model.id,
            username=model.username,
            avatar_url=model.profile.avatar_url if model.profile else None,
            status=model.status,
        )

    async def get_batch(self, user_ids: list[UUID]) -> list[BriefUser]:
        return await self._session.run_sync(
            lambda sync_session: self._get_batch_sync(sync_session, user_ids)
        )

    def _get_batch_sync(self, sync_session, user_ids: list[UUID]) -> list[BriefUser]:
        stmt = (
            select(UserModel)
            .options(joinedload(UserModel.profile))
            .where(UserModel.id.in_(user_ids))
        )
        models = sync_session.execute(stmt).unique().scalars().all()
        return [
            BriefUser(
                id=m.id,
                username=m.username,
                avatar_url=m.profile.avatar_url if m.profile else None,
                status=m.status,
            )
            for m in models
        ]

    async def search_brief(self, query: str, skip: int = 0, limit: int = 100) -> list[BriefUser]:
        return await self._session.run_sync(
            lambda sync_session: self._search_brief_sync(sync_session, query, skip, limit)
        )

    def _search_brief_sync(self, sync_session, query: str, skip: int, limit: int) -> list[BriefUser]:
        stmt = (
            select(UserModel)
            .options(joinedload(UserModel.profile))
            .where(
                or_(
                    UserModel.username.ilike(f"%{query}%"),
                    cast(UserModel.id, String).ilike(f"%{query}%"),
                ),
            )
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.username)
        )
        models = sync_session.execute(stmt).unique().scalars().all()
        return [
            BriefUser(
                id=m.id,
                username=m.username,
                avatar_url=m.profile.avatar_url if m.profile else None,
                status=m.status,
            )
            for m in models
        ]
