from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from src.infrastructure.search.protocol import SearchPort
from src.api.schemas import VideoResult
from src.infrastructure.database.models import Video, VideoStatus  # ваша ORM-модель

class SQLAlchemyVideoRepository(SearchPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[VideoResult], int]:
        base_filter = Video.status == VideoStatus.READY
        
        # Фильтр по тексту (ILIKE)
        text_filter = or_(
            Video.title.ilike(f"%{query}%"),
            Video.description.ilike(f"%{query}%")
        ) if query else None
        
        # Фильтр по тегам (ARRAY overlap)
        tags_filter = Video.tags.bool_op('&&')(tags) if tags else None
        
        # Собираем WHERE
        filters = [base_filter]
        if text_filter is not None:
            filters.append(text_filter)
        if tags_filter is not None:
            filters.append(tags_filter)
        
        # Запрос данных
        stmt = select(Video).where(*filters).offset(offset).limit(limit)
        count_stmt = select(func.count()).select_from(Video).where(*filters)
        
        videos = (await self.session.execute(stmt)).scalars().all()
        total = (await self.session.execute(count_stmt)).scalar() or 0
        

        results = [
            VideoResult(
                id=str(v.id),
                title=v.title,
                duration=v.duration,
                tags=v.tags or []
            )
            for v in videos
        ]
        return results, total