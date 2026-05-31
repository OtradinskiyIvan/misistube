from typing import Optional
from uuid import UUID

from ..infrastructure.database.uow import UnitOfWorkImpl
from ..infrastructure.repositories.comment_repository import CommentRepositoryImpl


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
        return {
            "id": comment.id,
            "user_id": comment.user_id,
            "video_id": comment.video_id,
            "parent_id": comment.parent_id,
            "content": comment.content,
            "is_edited": comment.is_edited,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
        }

    async def get_video_comments(self, video_id: UUID, skip: int = 0, limit: int = 50) -> list[dict]:
        comments = await self._comment_repo.get_by_video(video_id, skip=skip, limit=limit)
        return [
            {
                "id": c.id,
                "user_id": c.user_id,
                "video_id": c.video_id,
                "parent_id": c.parent_id,
                "content": c.content,
                "is_edited": c.is_edited,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in comments
        ]

    async def get_video_comments_count(self, video_id: UUID) -> int:
        return await self._comment_repo.count_by_video(video_id)

    async def update_comment(self, comment_id: UUID, user_id: UUID, content: str) -> Optional[dict]:
        comment = await self._comment_repo.get_by_id(comment_id)
        if comment is None or comment.user_id != user_id:
            return None

        updated = await self._comment_repo.update_content(comment_id, content)
        await self._uow.commit()
        if updated is None:
            return None
        return {
            "id": updated.id,
            "user_id": updated.user_id,
            "video_id": updated.video_id,
            "parent_id": updated.parent_id,
            "content": updated.content,
            "is_edited": updated.is_edited,
            "created_at": updated.created_at,
            "updated_at": updated.updated_at,
        }

    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        comment = await self._comment_repo.get_by_id(comment_id)
        if comment is None or comment.user_id != user_id:
            return False

        deleted = await self._comment_repo.delete(comment_id)
        if deleted:
            await self._uow.commit()
        return deleted
