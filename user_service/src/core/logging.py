import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="N/A")


def _add_correlation_id(_: Any, __: str, event_dict: dict[str, object]) -> dict[str, object]:
    if "correlation_id" not in event_dict:
        event_dict["correlation_id"] = correlation_id_var.get()
    return event_dict


def _add_service_name(service_name: str):
    def wrapper(_: Any, __: str, event_dict: dict[str, object]) -> dict[str, object]:
        event_dict.setdefault("service", service_name)
        return event_dict

    return wrapper


def configure_structlog(log_level: str = "INFO", service_name: str = "user-service") -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        _add_correlation_id,
        _add_service_name(service_name),
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.propagate = False


def bind_correlation_id(correlation_id: str) -> None:
    correlation_id_var.set(correlation_id)


def get_logger(name: str = "user-service") -> structlog.BoundLogger:
    return structlog.get_logger(name)
