from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities import UserSubscription
from ..models.subscription import UserSubscriptionModel


class SubscriptionRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def follow(self, follower_id: UUID, following_id: UUID) -> UserSubscription:
        return await self._session.run_sync(
            lambda sync_session: self._follow_sync(sync_session, follower_id, following_id)
        )

    def _follow_sync(self, sync_session, follower_id: UUID, following_id: UUID) -> UserSubscription:
        existing = sync_session.scalar(
            select(UserSubscriptionModel).where(
                UserSubscriptionModel.follower_id == follower_id,
                UserSubscriptionModel.following_id == following_id,
            )
        )
        if existing is not None:
            return self._to_domain(existing)

        model = UserSubscriptionModel(
            follower_id=follower_id,
            following_id=following_id,
        )
        sync_session.add(model)
        sync_session.flush()
        return self._to_domain(model)

    async def unfollow(self, follower_id: UUID, following_id: UUID) -> bool:
        return await self._session.run_sync(
            lambda sync_session: self._unfollow_sync(sync_session, follower_id, following_id)
        )

    def _unfollow_sync(self, sync_session, follower_id: UUID, following_id: UUID) -> bool:
        stmt = sa_delete(UserSubscriptionModel).where(
            UserSubscriptionModel.follower_id == follower_id,
            UserSubscriptionModel.following_id == following_id,
        )
        result = sync_session.execute(stmt)
        return result.rowcount > 0

    async def is_following(self, follower_id: UUID, following_id: UUID) -> bool:
        return await self._session.run_sync(
            lambda sync_session: self._is_following_sync(sync_session, follower_id, following_id)
        )

    def _is_following_sync(self, sync_session, follower_id: UUID, following_id: UUID) -> bool:
        model = sync_session.scalar(
            select(UserSubscriptionModel).where(
                UserSubscriptionModel.follower_id == follower_id,
                UserSubscriptionModel.following_id == following_id,
            )
        )
        return model is not None

    async def get_followers(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[UserSubscription]:
        return await self._session.run_sync(
            lambda sync_session: self._get_followers_sync(sync_session, user_id, skip, limit)
        )

    def _get_followers_sync(self, sync_session, user_id: UUID, skip: int, limit: int) -> list[UserSubscription]:
        stmt = (
            select(UserSubscriptionModel)
            .where(UserSubscriptionModel.following_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(UserSubscriptionModel.subscribed_at)
        )
        models = sync_session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_following(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[UserSubscription]:
        return await self._session.run_sync(
            lambda sync_session: self._get_following_sync(sync_session, user_id, skip, limit)
        )

    def _get_following_sync(self, sync_session, user_id: UUID, skip: int, limit: int) -> list[UserSubscription]:
        stmt = (
            select(UserSubscriptionModel)
            .where(UserSubscriptionModel.follower_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(UserSubscriptionModel.subscribed_at)
        )
        models = sync_session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    async def count_followers(self, user_id: UUID) -> int:
        return await self._session.run_sync(
            lambda sync_session: self._count_followers_sync(sync_session, user_id)
        )

    def _count_followers_sync(self, sync_session, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(UserSubscriptionModel).where(
            UserSubscriptionModel.following_id == user_id
        )
        return sync_session.scalar(stmt)

    async def count_following(self, user_id: UUID) -> int:
        return await self._session.run_sync(
            lambda sync_session: self._count_following_sync(sync_session, user_id)
        )

    def _count_following_sync(self, sync_session, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(UserSubscriptionModel).where(
            UserSubscriptionModel.follower_id == user_id
        )
        return sync_session.scalar(stmt)

    def _to_domain(self, model: UserSubscriptionModel) -> UserSubscription:
        return UserSubscription(
            id=model.id,
            follower_id=model.follower_id,
            following_id=model.following_id,
            subscribed_at=model.subscribed_at,
        )
