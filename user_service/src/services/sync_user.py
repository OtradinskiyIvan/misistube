from uuid import UUID

from ..domain.entities import User
from ..domain.interfaces import UnitOfWork, UserRepository


class SyncUserService:
    def __init__(self, repository: UserRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, user_id: UUID, username: str, email: str) -> User:
        user = await self._repository.get_by_id(user_id)
        user.username = username
        user.email = email
        updated = await self._repository.update(user)
        await self._uow.commit()
        return updated
