from typing import Optional
from uuid import UUID

from ..infrastructure.database.uow import UnitOfWorkImpl
from ..infrastructure.repositories.comment_repository import CommentRepositoryImpl


def _to_dict(c) -> dict:
    return {
        "id": c.id,
        "user_id": c.user_id,
        "video_id": c.video_id,
        "parent_id": c.parent_id,
        "content": c.content,
        "is_edited": c.is_edited,
        "is_blocked": c.is_blocked,
        "blocked_by": c.blocked_by,
        "blocked_at": c.blocked_at,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
    }


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepositoryImpl,
        uow: UnitOfWorkImpl,
    ) -> None:
        self._comment_repo = comment_repo
        self._uow = uow

    async def create_comment(
        self,
        user_id: UUID,
        video_id: UUID,
        content: str,
        parent_id: Optional[UUID] = None,
    ) -> dict:
        comment = await self._comment_repo.create(user_id, video_id, content, parent_id)
        await self._uow.commit()
        return _to_dict(comment)

    async def get_comment(self, comment_id: UUID) -> Optional[dict]:
        comment = await self._comment_repo.get_by_id(comment_id)
        if comment is None:
            return None
        return _to_dict(comment)

    async def get_video_comments(
        self,
        video_id: UUID,
        skip: int = 0,
        limit: int = 50,
        include_blocked: bool = False,
    ) -> list[dict]:
        comments = await self._comment_repo.get_by_video(
            video_id, skip=skip, limit=limit, include_blocked=include_blocked,
        )
        return [_to_dict(c) for c in comments]

    async def get_video_comments_count(self, video_id: UUID, include_blocked: bool = False) -> int:
        return await self._comment_repo.count_by_video(video_id, include_blocked=include_blocked)

    async def update_comment(self, comment_id: UUID, user_id: UUID, content: str) -> Optional[dict]:
        comment = await self._comment_repo.get_by_id(comment_id)
        if comment is None or comment.user_id != user_id:
            return None

        updated = await self._comment_repo.update_content(comment_id, content)
        await self._uow.commit()
        if updated is None:
            return None
        return _to_dict(updated)

    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        comment = await self._comment_repo.get_by_id(comment_id)
        if comment is None or comment.user_id != user_id:
            return False

        deleted = await self._comment_repo.delete(comment_id)
        if deleted:
            await self._uow.commit()
        return deleted

    async def block_comment(self, comment_id: UUID, blocked_by: UUID) -> Optional[dict]:
        comment = await self._comment_repo.block(comment_id, blocked_by)
        if comment is None:
            return None
        await self._uow.commit()
        return _to_dict(comment)

    async def unblock_comment(self, comment_id: UUID) -> Optional[dict]:
        comment = await self._comment_repo.unblock(comment_id)
        if comment is None:
            return None
        await self._uow.commit()
        return _to_dict(comment)

    async def get_blocked_comments(self, skip: int = 0, limit: int = 50) -> list[dict]:
        comments = await self._comment_repo.get_blocked(skip=skip, limit=limit)
        return [_to_dict(c) for c in comments]

    async def delete_comment_as_admin(self, comment_id: UUID) -> bool:
        deleted = await self._comment_repo.delete(comment_id)
        if deleted:
            await self._uow.commit()
        return deleted
