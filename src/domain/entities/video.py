# domain/entities/video.py
from dataclasses import dataclass
from datetime import datetime
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
    storage_key: str      # путь в S3 (например, "videos/uuid.mp4")
    status: VideoStatus
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(title: str, description: str, storage_key: str) -> "Video":
        now = datetime.utcnow()
        return Video(
            id=uuid4(),
            title=title,
            description=description,
            storage_key=storage_key,
            status=VideoStatus.UPLOADING,
            created_at=now,
            updated_at=now,
        )