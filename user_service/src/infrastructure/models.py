"""SQLAlchemy models for User Service."""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, UUID as SQLA_UUID
from sqlalchemy.orm import DeclarativeBase

from shared.database.session import Base


class UserModel(Base):
    """SQLAlchemy User model."""

    __tablename__ = "users"

    id = Column(SQLA_UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username={self.username}, email={self.email})>"
