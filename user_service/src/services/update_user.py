from typing import Optional
from uuid import UUID

from ..domain.entities import User
from ..domain.interfaces import UnitOfWork, UserRepository
from ._helpers import hash_password, validate_email, validate_password, validate_username


class UpdateUserService:
    def __init__(self, repository: UserRepository, uow: UnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def execute(
        self,
        user_id: UUID,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        status: Optional[str] = None,
    ) -> User:
        user = await self._repository.get_by_id(user_id)

        if username is not None:
            validate_username(username)
            user.username = username

        if email is not None:
            validate_email(email)
            user.email = email

        if password is not None:
            validate_password(password)
            user.hashed_password = hash_password(password)

        if status is not None:
            user.status = status

        updated = await self._repository.update(user)
        await self._uow.commit()
        return updated
