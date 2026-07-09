from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.manager import Base


class UserStatisticModel(Base):
    __tablename__ = "user_statistics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    total_videos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_views: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_subscribers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_likes_received: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_comments_received: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    user: Mapped[UserModel] = relationship(back_populates="statistics")

    def __repr__(self) -> str:
        return f"<UserStatisticModel(id={self.id}, user_id={self.user_id})>"
