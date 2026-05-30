from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreateDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def username_chars(cls, v: str) -> str:
        allowed = set("_-")
        if not all(c.isalnum() or c in allowed for c in v):
            raise ValueError(
                "Username can only contain alphanumeric characters, underscores, and hyphens",
            )
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdateDTO(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
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

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
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


class UserResponseDTO(BaseModel):
    id: UUID
    username: str
    email: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: list[UserResponseDTO]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code")
    detail: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., ge=400, description="HTTP status code")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "VALIDATION_ERROR",
                "detail": "Password must contain at least one uppercase letter",
                "status_code": 422,
            }
        },
    )
