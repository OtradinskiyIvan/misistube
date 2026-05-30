from uuid import uuid4

from ..domain.entities import User
from ..domain.interfaces import UnitOfWork, UserRepository
from ._helpers import hash_password, validate_email, validate_password, validate_username


class CreateUserService:
    def __init__(self, repository: UserRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        validate_username(username)
        validate_email(email)
        validate_password(password)

        user = User(
            id=uuid4(),
            username=username,
            email=email,
            hashed_password=hash_password(password),
            status="active",
        )

        created = await self._repository.create(user)
        await self._uow.commit()
        return created
