from uuid import UUID

from ..domain.exceptions import UserNotFoundError
from ..infrastructure.repositories import RoleRepositoryImpl, UserRepositoryImpl


class GetUserRolesService:
    def __init__(
        self,
        user_repo: UserRepositoryImpl,
        role_repo: RoleRepositoryImpl,
    ) -> None:
        self._user_repo = user_repo
        self._role_repo = role_repo

    async def execute(self, user_id: UUID) -> list[str]:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))

        return await self._role_repo.get_roles_by_user_id(user_id)
