import sys
from enum import Enum
from pathlib import Path

from sqlalchemy import Column, DateTime, Integer, String, Text, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.database.session import Base


class VideoStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    storage_key = Column(String(500), nullable=False)

    status = Column(
        SQLEnum(
            VideoStatus,
            name="video_status",
            native_enum=True,
            values_callable=lambda x: [e.value for e in x],
            create_type=False
        ),
        nullable=False,
        server_default=text("'uploading'::video_status")
    )
    duration_seconds = Column(Integer, nullable=True, server_default=text("0"))

    user_id = Column(UUID(as_uuid=True), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))

    # tags = deferred(Column(ARRAY(String), nullable=True, server_default=text("'{}'")))  - нет в БД creation service
    # thumbnail_url = deferred(Column(String(500), nullable=True))
