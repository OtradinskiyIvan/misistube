from typing import Optional
from uuid import UUID

from ..domain.entities import User
from ..domain.interfaces import UserRepository
from ..infrastructure.repositories import RoleRepositoryImpl


class GetUserService:
    def __init__(
        self,
        repository: UserRepository,
        role_repo: Optional[RoleRepositoryImpl] = None,
    ) -> None:
        self._repository = repository
        self._role_repo = role_repo

    async def by_id(self, user_id: UUID) -> User:
        return await self._repository.get_by_id(user_id)

    async def by_username(self, username: str) -> Optional[User]:
        return await self._repository.get_by_username(username)

    async def by_email(self, email: str) -> Optional[User]:
        return await self._repository.get_by_email(email)

    async def search_by_username(self, query: str, skip: int = 0, limit: int = 100) -> list[User]:
        if limit > 1000:
            limit = 1000
        if skip < 0:
            skip = 0
        return await self._repository.search_by_username(query, skip, limit)

    async def all(self, skip: int = 0, limit: int = 100) -> list[User]:
        if limit > 1000:
            limit = 1000
        if skip < 0:
            skip = 0
        return await self._repository.get_all(skip=skip, limit=limit)

    async def all_with_roles(self, skip: int = 0, limit: int = 100) -> list[dict]:
        users = await self.all(skip=skip, limit=limit)
        if self._role_repo is None:
            return [{"id": u.id, "username": u.username, "email": u.email, "status": u.status, "roles": [], "created_at": u.created_at, "updated_at": u.updated_at} for u in users]
        result = []
        for user in users:
            roles = await self._role_repo.get_roles_by_user_id(user.id)
            result.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "status": user.status,
                "roles": roles,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            })
        return result
