from uuid import UUID

from ..infrastructure.database.uow import UnitOfWorkImpl
from ..infrastructure.repositories.like_repository import LikeRepositoryImpl


class LikeService:
    def __init__(
        self,
        like_repo: LikeRepositoryImpl,
        uow: UnitOfWorkImpl,
    ) -> None:
        self._like_repo = like_repo
        self._uow = uow

    async def like(self, user_id: UUID, video_id: UUID) -> bool:
        existing = await self._like_repo.get_by_user_and_video(user_id, video_id)
        if existing is not None:
            return False

        await self._like_repo.add(user_id, video_id)
        await self._uow.commit()
        return True

    async def unlike(self, user_id: UUID, video_id: UUID) -> bool:
        removed = await self._like_repo.remove(user_id, video_id)
        if removed:
            await self._uow.commit()
        return removed

    async def is_liked(self, user_id: UUID, video_id: UUID) -> bool:
        existing = await self._like_repo.get_by_user_and_video(user_id, video_id)
        return existing is not None

    async def get_video_likes(self, video_id: UUID) -> list[UUID]:
        likes = await self._like_repo.get_by_video(video_id)
        return [like.user_id for like in likes]

    async def get_video_likes_count(self, video_id: UUID) -> int:
        return await self._like_repo.count_by_video(video_id)
