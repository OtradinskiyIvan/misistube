from typing import Protocol
from src.infrastructure.database.models import Video

from src.api.schemas import VideoResult


class SearchPort(Protocol):
    """Контракт поиска видео. UseCase зависит только от него."""
    async def search(
        self,
        query: str,
        tags: list[str] | None = None,
        offset: int = 0,
        limit: int = 20
    ) -> tuple[list[VideoResult], int]:
        """Возвращает (список результатов, общее количество)"""
        ...

    async def get_by_id(self, video_id: str) -> Optional[Video]:
        """Получить видео по ID"""
        from sqlalchemy import select
        stmt = select(Video).where(Video.id == video_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()