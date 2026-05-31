from fastapi import APIRouter, Depends, status, HTTPException

from authorization_service.src.services.auth import AuthService
from authorization_service.src.services import confirmation
from authorization_service.src.presentations.deps import get_auth_service
from authorization_service.src.presentations.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut, ConfirmRequest
from authorization_service.src.domain.entities.user import User
from uuid import UUID

router = APIRouter()

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    # create pending registration and send confirmation code
    try:
        await confirmation.create_pending_registration(payload.username, payload.email, payload.password, auth_service._settings)
    except Exception as exc:
        # propagate SMTP errors to client so they can correct settings
        raise HTTPException(status_code=500, detail=str(exc))

    return {"detail": "confirmation_sent"}


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_email(
    payload: ConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    ok = confirmation.verify_code(payload.email, payload.code)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired confirmation code")

    pending = confirmation.pop_pending(payload.email)
    if not pending:
        raise HTTPException(status_code=400, detail="No pending registration found or it expired")

    username, hashed_password = pending

    # construct domain user and save
    user = User(
        id=UUID(int=0),
        username=username,
        email=payload.email,
        hashed_password=hashed_password,
        is_active=True,
    )

    try:
        created = await auth_service._user_repo.save(user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return created

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    token_data = await auth_service.login(login=payload.login, password=payload.password)
    return TokenResponse(**token_data)

@router.get("/me", response_model=UserOut)
async def get_current_user():
    return UserOut(
        id="00000000-0000-0000-0000-000000000000",
        email="stub@example.com",
        is_active=True,
        created_at="1970-01-01T00:00:00Z",
    )
