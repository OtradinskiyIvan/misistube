from typing import Protocol

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
