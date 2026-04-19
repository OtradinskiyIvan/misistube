from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from shared.exceptions import AppBaseError
from ..domain.exceptions import UserNotFoundError, UserAlreadyExistsError, InvalidCredentialsError

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFoundError)
    async def handle_user_not_found(request: Request, exc: UserNotFoundError):
        return JSONResponse(status_code=404, content={"error": "user_not_found", "detail": str(exc)})

    @app.exception_handler(UserAlreadyExistsError)
    async def handle_user_already_exists(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(status_code=409, content={"error": "user_already_exists", "detail": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials(request: Request, exc: InvalidCredentialsError):
        return JSONResponse(status_code=401, content={"error": "invalid_credentials", "detail": str(exc)})

    @app.exception_handler(AppBaseError)
    async def handle_app_error(request: Request, exc: AppBaseError):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.code, "detail": exc.message})