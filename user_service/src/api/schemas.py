"""API Request/Response schemas."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class UserCreateRequest(BaseModel):
    """Request schema for creating a user."""

    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    display_name: Optional[str] = Field(None, max_length=255)


class UserUpdateRequest(BaseModel):
    """Request schema for updating a user."""

    username: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    display_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Response schema for a user."""

    id: UUID
    username: str
    email: str
    display_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Response schema for user list."""

    users: list[UserResponse]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=0)


class ErrorResponse(BaseModel):
    """Error response schema (RFC 7807-inspired)."""

    error: str = Field(..., description="Error code")
    detail: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., ge=400, description="HTTP status code")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "VALIDATION_ERROR",
                "detail": "Username must be at least 3 characters long",
                "status_code": 400,
            }
        }
    }
