from typing import Protocol, List, Tuple, Optional
from src.api.schemas import VideoResult

class SearchPort(Protocol):
    """Контракт поиска видео. UseCase зависит только от него."""
    async def search(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[VideoResult], int]:
        """Возвращает (список результатов, общее количество)"""
        ...