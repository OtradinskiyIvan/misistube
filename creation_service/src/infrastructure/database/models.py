# infrastructure/database/models.py
from sqlalchemy import String, Enum, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID, uuid4
from datetime import datetime, timezone
from src.domain.entities.video import VideoStatus

class Base(DeclarativeBase):
    pass

class VideoModel(Base):
    __tablename__ = "videos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(String(1000))
    storage_key: Mapped[str] = mapped_column(String(500))
    status: Mapped[VideoStatus] = mapped_column(
        Enum("uploading", "processing", "ready", "failed", name="video_status", create_constraint=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )