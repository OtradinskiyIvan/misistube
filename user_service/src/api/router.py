"""API Router for user service endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from .schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
    ErrorResponse,
)
from ..deps import get_logger_dep, get_settings, get_user_service
from ..domain.exceptions import UserNotFoundError
from ..services.user_service import UserService

router = APIRouter()


@router.get("/health")
async def health_check(
    logger=Depends(get_logger_dep),
    settings=Depends(get_settings),
):
    """Health check endpoint."""
    logger.info("health_check.requested")
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.SERVICE_VERSION,
    }


# ============================================================================
# Users Endpoints: /api/v1/users
# ============================================================================


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    request: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    """Create a new user.
    
    Request body:
    - username: str (3-255 chars, alphanumeric + underscore/hyphen)
    - email: str (valid email)
    - display_name: str | null (optional, max 255 chars)
    """
    logger.info("users.create.requested", username=request.username, email=request.email)
    
    user = await user_service.create_user(
        username=request.username,
        email=request.email,
        display_name=request.display_name,
    )
    
    logger.info("users.create.success", user_id=str(user.id))
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    """Get user by ID."""
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
    """List all users with pagination.
    
    Query parameters:
    - skip: int (default: 0, min: 0)
    - limit: int (default: 100, min: 1, max: 1000)
    """
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
    """Update user by ID.
    
    Request body (all fields optional):
    - username: str | null
    - email: str | null
    - display_name: str | null
    - is_active: bool | null
    """
    logger.info("users.update.requested", user_id=str(user_id))
    
    user = await user_service.update_user(
        user_id=user_id,
        username=request.username,
        email=request.email,
        display_name=request.display_name,
        is_active=request.is_active,
    )
    
    logger.info("users.update.success", user_id=str(user_id))
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    logger=Depends(get_logger_dep),
):
    """Delete user by ID."""
    logger.info("users.delete.requested", user_id=str(user_id))
    
    await user_service.delete_user(user_id)
    
    logger.info("users.delete.success", user_id=str(user_id))
    return None