# authorization_service/src/logger_setup.py
import logging
from pathlib import Path

from shared.logger import get_logger as shared_get_logger


def get_logger_with_file(service_name: str, level: str, log_file: str | Path):
    """Получить логгер с записью в файл"""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Базовый логгер из shared (только stdout)
    logger = shared_get_logger(service_name, level)

    # Добавляем файловый handler
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logger.logger.handlers[0].formatter)
    logger.logger.addHandler(file_handler)

    return logger
