import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.manager import Base


class UserPreferenceModel(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False,
    )
    is_profile_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notification_email: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_subscriber_count: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    user: Mapped["UserModel"] = relationship(back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreferenceModel(id={self.id}, user_id={self.user_id})>"
