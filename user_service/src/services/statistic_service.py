from uuid import UUID

from ..domain.entities import UserStatistic
from ..infrastructure.database.uow import UnitOfWorkImpl
from ..infrastructure.repositories.statistic_repository import StatisticRepositoryImpl

ALLOWED_FIELDS = {
    "total_videos",
    "total_views",
    "total_subscribers",
    "total_likes_received",
    "total_comments_received",
}


class StatisticService:
    def __init__(self, repo: StatisticRepositoryImpl, uow: UnitOfWorkImpl) -> None:
        self._repo = repo
        self._uow = uow

    async def get_or_create(self, user_id: UUID) -> UserStatistic:
        stats = await self._repo.get_by_user_id(user_id)
        if stats is not None:
            return stats
        stats = await self._repo.create(user_id)
        await self._uow.commit()
        return stats

    async def increment(self, user_id: UUID, field: str, amount: int = 1) -> UserStatistic | None:
        if field not in ALLOWED_FIELDS:
            return None
        stats = await self._repo.get_by_user_id(user_id)
        if stats is None:
            stats = await self._repo.create(user_id)
        await self._repo.increment_field(user_id, field, amount)
        await self._uow.commit()
        return await self._repo.get_by_user_id(user_id)

    async def decrement(self, user_id: UUID, field: str, amount: int = 1) -> UserStatistic | None:
        if field not in ALLOWED_FIELDS:
            return None
        stats = await self._repo.get_by_user_id(user_id)
        if stats is None:
            stats = await self._repo.create(user_id)
        await self._repo.decrement_field(user_id, field, amount)
        await self._uow.commit()
        return await self._repo.get_by_user_id(user_id)

    async def get(self, user_id: UUID) -> UserStatistic | None:
        return await self._repo.get_by_user_id(user_id)
