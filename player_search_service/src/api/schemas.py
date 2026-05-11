from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=200, description="Поисковый запрос")
    tags: Optional[list[str]] = Field(default=None, description="Фильтр по тегам")
    offset: int = Field(default=0, ge=0, description="Смещение")
    limit: int = Field(default=20, ge=1, le=100, description="Лимит результатов")

class VideoResult(BaseModel):
    """Результат поиска"""
    id: str
    title: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    tags: Optional[list[str]] = None

class SearchResponse(BaseModel):
    items: list[VideoResult]
    total: int
    offset: int
    limit: int

class PlaybackUrl(BaseModel):
    """Ссылка для воспроизведения"""
    hls_master_url: str
    expires_at: datetime

class ErrorDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: Optional[str] = None