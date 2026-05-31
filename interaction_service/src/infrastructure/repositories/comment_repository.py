from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.comment import CommentModel


class CommentRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: UUID, video_id: UUID, content: str, parent_id: Optional[UUID] = None) -> CommentModel:
        model = CommentModel(
            user_id=user_id,
            video_id=video_id,
            content=content,
            parent_id=parent_id,
        )
        self._session.add(model)
        await self._session.flush()
        return model

    async def get_by_id(self, comment_id: UUID) -> Optional[CommentModel]:
        stmt = select(CommentModel).where(CommentModel.id == comment_id)
        return await self._session.scalar(stmt)

    async def get_by_video(self, video_id: UUID, skip: int = 0, limit: int = 50) -> list[CommentModel]:
        stmt = (
            select(CommentModel)
            .where(CommentModel.video_id == video_id)
            .order_by(CommentModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_video(self, video_id: UUID) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(CommentModel).where(CommentModel.video_id == video_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_content(self, comment_id: UUID, content: str) -> Optional[CommentModel]:
        model = await self.get_by_id(comment_id)
        if model is None:
            return None
        model.content = content
        model.is_edited = True
        await self._session.flush()
        return model

    async def delete(self, comment_id: UUID) -> bool:
        stmt = sa_delete(CommentModel).where(CommentModel.id == comment_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0
