import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.manager import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    profile: Mapped[Optional["UserProfileModel"]] = relationship(
        back_populates="user", uselist=False,
    )
    roles: Mapped[list["UserRoleModel"]] = relationship(
        back_populates="user", foreign_keys="UserRoleModel.user_id",
    )
    preferences: Mapped[Optional["UserPreferenceModel"]] = relationship(
        back_populates="user", uselist=False,
    )
    statistics: Mapped[Optional["UserStatisticModel"]] = relationship(
        back_populates="user", uselist=False,
    )
    subscriptions_as_follower: Mapped[list["UserSubscriptionModel"]] = relationship(
        back_populates="follower", foreign_keys="UserSubscriptionModel.follower_id",
    )
    subscriptions_as_following: Mapped[list["UserSubscriptionModel"]] = relationship(
        back_populates="following", foreign_keys="UserSubscriptionModel.following_id",
    )

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username={self.username}, email={self.email})>"
