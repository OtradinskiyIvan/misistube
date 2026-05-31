from typing import Optional
from uuid import UUID

from ..domain.entities import User
from ..domain.interfaces import UserRepository


class GetUserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def by_id(self, user_id: UUID) -> User:
        return await self._repository.get_by_id(user_id)

    async def by_username(self, username: str) -> Optional[User]:
        return await self._repository.get_by_username(username)

    async def by_email(self, email: str) -> Optional[User]:
        return await self._repository.get_by_email(email)

    async def all(self, skip: int = 0, limit: int = 100) -> list[User]:
        if limit > 1000:
            limit = 1000
        if skip < 0:
            skip = 0
        return await self._repository.get_all(skip=skip, limit=limit)
