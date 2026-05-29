from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class User:
    id: UUID
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def deactivate(self) -> "User":
        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.now()
        )
