# infrastructure/repositories/video_repository.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from src.domain.entities.video import Video, VideoStatus
from src.domain.interfaces.video_repository import VideoRepositoryProtocol
from src.infrastructure.database.models import VideoModel

class SQLAlchemyVideoRepository(VideoRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, video: Video) -> None:
        model = VideoModel(
            id=video.id,
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

    async def list(self, limit: int, offset: int) -> list[Video]:
        result = await self._session.execute(
            select(VideoModel).order_by(VideoModel.created_at.desc()).limit(limit).offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(VideoModel)
        )
        return result.scalar()

    async def update(self, video: Video) -> None:
        result = await self._session.execute(
            update(VideoModel)
            .where(VideoModel.id == video.id)
            .values(
                title=video.title,
                description=video.description,
            status=video.status,
                duration_seconds=video.duration,
                storage_key=video.storage_key,
                updated_at=video.updated_at,
            )
        )
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
            created_at=model.created_at,
            updated_at=model.updated_at,
        )