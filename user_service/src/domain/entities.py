"""Domain entities for User Service."""
from datetime import datetime
from typing import Optional
from uuid import UUID


class User:
    """Domain User entity."""

    def __init__(
        self,
        id: UUID,
        username: str,
        email: str,
        display_name: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.display_name = display_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email})"
