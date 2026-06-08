from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from jwt import ExpiredSignatureError, InvalidTokenError

from .mappers import (
    map_create_dto,
    map_update_dto,
    map_user_to_response,
    map_users_to_response,
)
from .schemas import (
    AssignRoleInternalRequest,
    AvatarResponse,
    BatchUserRequest,
    ErrorResponse,
    FollowStatusResponse,
    HealthResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    RoleAssignDTO,
    RoleResponse,
    StatsUpdateRequest,
    SubscriptionActionRequest,
    SubscriptionListResponse,
    SubscriptionResponse,
    TokenDecodeRequest,
    TokenDecodedResponse,
    UserBriefResponse,
    UserCreateDTO,
    UserListResponse,
    UserResponseDTO,
    UserStatsResponse,
    UserUpdateDTO,
)
from ..core.security import decode_jwt_token
from ..deps import (
    get_assign_role_service,
    get_brief_user_service,
    get_create_user_service,
    get_delete_user_service,
    get_get_user_service,
    get_logger_dep,
    get_profile_service,
    get_settings,
    get_statistic_service,
    get_subscription_service,
    get_sync_user_service,
    get_update_user_service,
    get_user_roles_service,
    get_revoke_role_service,
    require_admin,
    get_current_user_payload,
    verify_internal_api_key,
)
from ..services.assign_role import AssignRoleService
from ..services.brief_user import BriefUserService
from ..services.create_user import CreateUserService
from ..services.delete_user import DeleteUserService
from ..services.get_user import GetUserService
from ..services.get_user_roles import GetUserRolesService
from ..services.revoke_role import RevokeRoleService
from ..services.statistic_service import StatisticService
from ..services.subscription_service import SubscriptionService
from ..services.profile_service import ProfileService
from ..services.sync_user import SyncUserService
from ..services.update_user import UpdateUserService

router = APIRouter(tags=["users"])

_error_responses = {
    400: {"model": ErrorResponse, "description": "Validation or duplicate error"},
    404: {"model": ErrorResponse, "description": "User not found"},
    422: {"model": ErrorResponse, "description": "Request validation error"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
}


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Returns service health status",
)
async def health_check(
    logger=Depends(get_logger_dep),
    settings=Depends(get_settings),
):
    logger.info("health_check.requested")
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.SERVICE_VERSION,
    )


@router.post(
    "/auth/decode",
    response_model=TokenDecodedResponse,
    tags=["auth"],
    summary="Decode JWT token",
    description="Decodes a JWT token and returns its payload.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid token"},
        401: {"model": ErrorResponse, "description": "Token has expired"},
    },
)
async def decode_token(
    payload: TokenDecodeRequest,
    settings=Depends(get_settings),
    logger=Depends(get_logger_dep),
):
    try:
        data = decode_jwt_token(
            payload.token,
            secret=settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        return TokenDecodedResponse(payload=data)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )


@router.post(
    "/auth/sync",
    response_model=UserResponseDTO,
    tags=["auth"],
    summary="Sync user from JWT",
    description="Decodes JWT and updates existing user data from payload. User must already exist (created by auth-service on email confirmation).",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid token or missing fields"},
        401: {"model": ErrorResponse, "description": "Token has expired"},
    },
)
async def sync_user(
    payload: TokenDecodeRequest,
    settings=Depends(get_settings),
    logger=Depends(get_logger_dep),
    service: SyncUserService = Depends(get_sync_user_service),
    is_internal: bool = Depends(verify_internal_api_key),
):
    try:
        data = decode_jwt_token(
            payload.token,
            secret=settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )

    if data.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    user_id = data.get("sub")
    username = data.get("username")
    email = data.get("email")

    if not user_id or not username or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token must contain sub, username, and email",
        )

    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format in token",
        )

    logger.info("auth.sync.requested", extra={"user_id": str(user_id), "username": username, "is_internal": is_internal})
    user = await service.execute(user_id=user_id, username=username, email=email, create_if_missing=is_internal)
    logger.info("auth.sync.success", extra={"user_id": str(user_id)})
    return map_user_to_response(user)


