from uuid import UUID

from ..domain.exceptions import UserNotFoundError
from ..infrastructure.database.uow import UnitOfWorkImpl
from ..infrastructure.repositories import RoleRepositoryImpl, UserRepositoryImpl


class AssignRoleService:
    def __init__(
        self,
        user_repo: UserRepositoryImpl,
        role_repo: RoleRepositoryImpl,
        uow: UnitOfWorkImpl,
    ) -> None:
        self._user_repo = user_repo
        self._role_repo = role_repo
        self._uow = uow

    async def execute(self, user_id: UUID, role: str, assigned_by: UUID | None = None) -> list[str]:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))

        await self._role_repo.assign_role(user_id, role, assigned_by)
        await self._uow.commit()

        return await self._role_repo.get_roles_by_user_id(user_id)
