from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreateDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr

    @field_validator("username")
    @classmethod
    def username_chars(cls, v: str) -> str:
        allowed = set("_-")
        if not all(c.isalnum() or c in allowed for c in v):
            raise ValueError(
                "Username can only contain alphanumeric characters, underscores, and hyphens",
            )
        return v


class UserUpdateDTO(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    status: Optional[str] = Field(None, max_length=50)

    @field_validator("username")
    @classmethod
    def username_chars(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = set("_-")
        if not all(c.isalnum() or c in allowed for c in v):
            raise ValueError(
                "Username can only contain alphanumeric characters, underscores, and hyphens",
            )
        return v

    @field_validator("status")
    @classmethod
    def status_value(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = {"active", "inactive", "banned", "suspended"}
        if v.lower() not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return v.lower()


class TokenDecodeRequest(BaseModel):
    token: str


class TokenDecodedResponse(BaseModel):
    payload: dict[str, Any]


class UserResponseDTO(BaseModel):
    id: UUID
    username: str
    email: str
    status: str
    roles: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: list[UserResponseDTO]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class AssignRoleInternalRequest(BaseModel):
    user_id: str
    role: str = Field(..., min_length=1, max_length=50)

class RoleAssignDTO(BaseModel):
    role: str = Field(..., min_length=1, max_length=50)


class RoleResponse(BaseModel):
    user_id: UUID
    roles: list[str]


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code")
    detail: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., ge=400, description="HTTP status code")
    correlation_id: str = Field(default="N/A", description="Request correlation ID for tracing")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "VALIDATION_ERROR",
                "detail": "Password must contain at least one uppercase letter",
                "status_code": 422,
                "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            }
        },
    )


class SubscriptionActionRequest(BaseModel):
    following_id: UUID

class SubscriptionResponse(BaseModel):
    id: UUID
    follower_id: UUID
    following_id: UUID
    subscribed_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubscriptionListResponse(BaseModel):
    subscriptions: list[SubscriptionResponse]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=0)

class FollowStatusResponse(BaseModel):
    is_following: bool

class UserBriefResponse(BaseModel):
    id: UUID
    username: str
    avatar_url: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class BatchUserRequest(BaseModel):
    ids: list[UUID]

class UserStatsResponse(BaseModel):
    user_id: UUID
    total_videos: int
    total_views: int
    total_subscribers: int
    total_likes_received: int
    total_comments_received: int
    updated_at: datetime

class StatsUpdateRequest(BaseModel):
    field: str
    amount: int = 1


class AvatarResponse(BaseModel):
    avatar_url: str

class ProfileResponse(BaseModel):
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProfileUpdateRequest(BaseModel):
    bio: Optional[str] = None
    location: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Service health status")
    service: str = Field(default="user-service", description="Service name")
    version: str = Field(default="0.1.0", description="Service version")
