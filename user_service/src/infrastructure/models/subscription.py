import uuid
from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.manager import Base


class UserSubscriptionModel(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    follower_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
    )
    following_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
    )
    subscribed_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="unique_subscription"),
        CheckConstraint("follower_id != following_id", name="no_self_subscription"),
    )

    follower: Mapped["UserModel"] = relationship(
        foreign_keys=[follower_id], back_populates="subscriptions_as_follower",
    )
    following: Mapped["UserModel"] = relationship(
        foreign_keys=[following_id], back_populates="subscriptions_as_following",
    )

    def __repr__(self) -> str:
        return f"<UserSubscriptionModel(follower={self.follower_id}, following={self.following_id})>"
