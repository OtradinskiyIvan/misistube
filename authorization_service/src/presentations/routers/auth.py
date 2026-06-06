import logging
from uuid import UUID

from authorization_service.src.domain.entities.user import User
from authorization_service.src.domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from authorization_service.src.presentations.deps import get_auth_service
from authorization_service.src.presentations.schemas.auth import (
    AccessTokenResponse,
    ConfirmRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from authorization_service.src.services import confirmation
from authorization_service.src.services.auth import AuthService
from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger("Authorization Service")

router = APIRouter()

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    if await auth_service._user_repo.exists_by_email(payload.email):
        logger.warning("Register: email already registered: %s", payload.email)
        raise HTTPException(status_code=409, detail="Email already registered")
    if await auth_service._user_repo.exists_by_username(payload.username):
        logger.warning("Register: username already taken: %s", payload.username)
        raise HTTPException(status_code=409, detail="Username already taken")

    await confirmation.create_pending_registration(
        payload.username, payload.email, payload.password, auth_service._settings
    )
    logger.info("Register: confirmation sent to %s", payload.email)
    return {"detail": "confirmation_sent"}


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_email(
    payload: ConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    ok = confirmation.verify_code(payload.email, payload.code)
    if not ok:
        logger.warning("Confirm: invalid or expired code for %s", payload.email)
        raise HTTPException(status_code=400, detail="Invalid or expired confirmation code")

    pending = confirmation.pop_pending(payload.email)
    if not pending:
        logger.warning("Confirm: no pending registration for %s", payload.email)
        raise HTTPException(status_code=400, detail="No pending registration found or it expired")

    username, hashed_password = pending

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
        logger.error("Confirm: failed to save user %s: %s", payload.email, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    await auth_service.sync_user_to_user_service(created)
    logger.info("Confirm: user %s confirmed", payload.email)
    return created

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    logger.info("Login attempt: %s", payload.login)
    try:
        token_data = await auth_service.login(
            login=payload.login,
            password=payload.password,
            admin_key=payload.admin_key,
        )
        logger.info("Login success: %s", payload.login)
        return TokenResponse(**token_data)
    except InvalidCredentialsError as exc:
        logger.warning("Login failed for %s: %s", payload.login, exc)
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    payload: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        token_data = await auth_service.refresh_access_token(payload.refresh_token)
    except InvalidCredentialsError as exc:
        logger.warning("Refresh failed: %s", exc)
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return AccessTokenResponse(**token_data)

@router.get("/me", response_model=UserOut)
async def get_current_user():
    logger.warning("/me endpoint called — stub implementation")
    return UserOut(
        id="00000000-0000-0000-0000-000000000000",
        email="stub@example.com",
        is_active=True,
        created_at="1970-01-01T00:00:00Z",
    )
