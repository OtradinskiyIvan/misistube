from typing import Optional
from uuid import UUID

from ..infrastructure.clients.creation_service_client import CreationServiceClient
from ..infrastructure.clients.user_service_client import UserServiceClient
from ..infrastructure.database.uow import UnitOfWorkImpl
from ..infrastructure.repositories.view_repository import ViewRepositoryImpl


class ViewService:
    def __init__(
        self,
        view_repo: ViewRepositoryImpl,
        uow: UnitOfWorkImpl,
        creation_client: CreationServiceClient,
        user_client: UserServiceClient,
    ) -> None:
        self._view_repo = view_repo
        self._uow = uow
        self._creation_client = creation_client
        self._user_client = user_client

    async def record_view(self, user_id: UUID, video_id: UUID) -> Optional[UUID]:
        owner_id = await self._creation_client.get_video_owner(video_id)
        if owner_id is None:
            return None

        await self._view_repo.add(user_id, video_id)
        await self._uow.commit()

        await self._user_client.increment_stat(owner_id, "total_views", 1)
        return owner_id
