from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field


class ProblemDetail(BaseModel):
    """Структура ошибки по стандарту RFC 7807"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "https://misistube.dev/errors/validation",
                "title": "Validation Error",
                "status": 422,
                "detail": "Request validation failed",
                "errors": [{"type": "missing", "loc": ["query", "q"], "msg": "Field required"}],
                "instance": "/api/v1/search",
            }
        }
    )

    type: str = Field(default="about:blank", description="URI-тип ошибки")
    title: str = Field(..., description="Краткое название проблемы")
    status: int = Field(..., description="HTTP-статус код")
    detail: str | None = Field(None, description="Подробное описание")
    errors: list[dict[str, Any]] | None = Field(None, description="Детали ошибок валидации")
    instance: str | None = Field(None, description="URI конкретного запроса")


def problem_response(
    status_code: int,
    title: str,
    detail: str | None = None,
    errors: list[dict[str, Any]] | None = None,
    problem_type: str = "about:blank",
    instance: str | None = None,
) -> JSONResponse:
    """Возвращает ответ в формате RFC 7807 с правильным Content-Type"""
    content = ProblemDetail(
        type=problem_type,
        title=title,
        status=status_code,
        detail=detail,
        errors=errors,
        instance=instance,
    ).model_dump(exclude_none=True)

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={"Content-Type": "application/problem+json"},
    )
