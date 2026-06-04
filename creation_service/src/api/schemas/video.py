# api/schemas/video.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.domain.entities.video import VideoStatus

class VideoCreateRequest(BaseModel):
    title: str
    description: str

class VideoUploadResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: VideoStatus
    duration: int
    created_at: datetime
    updated_at: datetime

class VideoDetailResponse(VideoUploadResponse):
    storage_url: str

class VideoListResponse(BaseModel):
    items: list[VideoUploadResponse]
    total: int