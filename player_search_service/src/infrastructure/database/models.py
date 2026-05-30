import enum
import uuid
from datetime import datetime

from shared.database.session import Base
from sqlalchemy import ARRAY, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class VideoStatus(str, enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class Video(Base):
    __tablename__ = "videos"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus), default=VideoStatus.PROCESSING)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
