from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.like import LikeModel


class LikeRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_id: UUID, video_id: UUID) -> LikeModel:
        model = LikeModel(user_id=user_id, video_id=video_id)
        self._session.add(model)
        await self._session.flush()
        return model

    async def remove(self, user_id: UUID, video_id: UUID) -> bool:
        stmt = sa_delete(LikeModel).where(
            LikeModel.user_id == user_id,
            LikeModel.video_id == video_id,
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_by_user_and_video(self, user_id: UUID, video_id: UUID) -> Optional[LikeModel]:
        stmt = select(LikeModel).where(
            LikeModel.user_id == user_id,
            LikeModel.video_id == video_id,
        )
        return await self._session.scalar(stmt)

    async def get_by_video(self, video_id: UUID) -> list[LikeModel]:
        stmt = select(LikeModel).where(LikeModel.video_id == video_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_video(self, video_id: UUID) -> int:
        stmt = select(func.count()).select_from(LikeModel).where(LikeModel.video_id == video_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()
