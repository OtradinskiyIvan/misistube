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

@dataclass
class Video:
    id: UUID
    title: str
    description: str
    storage_key: str
    status: VideoStatus
    duration: int
    user_id: UUID | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(title: str, description: str, storage_key: str, duration: int, user_id: UUID | None = None) -> "Video":
        now = datetime.now(timezone.utc)
        return Video(
            id=uuid4(),
            title=title,
            description=description,
            storage_key=storage_key,
            status=VideoStatus.UPLOADING,
            duration=duration,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )