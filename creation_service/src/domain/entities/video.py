# domain/entities/video.py
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

class VideoStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"

@dataclass
class Video:
    id: UUID
    title: str
    storage_key: str
    status: VideoStatus
    duration: int
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    description: str = ""
    thumbnail_key: str | None = None
    
    @staticmethod
    def create(title: str, storage_key: str, duration: int, user_id: UUID, description: str = "", thumbnail_key: str | None = None) -> "Video":
        now = datetime.now(timezone.utc)
        return Video(
            id=uuid4(),
            title=title,
            description=description,
            thumbnail_key=thumbnail_key,
            storage_key=storage_key,
            status=VideoStatus.UPLOADING,
            duration=duration,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )