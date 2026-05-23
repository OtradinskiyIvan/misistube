from fastapi import APIRouter, status
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from uuid import UUID, uuid4
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    return UserOut(
        id=uuid4(),
        email=payload.email,
        is_active=True,
        created_at=datetime.utcnow(),
    )

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    return TokenResponse(
        access_token="stub-access-token",
        refresh_token="stub-refresh-token",
        token_type="Bearer",
    )

@router.get("/me", response_model=UserOut)
async def get_current_user():
    return UserOut(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        email="stub@example.com",
        is_active=True,
        created_at=datetime.utcnow(),
    )
