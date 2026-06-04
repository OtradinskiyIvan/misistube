from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code")
    detail: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., ge=400, description="HTTP status code")
    correlation_id: str = Field(default="N/A", description="Request correlation ID for tracing")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "VALIDATION_ERROR",
                "detail": "Invalid request data",
                "status_code": 422,
                "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            }
        },
    )


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    service: str = Field(default="interaction-service")
    version: str = Field(default="0.1.0")


class LikeRequest(BaseModel):
    video_id: UUID


class LikeResponse(BaseModel):
    liked: bool


class LikeCountResponse(BaseModel):
    video_id: UUID
    count: int


class CommentCreateRequest(BaseModel):
    video_id: UUID
    content: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[UUID] = None


class CommentUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    id: UUID
    user_id: UUID
    video_id: UUID
    parent_id: Optional[UUID] = None
    content: str
    is_edited: bool
    is_blocked: bool = False
    blocked_by: Optional[UUID] = None
    blocked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedCommentsResponse(BaseModel):
    comments: list[CommentResponse]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=0)


class AdminCommentActionResponse(BaseModel):
    success: bool
    detail: str = ""
