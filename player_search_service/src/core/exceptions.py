import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import get_settings
from src.core.problem import problem_response

logger = logging.getLogger("player_search_service")


class DomainError(Exception):
    """Базовое исключение для доменных ошибок"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class VideoNotFoundError(DomainError):
    def __init__(self, video_id: str):
        self.video_id = video_id
        super().__init__(f"Video not found: {video_id}")


def register_rfc7807_handlers(app: FastAPI):
    """Регистрирует обработчики ошибок в FastAPI-приложении"""
    settings = get_settings()
    is_production = settings.APP_ENV == "production"

    @app.exception_handler(VideoNotFoundError)
    async def video_not_found_handler(request: Request, exc: VideoNotFoundError):
        logger.info("Video not found: %s on %s", exc.video_id, request.url.path)
        return problem_response(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Video Not Found",
            detail=exc.message,
            problem_type="https://misistube.dev/errors/not-found",
            instance=request.url.path,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return problem_response(
            status_code=exc.status_code,
            title=exc.detail or "HTTP Error",
            detail=exc.detail,
            problem_type=f"https://misistube.dev/errors/http-{exc.status_code}",
            instance=request.url.path,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
        return problem_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Error",
            detail="Request validation failed",
            errors=exc.errors(),
            problem_type="https://misistube.dev/errors/validation",
            instance=request.url.path,
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
            instance=request.url.path,
        )
