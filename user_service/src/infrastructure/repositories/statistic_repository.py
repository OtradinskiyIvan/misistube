from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities import UserStatistic
from ..models.statistic import UserStatisticModel


class StatisticRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserStatistic]:
        return await self._session.run_sync(
            lambda sync_session: self._get_by_user_id_sync(sync_session, user_id)
        )

    def _get_by_user_id_sync(self, sync_session, user_id: UUID) -> Optional[UserStatistic]:
        model = sync_session.scalar(
            select(UserStatisticModel).where(UserStatisticModel.user_id == user_id)
        )
        return self._to_domain(model) if model else None

    async def create(self, user_id: UUID) -> UserStatistic:
        return await self._session.run_sync(
            lambda sync_session: self._create_sync(sync_session, user_id)
        )

    def _create_sync(self, sync_session, user_id: UUID) -> UserStatistic:
        model = UserStatisticModel(user_id=user_id)
        sync_session.add(model)
        sync_session.flush()
        return self._to_domain(model)

    async def increment_field(self, user_id: UUID, field: str, amount: int = 1) -> None:
        await self._session.run_sync(
            lambda sync_session: self._increment_field_sync(sync_session, user_id, field, amount)
        )

    def _increment_field_sync(self, sync_session, user_id: UUID, field: str, amount: int) -> None:
        stmt = (
            update(UserStatisticModel)
            .where(UserStatisticModel.user_id == user_id)
            .values({field: UserStatisticModel.__table__.c[field] + amount})
        )
        sync_session.execute(stmt)

    async def decrement_field(self, user_id: UUID, field: str, amount: int = 1) -> None:
        await self._session.run_sync(
            lambda sync_session: self._decrement_field_sync(sync_session, user_id, field, amount)
        )

    def _decrement_field_sync(self, sync_session, user_id: UUID, field: str, amount: int) -> None:
        stmt = (
            update(UserStatisticModel)
            .where(UserStatisticModel.user_id == user_id)
            .values({field: UserStatisticModel.__table__.c[field] - amount})
        )
        sync_session.execute(stmt)

    def _to_domain(self, model: UserStatisticModel) -> UserStatistic:
        return UserStatistic(
            id=model.id,
            user_id=model.user_id,
            total_videos=model.total_videos,
            total_views=model.total_views,
            total_subscribers=model.total_subscribers,
            total_likes_received=model.total_likes_received,
            total_comments_received=model.total_comments_received,
            updated_at=model.updated_at,
        )
