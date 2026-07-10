from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.manager import Base


class UserRoleModel(Base):
    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), nullable=False,
    )
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "role", name="unique_user_role"),
    )

    user: Mapped[UserModel] = relationship(
        back_populates="roles", foreign_keys=[user_id],
    )
    assigner: Mapped[UserModel | None] = relationship(
        foreign_keys=[assigned_by],
    )

    def __repr__(self) -> str:
        return f"<UserRoleModel(id={self.id}, user_id={self.user_id}, role={self.role})>"
