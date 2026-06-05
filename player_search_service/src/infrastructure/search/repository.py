from typing import Optional
from sqlalchemy import select, func, or_, cast, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

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
        tags: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 20
    ) -> tuple[list[VideoResult], int]:
        """
        Поиск видео с фильтрацией по тексту и тегам.
        """
        stmt = select(Video).where(Video.status == VideoStatus.READY)   # UPLOADING можно заменить для тестов
        
        if query:
            stmt = stmt.where(
                or_(
                    Video.title.ilike(f"%{query}%"),
                    Video.description.ilike(f"%{query}%")
                )
            )
        
        # if tags:
        #    tags_list = tags if isinstance(tags, list) else [tags]
        #    stmt = stmt.where(Video.tags.op('&&')(cast(tags_list, ARRAY(String))))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        data_stmt = stmt.order_by(Video.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(data_stmt)
        videos = result.scalars().all()
        
        # 4. МАППИНГ В DTO
        items = [
            VideoResult(
                id=str(v.id),
                title=v.title,
                description=v.description,       
                storage_key=v.storage_key,          
                status=v.status.value if hasattr(v.status, 'value') else str(v.status), 
                duration_seconds=v.duration_seconds,
                created_at=v.created_at.isoformat() if v.created_at else None, 
                updated_at=v.updated_at.isoformat() if v.updated_at else None, 
                
                # Безопасное получение отсутствующих полей
                tags=getattr(v, 'tags', None),       
                thumbnail_url=getattr(v, 'thumbnail_url', None)
            )
            for v in videos
        ]
        
        return items, total
    
    async def get_by_id(self, video_id: str) -> Optional[Video]:
        """Получить видео по ID"""
        from sqlalchemy import select
        
        try:
            video_uuid = uuid.UUID(video_id)
        except ValueError:
            return None
        
        stmt = select(Video).where(Video.id == video_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()