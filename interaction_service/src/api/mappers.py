from .schemas import CommentResponse


def map_comment_to_response(comment: dict) -> CommentResponse:
    return CommentResponse(
        id=comment["id"],
        user_id=comment["user_id"],
        video_id=comment["video_id"],
        parent_id=comment.get("parent_id"),
        content=comment["content"],
        is_edited=comment["is_edited"],
        created_at=comment["created_at"],
        updated_at=comment["updated_at"],
    )
