from uuid import UUID

from ..domain.interfaces import UnitOfWork, UserRepository


class DeleteUserService:
    def __init__(self, repository: UserRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, user_id: UUID) -> bool:
        result = await self._repository.delete(user_id)
        await self._uow.commit()
        return result
