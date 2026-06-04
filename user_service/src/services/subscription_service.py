from uuid import UUID

from ..domain.entities import UserSubscription
from ..infrastructure.database.uow import UnitOfWorkImpl
from ..infrastructure.repositories.subscription_repository import SubscriptionRepositoryImpl


class SubscriptionService:
    def __init__(self, repo: SubscriptionRepositoryImpl, uow: UnitOfWorkImpl) -> None:
        self._repo = repo
        self._uow = uow

    async def follow(self, follower_id: UUID, following_id: UUID) -> UserSubscription:
        result = await self._repo.follow(follower_id, following_id)
        await self._uow.commit()
        return result

    async def unfollow(self, follower_id: UUID, following_id: UUID) -> bool:
        result = await self._repo.unfollow(follower_id, following_id)
        if result:
            await self._uow.commit()
        return result

    async def is_following(self, follower_id: UUID, following_id: UUID) -> bool:
        return await self._repo.is_following(follower_id, following_id)

    async def get_followers(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[UserSubscription]:
        return await self._repo.get_followers(user_id, skip, limit)

    async def get_following(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[UserSubscription]:
        return await self._repo.get_following(user_id, skip, limit)

    async def count_followers(self, user_id: UUID) -> int:
        return await self._repo.count_followers(user_id)

    async def count_following(self, user_id: UUID) -> int:
        return await self._repo.count_following(user_id)
