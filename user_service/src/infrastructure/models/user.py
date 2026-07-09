from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
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

    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    profile: Mapped[UserProfileModel | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete",
    )
    roles: Mapped[list[UserRoleModel]] = relationship(
        back_populates="user", foreign_keys="UserRoleModel.user_id", cascade="all, delete",
    )
    preferences: Mapped[UserPreferenceModel | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete",
    )
    statistics: Mapped[UserStatisticModel | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete",
    )
    subscriptions_as_follower: Mapped[list[UserSubscriptionModel]] = relationship(
        back_populates="follower", foreign_keys="UserSubscriptionModel.follower_id", cascade="all, delete",
    )
    subscriptions_as_following: Mapped[list[UserSubscriptionModel]] = relationship(
        back_populates="following", foreign_keys="UserSubscriptionModel.following_id", cascade="all, delete",
    )

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username={self.username}, email={self.email})>"
