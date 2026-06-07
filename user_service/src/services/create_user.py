from uuid import uuid4

from ..domain.entities import User
from ..domain.interfaces import UnitOfWork, UserRepository


class CreateUserService:
    def __init__(self, repository: UserRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(
        self,
        username: str,
        email: str,
    ) -> User:
        user = User(
            id=uuid4(),
            username=username,
            email=email,
            status="active",
        )

        created = await self._repository.create(user)
        await self._uow.commit()
        return created
