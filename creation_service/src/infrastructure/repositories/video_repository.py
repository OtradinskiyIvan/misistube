# infrastructure/repositories/video_repository.py
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from src.domain.entities.video import Video, VideoStatus
from src.domain.exceptions import VideoNotFoundError
from src.domain.interfaces.video_repository import VideoRepositoryProtocol
from src.infrastructure.database.models import VideoModel

class SQLAlchemyVideoRepository(VideoRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, video: Video) -> None:
        model = VideoModel(
            id=video.id,
            user_id=video.user_id,
            title=video.title,
            description=video.description,
            storage_key=video.storage_key,
            status=video.status,
            duration_seconds=video.duration,
            created_at=video.created_at,
            updated_at=video.updated_at,
        )
        self._session.add(model)
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def get(self, video_id: UUID) -> Video | None:
        result = await self._session.execute(
            select(VideoModel).where(VideoModel.id == video_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, limit: int, offset: int, user_id: UUID | None = None) -> list[Video]:
        stmt = select(VideoModel).order_by(VideoModel.created_at.desc())
        stmt = stmt.where(VideoModel.status != VideoStatus.DELETED.value)
        if user_id is not None:
            stmt = stmt.where(VideoModel.user_id == user_id)
        result = await self._session.execute(stmt.limit(limit).offset(offset))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count(self, user_id: UUID | None = None) -> int:
        stmt = select(func.count()).select_from(VideoModel)
        stmt = stmt.where(VideoModel.status != VideoStatus.DELETED.value)
        if user_id is not None:
            stmt = stmt.where(VideoModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def update(self, video: Video) -> None:
        result = await self._session.execute(
            update(VideoModel)
            .where(VideoModel.id == video.id)
            .values(
                user_id=video.user_id,
                title=video.title,
                description=video.description,
                status=video.status,
                duration_seconds=video.duration,
                storage_key=video.storage_key,
                updated_at=video.updated_at,
            )
        )
        await self._session.commit()

    async def update_status(self, video_id: UUID, status: VideoStatus) -> None:
        result = await self._session.execute(
            update(VideoModel)
            .where(VideoModel.id == video_id)
            .values(status=status, updated_at=datetime.now(timezone.utc))
        )
        if result.rowcount == 0:
            raise VideoNotFoundError(video_id)
        await self._session.commit()

    async def delete(self, video_id: UUID) -> None:
        result = await self._session.execute(
            delete(VideoModel).where(VideoModel.id == video_id)
        )
        if result.rowcount == 0:
            raise VideoNotFoundError(video_id)
        await self._session.commit()

    @staticmethod
    def _to_entity(model: VideoModel) -> Video:
        return Video(
            id=model.id,
            title=model.title,
            description=model.description,
            storage_key=model.storage_key,
            status=VideoStatus(model.status),
            duration=model.duration_seconds,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )