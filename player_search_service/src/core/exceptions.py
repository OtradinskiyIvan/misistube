import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError

from src.core.config import get_settings
from src.core.problem import problem_response

logger = logging.getLogger("player_search_service")


def register_rfc7807_handlers(app: FastAPI):
    """Регистрирует обработчики ошибок в FastAPI-приложении"""
    settings = get_settings()
    is_production = settings.APP_ENV == "production"

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
        return problem_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Error",
            detail="Request validation failed",
            errors=exc.errors(),
            problem_type="https://misistube.dev/errors/validation",
            instance=request.url.path
        )

    @app.exception_handler(Exception)
    async def global_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s: %s", request.url.path, exc)

        detail = "Internal server error" if is_production else str(exc)

        return problem_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail=detail,
            problem_type="https://misistube.dev/errors/internal",
            instance=request.url.path
        )