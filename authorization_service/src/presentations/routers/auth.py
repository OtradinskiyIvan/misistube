from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from ...services.auth import AuthService
from ..deps import get_auth_service
from ...domain.exceptions import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
):
    try:
        user = await service.register(payload.email, payload.password)
        return UserOut.model_validate(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    try:
        tokens = await service.login(payload.email, payload.password)
        return TokenResponse(**tokens)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=UserOut)
async def get_current_user(
    service: AuthService = Depends(get_auth_service),
    # В продакшене здесь будет Depends(get_current_user_id) из JWT
    user_id: str = "00000000-0000-0000-0000-000000000000"
):
    from uuid import UUID
    try:
        user = await service.get_user(UUID(user_id))
        return UserOut.model_validate(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))