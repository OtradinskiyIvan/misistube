# infrastructure/database/models.py
from sqlalchemy import String, Enum, DateTime, Integer, Uuid, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID, uuid4
from datetime import datetime, timezone
from src.domain.entities.video import VideoStatus

class Base(DeclarativeBase):
    pass

class VideoModel(Base):
    __tablename__ = "videos"

    __table_args__ = (
        Index("idx_videos_created_at", "created_at"),
        Index("idx_videos_user_id", "user_id"),
        Index("idx_videos_status", "status"),
        Index("idx_videos_storage_key", "storage_key"),
        {"comment": "Хранит метаданные видео и ссылки на файлы в S3"},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, comment="Уникальный идентификатор видео")
    user_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, comment="UUID пользователя, загрузившего видео")
    title: Mapped[str] = mapped_column(String(255), comment="Название видео")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, comment="Длительность в секундах")
    description: Mapped[str] = mapped_column(String(1000), default="", comment="Описание видео")
    storage_key: Mapped[str] = mapped_column(String(500), comment="Ключ объекта в S3 (путь к файлу)")
    status: Mapped[VideoStatus] = mapped_column(
        Enum("uploading", "processing", "ready", "failed", "deleted", name="video_status", create_type=True, create_constraint=True),
        comment="Текущий статус обработки видео",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        comment="Дата и время создания записи",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        comment="Дата и время последнего обновления",
    )
