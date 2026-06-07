import uuid
from datetime import datetime

from sqlalchemy import DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database.manager import Base


class LikeModel(Base):
    __tablename__ = "likes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True,
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="unique_user_video_like"),
    )

    def __repr__(self) -> str:
        return f"<LikeModel(user_id={self.user_id}, video_id={self.video_id})>"
