from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from jwt import ExpiredSignatureError, InvalidTokenError

from .mappers import (
    map_create_dto,
    map_update_dto,
    map_user_to_response,
    map_users_to_response,
)
from .schemas import (
    ErrorResponse,
    HealthResponse,
    TokenDecodeRequest,
    TokenDecodedResponse,
    UserCreateDTO,
    UserListResponse,
    UserResponseDTO,
    UserUpdateDTO,
)
from ..core.security import decode_jwt_token
from ..deps import (
    get_create_user_service,
    get_delete_user_service,
    get_get_user_service,
    get_logger_dep,
    get_settings,
    get_sync_user_service,
    get_update_user_service,
)
from ..services.create_user import CreateUserService
from ..services.delete_user import DeleteUserService
from ..services.get_user import GetUserService
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
    description="Decodes JWT, creates or updates user in DB from payload data.",
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

    logger.info("auth.sync.requested", extra={"user_id": str(user_id), "username": username})
    user = await service.execute(user_id=user_id, username=username, email=email)
    logger.info("auth.sync.success", extra={"user_id": str(user_id)})
    return map_user_to_response(user)


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
    users = await service.all(skip=skip, limit=limit)
    logger.info("users.list.success", extra={"count": len(users)})
    return UserListResponse(
        users=map_users_to_response(users),
        total=len(users),
        skip=skip,
        limit=limit,
    )


@router.put(
    "/users/{user_id}",
    response_model=UserResponseDTO,
    summary="Update user",
    description="Updates an existing user's fields (username, email, status).",
    responses={**_error_responses},
)
async def update_user(
    user_id: UUID,
    dto: UserUpdateDTO,
    service: UpdateUserService = Depends(get_update_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.update.requested", extra={"user_id": str(user_id)})
    data = map_update_dto(dto)
    user = await service.execute(user_id=user_id, **data)
    logger.info("users.update.success", extra={"user_id": str(user_id)})
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
