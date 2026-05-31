from uuid import UUID

from ..domain.entities import User
from ..domain.exceptions import UserNotFoundError
from ..domain.interfaces import UnitOfWork, UserRepository


class SyncUserService:
    def __init__(self, repository: UserRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(self, user_id: UUID, username: str, email: str) -> User:
        try:
            user = await self._repository.get_by_id(user_id)
            user.username = username
            user.email = email
            updated = await self._repository.update(user)
        except UserNotFoundError:
            user = User(
                id=user_id,
                username=username,
                email=email,
                status="active",
            )
            updated = await self._repository.create(user)

        await self._uow.commit()
        return updated
