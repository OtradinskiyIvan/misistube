import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.logger import correlation_id_var, get_logger as shared_get_logger, JSONFormatter

__all__ = ["correlation_id_var", "get_logger", "bind_correlation_id", "configure_logging"]

LOG_DIR = ROOT_DIRECTORY / "logs"
LOG_FILE = LOG_DIR / "interaction_service.log"


def bind_correlation_id(correlation_id: str) -> None:
    correlation_id_var.set(correlation_id)


def get_logger(name: str = "interaction-service", level: str = "INFO") -> logging.LoggerAdapter:
    logger = shared_get_logger(name, level)
    _ensure_file_handler(logger, level)
    return logger


def _ensure_file_handler(logger: logging.LoggerAdapter, log_level: str) -> None:
    for handler in logger.logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            return

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8",
    )
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    handler.setFormatter(JSONFormatter())
    logger.logger.addHandler(handler)


def configure_logging(log_level: str = "INFO", service_name: str = "interaction-service") -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)

    logger = get_logger(service_name, log_level)
    _ensure_file_handler(logger, log_level)
