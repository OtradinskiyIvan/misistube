from datetime import datetime
from typing import Optional
from uuid import UUID


class User:
    def __init__(
        self,
        id: UUID,
        username: str,
        email: str,
        hashed_password: str,
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email})"
