import time
from uuid import UUID

from ..domain.interfaces import UnitOfWork, UserRepository


class DeactivateUserService:
    def __init__(self, repository: UserRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, user_id: UUID) -> bool:
        user = await self._repository.get_by_id(user_id)
        ts = int(time.time())
        user.username = f"{user.username}_deleted_{ts}"
        user.email = f"deleted_{ts}@deleted.local"
        user.status = "inactive"
        await self._repository.update(user)
        await self._uow.commit()
        return True
