"""RFC 7807 Problem Details для стандартизации ответов об ошибках"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi.responses import JSONResponse


class ProblemDetail(BaseModel):
    """Структура ошибки по стандарту RFC 7807"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "https://misistube.dev/errors/validation",
                "title": "Validation Error",
                "status": 422,
                "detail": "Field 'q' is required",
                "instance": "/api/v1/search"
            }
        }
    )

    type: str = Field(default="about:blank", description="URI-тип ошибки")
    title: str = Field(..., description="Краткое название проблемы")
    status: int = Field(..., description="HTTP-статус код")
    detail: Optional[str] = Field(None, description="Подробное описание (может содержать JSON-строку)")
    instance: Optional[str] = Field(None, description="URI конкретного запроса, вызвавшего ошибку")


def problem_response(
    status_code: int,
    title: str,
    detail: str | None = None,
    problem_type: str = "about:blank",
    instance: str | None = None
) -> JSONResponse:
    """Возвращает ответ в формате RFC 7807 с правильным Content-Type"""
    content = ProblemDetail(
        type=problem_type,
        title=title,
        status=status_code,
        detail=detail,
        instance=instance
    ).model_dump(exclude_none=True)
    
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={"Content-Type": "application/problem+json"}
    )