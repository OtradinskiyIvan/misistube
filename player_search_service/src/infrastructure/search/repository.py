import uuid
from datetime import datetime
from typing import cast

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import VideoResult
from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.search.protocol import SearchPort


class SQLAlchemyVideoRepository(SearchPort):
    """Асинхронный репозиторий для поиска видео через SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(
        self, query: str | None, tags: list[str] | None = None, offset: int = 0, limit: int = 20
    ) -> tuple[list[VideoResult], int]:
        """
        Поиск видео с фильтрацией по тексту и тегам.
        """
        base_conditions = [Video.status == VideoStatus.READY]

        if query:
            base_conditions.append(
                or_(Video.title.ilike(f"%{query}%"), Video.description.ilike(f"%{query}%"))
            )

        count_stmt = select(func.count()).select_from(Video).where(*base_conditions)
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0

        data_stmt = (
            select(Video)
            .where(*base_conditions)
            .order_by(Video.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(data_stmt)
        videos = result.scalars().all()

        # 4. МАППИНГ В DTO
        items = [
            VideoResult(
                id=str(v.id),
                title=cast(str, v.title),
                description=cast(str | None, v.description),
                storage_key=cast(str, v.storage_key),
                status=str(cast(VideoStatus, v.status)),
                duration_seconds=cast(int, v.duration_seconds),
                created_at=cast(datetime, v.created_at).isoformat() if v.created_at else None,
                updated_at=cast(datetime, v.updated_at).isoformat() if v.updated_at else None,
                thumbnail_key=cast(str | None, v.thumbnail_key),
                user_id=str(v.user_id),
                username=str(v.user_id),
                # Безопасное получение отсутствующих полей
                tags=getattr(v, "tags", None),
                thumbnail_url=getattr(v, "thumbnail_url", None),
            )
            for v in videos
        ]

        return items, total

    async def get_by_id(self, video_id: str) -> Video | None:
        """Получить видео по ID"""
        from sqlalchemy import select

        try:
            video_uuid = uuid.UUID(video_id)
        except ValueError:
            return None

        stmt = select(Video).where(Video.id == video_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