@router.post(
    "/auth/assign-role",
    response_model=RoleResponse,
    status_code=200,
    tags=["auth"],
    summary="Assign role to user (internal)",
    description="Assigns a role to a user. Authenticated via JWT from auth service.",
)
async def assign_role_internal(
    payload: AssignRoleInternalRequest,
    settings=Depends(get_settings),
    logger=Depends(get_logger_dep),
    service: AssignRoleService = Depends(get_assign_role_service),
    _admin=Depends(require_admin),
):
    try:
        user_id = UUID(payload.user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format",
        )

    logger.info("auth.assign_role.requested", extra={"user_id": str(user_id), "role": payload.role})
    roles = await service.execute(user_id=user_id, role=payload.role, assigned_by=None)
    logger.info("auth.assign_role.success", extra={"user_id": str(user_id), "role": payload.role})
    return RoleResponse(user_id=user_id, roles=roles)


@router.post(
    "/users",
    response_model=UserResponseDTO,
    status_code=201,
    summary="Create a new user",
    description="Creates a user with the given username and email (auth handled by auth-service).",
    responses={**_error_responses},
)
async def create_user(
    dto: UserCreateDTO,
    service: CreateUserService = Depends(get_create_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.create.requested", extra={"username": dto.username, "email": dto.email})
    data = map_create_dto(dto)
    user = await service.execute(**data)
    logger.info("users.create.success", extra={"user_id": str(user.id)})
    return map_user_to_response(user)


@router.get(
    "/users/search",
    response_model=list[UserBriefResponse],
    summary="Search users",
    description="Search users by username or uuid (case-insensitive partial match).",
)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: BriefUserService = Depends(get_brief_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.search.requested", extra={"query": q})
    users = await service.search_brief(q, skip, limit)
    logger.info("users.search.success", extra={"count": len(users)})
    return [
        UserBriefResponse(id=u.id, username=u.username, avatar_url=u.avatar_url, status=u.status)
        for u in users
    ]


@router.get(
    "/users/{user_id}",
    response_model=UserResponseDTO,
    summary="Get user by ID",
    description="Retrieves a user by their UUID.",
    responses={**_error_responses},
)
async def get_user(
    user_id: UUID,
    service: GetUserService = Depends(get_get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.get.requested", extra={"user_id": str(user_id)})
    user = await service.by_id(user_id)
    logger.info("users.get.success", extra={"user_id": str(user_id)})
    return map_user_to_response(user)


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List users",
    description="Returns a paginated list of users.",
    responses={**_error_responses},
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    service: GetUserService = Depends(get_get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.list.requested", extra={"skip": skip, "limit": limit})
    users = await service.all_with_roles(skip=skip, limit=limit)
    from ..api.schemas import UserResponseDTO
    user_dtos = [UserResponseDTO(**u) for u in users]
    logger.info("users.list.success", extra={"count": len(user_dtos)})
    return UserListResponse(
        users=user_dtos,
        total=len(user_dtos),
        skip=skip,
        limit=limit,
    )


@router.put(
    "/users/{user_id}",
    response_model=UserResponseDTO,
    summary="Update user",
    description="Updates an existing user's fields (username, email, status). Admin only.",
    responses={**_error_responses},
)
async def update_user(
    user_id: UUID,
    dto: UserUpdateDTO,
    service: UpdateUserService = Depends(get_update_user_service),
    logger=Depends(get_logger_dep),
    _admin=Depends(require_admin),
):
    logger.info("users.update.requested", extra={"user_id": str(user_id)})
    data = map_update_dto(dto)
    user = await service.execute(user_id=user_id, **data)
    logger.info("users.update.success", extra={"user_id": str(user_id)})
    return map_user_to_response(user)



@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponseDTO,
    summary="Update user status",
    description="Updates user status (active, inactive, banned, suspended). Admin only.",
    responses={**_error_responses},
)
async def update_user_status(
    user_id: UUID,
    dto: UserUpdateDTO,
    service: UpdateUserService = Depends(get_update_user_service),
    logger=Depends(get_logger_dep),
    _admin=Depends(require_admin),
):
    logger.info("users.status.update.requested", extra={"user_id": str(user_id), "status": dto.status})
    if not dto.status:
        raise HTTPException(status_code=400, detail="Status is required")
    data = map_update_dto(dto)
    user = await service.execute(user_id=user_id, **data)
    logger.info("users.status.update.success", extra={"user_id": str(user_id), "status": user.status})
    return map_user_to_response(user)


@router.delete(
    "/users/{user_id}",
    status_code=204,
    summary="Delete user",
    description="Permanently deletes a user by their UUID.",
    responses={
        204: {"description": "User deleted successfully"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_user(
    user_id: UUID,
    service: DeleteUserService = Depends(get_delete_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.delete.requested", extra={"user_id": str(user_id)})
    await service.execute(user_id)
    logger.info("users.delete.success", extra={"user_id": str(user_id)})
    return None


@router.get(
    "/users/{user_id}/status",
    response_model=dict,
    summary="Get user status",
    description="Returns the user's current status. Used by auth_service during login.",
    responses={**_error_responses},
)
async def get_user_status(
    user_id: UUID,
    service: GetUserService = Depends(get_get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.status.get.requested", extra={"user_id": str(user_id)})
    user = await service.by_id(user_id)
    logger.info("users.status.get.success", extra={"user_id": str(user_id), "status": user.status})
    return {"user_id": str(user.id), "status": user.status}


@router.get(
    "/users/{user_id}/roles",
    response_model=RoleResponse,
    summary="Get user roles",
    description="Returns a list of roles assigned to a user.",
    responses={**_error_responses},
)
async def get_user_roles(
    user_id: UUID,
    service: GetUserRolesService = Depends(get_user_roles_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.roles.get.requested", extra={"user_id": str(user_id)})
    roles = await service.execute(user_id)
    logger.info("users.roles.get.success", extra={"user_id": str(user_id), "roles": roles})
    return RoleResponse(user_id=user_id, roles=roles)


@router.post(
    "/users/{user_id}/roles",
    response_model=RoleResponse,
    status_code=201,
    summary="Assign role to user",
    description="Assigns a role to a user. Admin only.",
    responses={**_error_responses},
)
async def assign_role(
    user_id: UUID,
    dto: RoleAssignDTO,
    service: AssignRoleService = Depends(get_assign_role_service),
    logger=Depends(get_logger_dep),
    admin_payload: dict = Depends(require_admin),
):
    logger.info("users.roles.assign.requested", extra={"user_id": str(user_id), "role": dto.role})
    admin_id = UUID(admin_payload["sub"])
    roles = await service.execute(user_id=user_id, role=dto.role, assigned_by=admin_id)
    logger.info("users.roles.assign.success", extra={"user_id": str(user_id), "role": dto.role})
    return RoleResponse(user_id=user_id, roles=roles)


@router.delete(
    "/users/{user_id}/roles/{role}",
    response_model=RoleResponse,
    summary="Revoke role from user",
    description="Revokes a role from a user. Admin only.",
    responses={**_error_responses},
)
async def revoke_role(
    user_id: UUID,
    role: str,
    service: RevokeRoleService = Depends(get_revoke_role_service),
    logger=Depends(get_logger_dep),
    _admin=Depends(require_admin),
):
    logger.info("users.roles.revoke.requested", extra={"user_id": str(user_id), "role": role})
    roles = await service.execute(user_id=user_id, role=role)
    logger.info("users.roles.revoke.success", extra={"user_id": str(user_id), "role": role})
    return RoleResponse(user_id=user_id, roles=roles)


@router.get(
    "/users/{user_id}/brief",
    response_model=UserBriefResponse,
    summary="Get user brief",
    description="Returns lightweight user info (id, username, avatar_url, status).",
)
async def get_user_brief(
    user_id: UUID,
    service: BriefUserService = Depends(get_brief_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.brief.requested", extra={"user_id": str(user_id)})
    user = await service.get_brief(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info("users.brief.success", extra={"user_id": str(user_id)})
    return UserBriefResponse(
        id=user.id, username=user.username, avatar_url=user.avatar_url, status=user.status,
    )


@router.post(
    "/users/batch",
    response_model=list[UserBriefResponse],
    summary="Get batch users",
    description="Returns brief info for multiple users by IDs.",
)
async def batch_users(
    dto: BatchUserRequest,
    service: BriefUserService = Depends(get_brief_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.batch.requested", extra={"count": len(dto.ids)})
    users = await service.get_batch(dto.ids)
    logger.info("users.batch.success", extra={"count": len(users)})
    return [
        UserBriefResponse(id=u.id, username=u.username, avatar_url=u.avatar_url, status=u.status)
        for u in users
    ]


@router.post(
    "/users/{follower_id}/follow/{following_id}",
    response_model=SubscriptionResponse,
    summary="Follow a user",
    description="Creates a subscription (follower_id follows following_id).",
)
async def follow_user(
    follower_id: UUID,
    following_id: UUID,
    service: SubscriptionService = Depends(get_subscription_service),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.follow.requested", extra={"follower": str(follower_id), "following": str(following_id)})
    if follower_id == following_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
    sub = await service.follow(follower_id, following_id)
    logger.info("subscriptions.follow.success")
    return SubscriptionResponse(
        id=sub.id,
        follower_id=sub.follower_id,
        following_id=sub.following_id,
        subscribed_at=sub.subscribed_at,
    )


@router.delete(
    "/users/{follower_id}/follow/{following_id}",
    status_code=204,
    summary="Unfollow a user",
    description="Removes a subscription.",
)
async def unfollow_user(
    follower_id: UUID,
    following_id: UUID,
    service: SubscriptionService = Depends(get_subscription_service),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.unfollow.requested", extra={"follower": str(follower_id), "following": str(following_id)})
    await service.unfollow(follower_id, following_id)
    logger.info("subscriptions.unfollow.success")
    return None


@router.get(
    "/users/{user_id}/following",
    response_model=list[SubscriptionResponse],
    summary="Get following",
    description="Returns users that user_id is following.",
)
async def get_following(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SubscriptionService = Depends(get_subscription_service),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.following.requested", extra={"user_id": str(user_id)})
    subs = await service.get_following(user_id, skip, limit)
    logger.info("subscriptions.following.success", extra={"count": len(subs)})
    return [
        SubscriptionResponse(id=s.id, follower_id=s.follower_id, following_id=s.following_id, subscribed_at=s.subscribed_at)
        for s in subs
    ]


@router.get(
    "/users/{user_id}/followers",
    response_model=list[SubscriptionResponse],
    summary="Get followers",
    description="Returns users that follow user_id.",
)
async def get_followers(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SubscriptionService = Depends(get_subscription_service),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.followers.requested", extra={"user_id": str(user_id)})
    subs = await service.get_followers(user_id, skip, limit)
    logger.info("subscriptions.followers.success", extra={"count": len(subs)})
    return [
        SubscriptionResponse(id=s.id, follower_id=s.follower_id, following_id=s.following_id, subscribed_at=s.subscribed_at)
        for s in subs
    ]


@router.get(
    "/users/{follower_id}/is-following/{following_id}",
    response_model=FollowStatusResponse,
    summary="Check follow status",
    description="Returns whether follower_id is following following_id.",
)
async def is_following(
    follower_id: UUID,
    following_id: UUID,
    service: SubscriptionService = Depends(get_subscription_service),
    logger=Depends(get_logger_dep),
):
    logger.info("subscriptions.is_following.requested", extra={"follower": str(follower_id), "following": str(following_id)})
    result = await service.is_following(follower_id, following_id)
    return FollowStatusResponse(is_following=result)


@router.get(
    "/users/{user_id}/stats",
    response_model=UserStatsResponse,
    summary="Get user statistics",
    description="Returns aggregated statistics for a user (views, likes, comments, subscribers, videos).",
)
async def get_user_stats(
    user_id: UUID,
    service: StatisticService = Depends(get_statistic_service),
    sub_service: SubscriptionService = Depends(get_subscription_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.stats.get.requested", extra={"user_id": str(user_id)})
    stats = await service.get_or_create(user_id)
    subscribers = await sub_service.count_followers(user_id)
    return UserStatsResponse(
        user_id=stats.user_id,
        total_videos=stats.total_videos,
        total_views=stats.total_views,
        total_subscribers=subscribers,
        total_likes_received=stats.total_likes_received,
        total_comments_received=stats.total_comments_received,
        updated_at=stats.updated_at,
    )


@router.post(
    "/users/{user_id}/stats/increment",
    response_model=UserStatsResponse,
    summary="Increment a stat counter",
    description="Increments a specific stat field. Used by internal services.",
)
async def increment_user_stats(
    user_id: UUID,
    body: StatsUpdateRequest,
    service: StatisticService = Depends(get_statistic_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.stats.increment.requested", extra={"user_id": str(user_id), "field": body.field, "amount": body.amount})
    stats = await service.increment(user_id, body.field, body.amount)
    if stats is None:
        raise HTTPException(status_code=400, detail=f"Invalid field: {body.field}")
    return UserStatsResponse(
        user_id=stats.user_id,
        total_videos=stats.total_videos,
        total_views=stats.total_views,
        total_subscribers=stats.total_subscribers,
        total_likes_received=stats.total_likes_received,
        total_comments_received=stats.total_comments_received,
        updated_at=stats.updated_at,
    )


@router.post(
    "/users/{user_id}/stats/decrement",
    response_model=UserStatsResponse,
    summary="Decrement a stat counter",
    description="Decrements a specific stat field. Used by internal services.",
)
async def decrement_user_stats(
    user_id: UUID,
    body: StatsUpdateRequest,
    service: StatisticService = Depends(get_statistic_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.stats.decrement.requested", extra={"user_id": str(user_id), "field": body.field, "amount": body.amount})
    stats = await service.decrement(user_id, body.field, body.amount)
    if stats is None:
        raise HTTPException(status_code=400, detail=f"Invalid field: {body.field}")
    return UserStatsResponse(
        user_id=stats.user_id,
        total_videos=stats.total_videos,
        total_views=stats.total_views,
        total_subscribers=stats.total_subscribers,
        total_likes_received=stats.total_likes_received,
        total_comments_received=stats.total_comments_received,
        updated_at=stats.updated_at,
    )


@router.put(
    "/users/{user_id}/profile/avatar",
    response_model=AvatarResponse,
    summary="Upload or replace avatar",
)
async def upload_avatar(
    user_id: UUID,
    file: UploadFile = File(...),
    profile: ProfileService = Depends(get_profile_service),
    logger=Depends(get_logger_dep),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        raise HTTPException(status_code=400, detail="Unsupported image type. Use JPEG, PNG, GIF or WebP.")

    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5 MB.")

    url = await profile.upload_avatar(user_id, data, file.content_type)
    logger.info("profile.avatar.uploaded", extra={"user_id": str(user_id)})
    return AvatarResponse(avatar_url=url)


@router.delete(
    "/users/{user_id}/profile/avatar",
    summary="Delete avatar",
)
async def delete_avatar(
    user_id: UUID,
    profile: ProfileService = Depends(get_profile_service),
    logger=Depends(get_logger_dep),
):
    await profile.delete_avatar(user_id)
    logger.info("profile.avatar.deleted", extra={"user_id": str(user_id)})
    return {"detail": "Avatar deleted"}


@router.get(
    "/users/{user_id}/profile",
    response_model=ProfileResponse,
    summary="Get user profile",
)
async def get_profile(
    user_id: UUID,
    profile: ProfileService = Depends(get_profile_service),
):
    p = await profile.get_profile(user_id)
    if p is None:
        p = await profile.update_profile(user_id)
    return ProfileResponse(
        avatar_url=p.avatar_url,
        bio=p.bio,
        location=p.location,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.put(
    "/users/{user_id}/profile",
    response_model=ProfileResponse,
    summary="Update user profile (bio, location)",
)
async def update_profile(
    user_id: UUID,
    body: ProfileUpdateRequest,
    profile: ProfileService = Depends(get_profile_service),
    logger=Depends(get_logger_dep),
):
    p = await profile.update_profile(user_id, bio=body.bio, location=body.location)
    logger.info("profile.updated", extra={"user_id": str(user_id)})
    return ProfileResponse(
        avatar_url=p.avatar_url,
        bio=p.bio,
        location=p.location,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )
