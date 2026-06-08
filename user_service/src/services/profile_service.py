import re
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..infrastructure.models.profile import UserProfileModel
from ..infrastructure.storage.s3_client import S3Client

_EXT_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}


class ProfileService:
    def __init__(self, session: AsyncSession, s3: S3Client) -> None:
        self._session = session
        self._s3 = s3

    async def get_profile(self, user_id: UUID) -> UserProfileModel | None:
        return await self._session.run_sync(
            lambda sync_session: self._get_profile_sync(sync_session, user_id)
        )

    async def update_profile(self, user_id: UUID, bio: str | None = None, location: str | None = None) -> UserProfileModel:
        return await self._session.run_sync(
            lambda sync_session: self._update_profile_sync(sync_session, user_id, bio, location)
        )

    async def upload_avatar(self, user_id: UUID, data: bytes, content_type: str) -> str:
        ext = _EXT_MAP.get(content_type, "jpg")
        key = f"avatars/{user_id}_{uuid4()}.{ext}"

        public_url = await self._s3.upload_file(key, data, content_type)

        await self._session.run_sync(
            lambda sync_session: self._set_avatar_url_sync(sync_session, user_id, public_url)
        )

        return public_url

    async def delete_avatar(self, user_id: UUID) -> None:
        old_url = await self._session.run_sync(
            lambda sync_session: self._get_avatar_url_sync(sync_session, user_id)
        )

        if old_url:
            key = self._extract_key(old_url)
            if key:
                await self._s3.delete_file(key)

        await self._session.run_sync(
            lambda sync_session: self._set_avatar_url_sync(sync_session, user_id, None)
        )

    def _get_profile_sync(self, sync_session, user_id: UUID) -> UserProfileModel | None:
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        return sync_session.scalar(stmt)

    def _update_profile_sync(self, sync_session, user_id: UUID, bio: str | None, location: str | None) -> UserProfileModel:
        values = {"updated_at": func.now()}
        if bio is not None:
            values["bio"] = bio
        if location is not None:
            values["location"] = location

        stmt = pg_insert(UserProfileModel).values(
            id=uuid4(), user_id=user_id,
        ).on_conflict_do_update(
            index_elements=["user_id"],
            set_=values,
        )
        sync_session.execute(stmt)
        sync_session.commit()

        return self._get_profile_sync(sync_session, user_id)

    def _set_avatar_url_sync(self, sync_session, user_id: UUID, url: str | None) -> None:
        stmt = pg_insert(UserProfileModel).values(
            id=uuid4(), user_id=user_id, avatar_url=url,
        ).on_conflict_do_update(
            index_elements=["user_id"],
            set_={"avatar_url": url, "updated_at": func.now()},
        )
        sync_session.execute(stmt)
        sync_session.commit()

    def _get_avatar_url_sync(self, sync_session, user_id: UUID) -> str | None:
        stmt = select(UserProfileModel.avatar_url).where(UserProfileModel.user_id == user_id)
        row = sync_session.execute(stmt).one_or_none()
        return row[0] if row else None

    @staticmethod
    def _extract_key(url: str) -> str | None:
        m = re.search(r"/avatars/[^?]+", url)
        return m.group(0).lstrip("/") if m else None
