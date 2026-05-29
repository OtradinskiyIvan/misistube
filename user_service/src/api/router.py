from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from .schemas import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from ..deps import get_logger_dep, get_settings, get_user_service
from ..services.user_service import UserService

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
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.create.requested", username=request.username, email=request.email)

    user = await user_service.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
    )

    logger.info("users.create.success", user_id=str(user.id))
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.get.requested", user_id=str(user_id))

    user = await user_service.get_user(user_id)

    logger.info("users.get.success", user_id=str(user_id))
    return user


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.list.requested", skip=skip, limit=limit)

    users = await user_service.get_all_users(skip=skip, limit=limit)

    logger.info("users.list.success", count=len(users))
    return UserListResponse(users=users, total=len(users), skip=skip, limit=limit)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.update.requested", user_id=str(user_id))

    user = await user_service.update_user(
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
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    logger.info("users.delete.requested", user_id=str(user_id))

    await user_service.delete_user(user_id)

    logger.info("users.delete.success", user_id=str(user_id))
    return None
