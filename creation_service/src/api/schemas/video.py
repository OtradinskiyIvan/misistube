# api/schemas/video.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.domain.entities.video import VideoStatus

class VideoCreateRequest(BaseModel):
    title: str
    description: str = ""
    user_id: UUID

class VideoUploadResponse(BaseModel):
    id: UUID
    title: str
    description: str = ""
    status: VideoStatus
    duration: int
    thumbnail_url: str | None = None
    user_id: UUID
    created_at: datetime
    updated_at: datetime

class VideoDetailResponse(VideoUploadResponse):
    storage_url: str

class VideoStatusUpdate(BaseModel):
    status: VideoStatus

class VideoListResponse(BaseModel):
    items: list[VideoUploadResponse]
    total: int