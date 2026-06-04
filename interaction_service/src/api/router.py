from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from .mappers import map_comment_to_response
from .schemas import (
    AdminActionResponse,
    AdminCommentActionResponse,
    CommentCreateRequest,
    CommentResponse,
    CommentUpdateRequest,
    ErrorResponse,
    HealthResponse,
    LikedVideosResponse,
    LikeCountResponse,
    LikeRequest,
    LikeResponse,
    PaginatedCommentsResponse,
)
from ..deps import (
    get_comment_service,
    get_current_user_id,
    get_like_service,
    get_logger_dep,
    get_settings,
    get_user_service_client,
    require_admin,
)
from ..infrastructure.clients.user_service_client import UserServiceClient
from ..services.comment_service import CommentService
from ..services.like_service import LikeService


router = APIRouter(tags=["interactions"])

_error_responses = {
    400: {"model": ErrorResponse, "description": "Validation error"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    404: {"model": ErrorResponse, "description": "Resource not found"},
    422: {"model": ErrorResponse, "description": "Request validation error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
}


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
)
async def health_check(
    logger=Depends(get_logger_dep),
    s=Depends(get_settings),
):
    logger.info("health_check.requested")
    return HealthResponse(
        status="ok",
        service=s.APP_NAME,
        version=s.SERVICE_VERSION,
    )


@router.post(
    "/likes",
    response_model=LikeResponse,
    status_code=201,
    summary="Like a video",
    responses={**_error_responses},
)
async def like_video(
    body: LikeRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: LikeService = Depends(get_like_service),
    logger=Depends(get_logger_dep),
):
    logger.info("likes.create.requested", extra={"user_id": str(user_id), "video_id": str(body.video_id)})
    liked = await service.like(user_id, body.video_id)
    return LikeResponse(liked=liked)


@router.delete(
    "/likes/video/{video_id}",
    status_code=204,
    summary="Unlike a video",
    responses={**_error_responses},
)
async def unlike_video(
    video_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: LikeService = Depends(get_like_service),
    logger=Depends(get_logger_dep),
):
    logger.info("likes.delete.requested", extra={"user_id": str(user_id), "video_id": str(video_id)})
    removed = await service.unlike(user_id, video_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Like not found")
    return None


@router.get(
    "/likes/video/{video_id}",
    response_model=LikeResponse,
    summary="Check if user liked the video",
    responses={**_error_responses},
)
async def is_liked(
    video_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: LikeService = Depends(get_like_service),
    logger=Depends(get_logger_dep),
):
    logger.info("likes.check.requested", extra={"user_id": str(user_id), "video_id": str(video_id)})
    liked = await service.is_liked(user_id, video_id)
    return LikeResponse(liked=liked)


@router.get(
    "/likes/video/{video_id}/count",
    response_model=LikeCountResponse,
    summary="Get likes count for a video",
    responses={**_error_responses},
)
async def likes_count(
    video_id: UUID,
    service: LikeService = Depends(get_like_service),
    logger=Depends(get_logger_dep),
):
    logger.info("likes.count.requested", extra={"video_id": str(video_id)})
    count = await service.get_video_likes_count(video_id)
    return LikeCountResponse(video_id=video_id, count=count)


@router.post(
    "/comments",
    response_model=CommentResponse,
    status_code=201,
    summary="Create a comment",
    responses={**_error_responses},
)
async def create_comment(
    body: CommentCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
):
    logger.info("comments.create.requested", extra={"user_id": str(user_id), "video_id": str(body.video_id)})
    comment = await service.create_comment(
        user_id=user_id,
        video_id=body.video_id,
        content=body.content,
        parent_id=body.parent_id,
    )
    return map_comment_to_response(comment)


@router.get(
    "/comments/video/{video_id}",
    response_model=PaginatedCommentsResponse,
    summary="Get comments for a video",
    responses={**_error_responses},
)
async def get_video_comments(
    video_id: UUID,
    skip: int = Query(0, ge=0, description="Number to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max comments"),
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
):
    logger.info("comments.list.requested", extra={"video_id": str(video_id), "skip": skip, "limit": limit})
    comments = await service.get_video_comments(video_id, skip=skip, limit=limit)
    total = await service.get_video_comments_count(video_id)
    return PaginatedCommentsResponse(
        comments=[map_comment_to_response(c) for c in comments],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Edit a comment",
    responses={**_error_responses},
)
async def update_comment(
    comment_id: UUID,
    body: CommentUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
):
    logger.info("comments.update.requested", extra={"comment_id": str(comment_id), "user_id": str(user_id)})
    comment = await service.update_comment(comment_id, user_id, body.content)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found or not owned by user")
    return map_comment_to_response(comment)


@router.delete(
    "/comments/{comment_id}",
    status_code=204,
    summary="Delete a comment",
    responses={**_error_responses},
)
async def delete_comment(
    comment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
):
    logger.info("comments.delete.requested", extra={"comment_id": str(comment_id), "user_id": str(user_id)})
    deleted = await service.delete_comment(comment_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found or not owned by user")
    return None


# Admin endpoints for comment moderation

@router.post(
    "/admin/comments/{comment_id}/block",
    response_model=AdminCommentActionResponse,
    summary="Block a comment (admin)",
    responses={**_error_responses},
)
async def block_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
    admin_payload: dict = Depends(require_admin),
):
    logger.info("admin.comments.block.requested", extra={"comment_id": str(comment_id)})
    admin_id = UUID(admin_payload["sub"])
    comment = await service.block_comment(comment_id, admin_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    logger.info("admin.comments.block.success", extra={"comment_id": str(comment_id)})
    return AdminCommentActionResponse(success=True, detail="Comment blocked")


@router.post(
    "/admin/comments/{comment_id}/unblock",
    response_model=AdminCommentActionResponse,
    summary="Unblock a comment (admin)",
    responses={**_error_responses},
)
async def unblock_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
    _admin=Depends(require_admin),
):
    logger.info("admin.comments.unblock.requested", extra={"comment_id": str(comment_id)})
    comment = await service.unblock_comment(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    logger.info("admin.comments.unblock.success", extra={"comment_id": str(comment_id)})
    return AdminCommentActionResponse(success=True, detail="Comment unblocked")


@router.post(
    "/subscriptions/follow/{following_id}",
    status_code=201,
    summary="Follow a user",
    description="Proxy to user_service follow endpoint.",
)
async def proxy_follow(
    following_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    user_svc: UserServiceClient = Depends(get_user_service_client),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.follow.requested", extra={"follower": str(user_id), "following": str(following_id)})
    ok = await user_svc.follow(user_id, following_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Already following or error")
    return {"success": True}


@router.delete(
    "/subscriptions/follow/{following_id}",
    status_code=204,
    summary="Unfollow a user",
    description="Proxy to user_service unfollow endpoint.",
)
async def proxy_unfollow(
    following_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    user_svc: UserServiceClient = Depends(get_user_service_client),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.unfollow.requested", extra={"follower": str(user_id), "following": str(following_id)})
    await user_svc.unfollow(user_id, following_id)
    return None


@router.get(
    "/subscriptions/{user_id}/following",
    summary="Get following",
    description="Proxy to user_service get following.",
)
async def proxy_get_following(
    user_id: UUID,
    user_svc: UserServiceClient = Depends(get_user_service_client),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.following.requested", extra={"user_id": str(user_id)})
    data = await user_svc.get_following(user_id)
    return {"subscriptions": data}


@router.get(
    "/subscriptions/{user_id}/followers",
    summary="Get followers",
    description="Proxy to user_service get followers.",
)
async def proxy_get_followers(
    user_id: UUID,
    user_svc: UserServiceClient = Depends(get_user_service_client),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.followers.requested", extra={"user_id": str(user_id)})
    data = await user_svc.get_followers(user_id)
    return {"subscriptions": data}


@router.get(
    "/subscriptions/is-following/{following_id}",
    summary="Check if following",
    description="Proxy to user_service is-following.",
)
async def proxy_is_following(
    following_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    user_svc: UserServiceClient = Depends(get_user_service_client),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.is_following.requested", extra={"follower": str(user_id), "following": str(following_id)})
    result = await user_svc.is_following(user_id, following_id)
    return {"is_following": result}


@router.get(
    "/users/{user_id}/liked-videos",
    response_model=LikedVideosResponse,
    summary="Get liked videos",
    description="Returns video IDs liked by a user.",
)
async def get_liked_videos(
    user_id: UUID,
    service: LikeService = Depends(get_like_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.liked_videos.requested", extra={"user_id": str(user_id)})
    video_ids = await service.get_user_liked_video_ids(user_id)
    logger.info("users.liked_videos.success", extra={"count": len(video_ids)})
    return LikedVideosResponse(video_ids=video_ids)


@router.delete(
    "/admin/comments/{comment_id}",
    status_code=204,
    summary="Delete any comment (admin)",
    description="Deletes any comment by ID (admin/moderator).",
    responses={**_error_responses},
)
async def admin_delete_comment(
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
    _admin=Depends(require_admin),
):
    logger.info("admin.comments.delete.requested", extra={"comment_id": str(comment_id)})
    deleted = await service.delete_comment_as_admin(comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    return None


@router.get(
    "/admin/comments/blocked",
    response_model=PaginatedCommentsResponse,
    summary="List blocked comments (admin)",
    responses={**_error_responses},
)
async def list_blocked_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: CommentService = Depends(get_comment_service),
    logger=Depends(get_logger_dep),
    _admin=Depends(require_admin),
):
    logger.info("admin.comments.blocked.list.requested", extra={"skip": skip, "limit": limit})
    comments = await service.get_blocked_comments(skip=skip, limit=limit)
    total = len(comments)
    return PaginatedCommentsResponse(
        comments=[map_comment_to_response(c) for c in comments],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/admin/users/{user_id}/ban",
    response_model=AdminActionResponse,
    summary="Admin: ban a user",
    description="Sets user status to 'banned' via user_service.",
)
async def admin_ban_user(
    user_id: UUID,
    user_svc: UserServiceClient = Depends(get_user_service_client),
    logger=Depends(get_logger_dep),
):
    logger.info("admin.users.ban.requested", extra={"user_id": str(user_id)})
    ok = await user_svc.update_user_status(user_id, "banned")
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("admin.users.ban.success", extra={"user_id": str(user_id)})
    return AdminActionResponse(success=True, detail=f"User {user_id} banned")


@router.post(
    "/admin/users/{user_id}/unban",
    response_model=AdminActionResponse,
    summary="Admin: unban a user",
    description="Sets user status to 'active' via user_service.",
)
async def admin_unban_user(
    user_id: UUID,
    user_svc: UserServiceClient = Depends(get_user_service_client),
    logger=Depends(get_logger_dep),
):
    logger.info("admin.users.unban.requested", extra={"user_id": str(user_id)})
    ok = await user_svc.update_user_status(user_id, "active")
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("admin.users.unban.success", extra={"user_id": str(user_id)})
    return AdminActionResponse(success=True, detail=f"User {user_id} unbanned")
