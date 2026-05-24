# api/schemas/video.py
from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime
from enum import Enum

class VideoStatusEnum(str, Enum):
    uploading = "uploading"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class VideoCreateRequest(BaseModel):
    title: str
    description: str

class VideoUploadResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: VideoStatusEnum
    created_at: datetime

class VideoDetailResponse(VideoUploadResponse):
    storage_url: HttpUrl  # presigned URL для доступа к файлу

class VideoListResponse(BaseModel):
    items: list[VideoUploadResponse]
    total: int