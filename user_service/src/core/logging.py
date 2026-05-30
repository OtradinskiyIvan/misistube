import logging
import sys
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.logger import correlation_id_var, get_logger

__all__ = ["correlation_id_var", "get_logger", "bind_correlation_id", "configure_logging"]


def bind_correlation_id(correlation_id: str) -> None:
    correlation_id_var.set(correlation_id)


def configure_logging(log_level: str = "INFO", service_name: str = "user-service") -> None:
    logging.getLogger().setLevel(getattr(logging, log_level.upper(), logging.INFO))
    get_logger(service_name, log_level)
