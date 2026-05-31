from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.search.protocol import SearchPort
from src.api.schemas import VideoResult


class SQLAlchemyVideoRepository(SearchPort):
    """Асинхронный репозиторий для поиска видео через SQLAlchemy"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(
        self,
        query: Optional[str],
        tags: Optional[list[str]],
        offset: int,
        limit: int
    ) -> tuple[list[VideoResult], int]:
        """
        Поиск видео с фильтрацией по тексту и тегам.
        
        - query: поиск по title/description (ILIKE, регистронезависимый)
        - tags: фильтрация по массиву тегов (логическое ИЛИ через ARRAY overlap)
        """
        # Основной запрос
        stmt = select(Video).where(Video.status == VideoStatus.READY)
        
        # Фильтр по тексту — только если query передан и не пустой
        if query:
            stmt = stmt.where(
                or_(
                    Video.title.ilike(f"%{query}%"),
                    Video.description.ilike(f"%{query}%")
                )
            )
        
        # Фильтр по тегам — только если tags переданы
        if tags:
            # PostgreSQL ARRAY overlap: video.tags && %tags%
            stmt = stmt.where(Video.tags.overlap(tags))
        
        # Пагинация
        stmt = stmt.order_by(Video.created_at.desc()).offset(offset).limit(limit)
        
        # Выполняем запрос
        result = await self.session.execute(stmt)
        videos = result.scalars().all()
        
        # Подсчёт общего количества (для пагинации) — с теми же фильтрами
        count_stmt = select(func.count(Video.id)).where(Video.status == VideoStatus.READY)
        
        if query:
            count_stmt = count_stmt.where(
                or_(
                    Video.title.ilike(f"%{query}%"),
                    Video.description.ilike(f"%{query}%")
                )
            )
        if tags:
            count_stmt = count_stmt.where(Video.tags.overlap(tags))
        
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Маппинг в DTO
        items = [
            VideoResult(
                id=str(v.id),
                title=v.title,
                thumbnail_url=v.thumbnail_url,
                duration=v.duration,
                tags=v.tags or []
            )
            for v in videos
        ]
        
        return items, total