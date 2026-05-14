import uuid
from typing import Optional

from fastapi import Depends, Header

from src.core.logging import bind_correlation_id, configure_structlog, get_logger
from src.core.settings import settings, UserServiceSettings

configure_structlog(log_level=settings.LOG_LEVEL, service_name=settings.APP_NAME)


def get_settings() -> UserServiceSettings:
    return settings


async def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID"),
) -> str:
    correlation_id = x_correlation_id or str(uuid.uuid4())
    bind_correlation_id(correlation_id)
    return correlation_id


def get_logger_dep(correlation_id: str = Depends(get_correlation_id)):
    return get_logger().bind(correlation_id=correlation_id)
