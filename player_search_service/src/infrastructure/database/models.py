import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, DateTime, ARRAY, Enum as SQLEnum, text
from sqlalchemy.dialects.postgresql import UUID

import sys
from pathlib import Path
ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.database.session import Base

class VideoStatus(str, Enum):
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    storage_key = Column(String(500), nullable=False)
    
    status = Column(
        SQLEnum(
            VideoStatus,
            name="videostatus",         
            native_enum=True,             
            values_callable=lambda x: [e.value for e in x], 
            create_type=False             
        ),
        nullable=False,
        server_default=text("'UPLOADING'")
    )
    
    tags = Column(ARRAY(String), nullable=True, server_default=text("'{}'"))
    duration = Column(Integer, nullable=True, server_default=text("0"))
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))