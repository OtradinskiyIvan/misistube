from fastapi import APIRouter, status, Depends
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from ..deps import get_auth_service
from ...services.auth import AuthService

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register(email=payload.email, password=payload.password)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    token_data = await auth_service.login(email=payload.email, password=payload.password)
    return TokenResponse(**token_data)

@router.get("/me", response_model=UserOut)
async def get_current_user():
    return UserOut(
        id="00000000-0000-0000-0000-000000000000",
        email="stub@example.com",
        is_active=True,
        created_at="1970-01-01T00:00:00Z",
    )
