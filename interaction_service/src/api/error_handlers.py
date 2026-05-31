"""Exception handlers for API responses."""
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..core.logging import correlation_id_var

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.exceptions import AppBaseError, InfrastructureError, ValidationAppError


def _create_error_response(error: AppBaseError) -> dict:
    return {
        "error": error.code,
        "detail": error.message,
        "status_code": error.status_code,
        "correlation_id": correlation_id_var.get(),
    }


async def app_exception_handler(request: Request, exc: AppBaseError) -> JSONResponse:
    error_response = _create_error_response(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    errors = exc.errors() if hasattr(exc, "errors") else []
    first = errors[0] if errors else {}
    field = " -> ".join(str(p) for p in first.get("loc", [])) if first else ""
    msg = first.get("msg", str(exc)) if first else str(exc)
    detail = f"{field}: {msg}" if field else msg
    correlation_id = correlation_id_var.get()
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "detail": detail,
            "status_code": 422,
            "correlation_id": correlation_id,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = correlation_id_var.get()
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred",
            "status_code": 500,
            "correlation_id": correlation_id,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppBaseError, app_exception_handler)
    app.add_exception_handler(InfrastructureError, app_exception_handler)
    app.add_exception_handler(ValidationAppError, app_exception_handler)

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    app.add_exception_handler(Exception, generic_exception_handler)
