from datetime import datetime

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    q: str | None = Field(None, max_length=255, description="Поисковый запрос")
    tags: list[str] | None = Field(default=None, description="Фильтр по тегам")
    offset: int = Field(default=0, ge=0, description="Смещение")
    limit: int = Field(default=20, ge=1, le=100, description="Лимит результатов")


class VideoResult(BaseModel):
    """Результат поиска"""

    id: str
    title: str
    description: str | None = None
    storage_key: str
    status: str
    duration_seconds: int
    thumbnail_key: str | None = None
    thumbnail_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    user_id: str
    username: str

    tags: list[str] | None = None


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
    detail: str | None = None
