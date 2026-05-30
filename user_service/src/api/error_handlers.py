"""Exception handlers for API responses."""
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..domain.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidUserDataError,
    UserDeletionError,
)

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.exceptions import AppBaseError, InfrastructureError, ValidationAppError


def _create_error_response(error: AppBaseError) -> dict:
    """Create error response dict from AppBaseError."""
    return {
        "error": error.code,
        "detail": error.message,
        "status_code": error.status_code,
    }


async def app_exception_handler(request: Request, exc: AppBaseError) -> JSONResponse:
    """Handle AppBaseError and its subclasses."""
    error_response = _create_error_response(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    error_response = {
        "error": "INTERNAL_ERROR",
        "detail": "An unexpected error occurred",
        "status_code": 500,
    }
    return JSONResponse(
        status_code=500,
        content=error_response,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers to the FastAPI app."""
    # Register AppBaseError handler for all domain exceptions
    app.add_exception_handler(AppBaseError, app_exception_handler)
    app.add_exception_handler(InfrastructureError, app_exception_handler)
    app.add_exception_handler(ValidationAppError, app_exception_handler)
    app.add_exception_handler(UserNotFoundError, app_exception_handler)
    app.add_exception_handler(UserAlreadyExistsError, app_exception_handler)
    app.add_exception_handler(InvalidUserDataError, app_exception_handler)
    app.add_exception_handler(UserDeletionError, app_exception_handler)

    # Catch-all for unexpected exceptions
    app.add_exception_handler(Exception, generic_exception_handler)
