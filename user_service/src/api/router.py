from uuid import UUID

from fastapi import APIRouter, Depends, Query

from .schemas import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from ..deps import (
    get_create_user_service,
    get_delete_user_service,
    get_get_user_service,
    get_logger_dep,
    get_settings,
    get_update_user_service,
)
from ..services.create_user import CreateUserService
from ..services.delete_user import DeleteUserService
from ..services.get_user import GetUserService
from ..services.update_user import UpdateUserService

router = APIRouter()


@router.get("/health")
async def health_check(
    logger=Depends(get_logger_dep),
    settings=Depends(get_settings),
):
    logger.info("health_check.requested")
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.SERVICE_VERSION,
    }


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    request: UserCreateRequest,
    service: CreateUserService = Depends(get_create_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.create.requested", username=request.username, email=request.email)

    user = await service.execute(
        username=request.username,
        email=request.email,
        password=request.password,
    )

    logger.info("users.create.success", user_id=str(user.id))
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    service: GetUserService = Depends(get_get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.get.requested", user_id=str(user_id))

    user = await service.by_id(user_id)

    logger.info("users.get.success", user_id=str(user_id))
    return user


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: GetUserService = Depends(get_get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.list.requested", skip=skip, limit=limit)

    users = await service.all(skip=skip, limit=limit)

    logger.info("users.list.success", count=len(users))
    return UserListResponse(users=users, total=len(users), skip=skip, limit=limit)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    service: UpdateUserService = Depends(get_update_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.update.requested", user_id=str(user_id))

    user = await service.execute(
        user_id=user_id,
        username=request.username,
        email=request.email,
        password=request.password,
        status=request.status,
    )

    logger.info("users.update.success", user_id=str(user_id))
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    service: DeleteUserService = Depends(get_delete_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.delete.requested", user_id=str(user_id))

    await service.execute(user_id)

    logger.info("users.delete.success", user_id=str(user_id))
    return None
