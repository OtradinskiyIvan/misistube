# infrastructure/database/models.py
from sqlalchemy import String, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, Enum, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class VideoModel(Base):
    __tablename__ = "videos"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)   
    description: Mapped[str] = mapped_column(String(1000))
    storage_key: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(Enum("uploading","processing","ready","failed"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)