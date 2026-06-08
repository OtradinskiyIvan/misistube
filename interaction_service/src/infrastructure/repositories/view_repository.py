from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.view import ViewModel


class ViewRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_id: UUID, video_id: UUID) -> ViewModel:
        return await self._session.run_sync(
            lambda sync_session: self._add_sync(sync_session, user_id, video_id)
        )

    def _add_sync(self, sync_session, user_id: UUID, video_id: UUID) -> ViewModel:
        model = ViewModel(user_id=user_id, video_id=video_id)
        sync_session.add(model)
        sync_session.flush()
        return model
