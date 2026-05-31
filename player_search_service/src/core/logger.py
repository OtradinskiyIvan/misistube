import sys
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

import logging
from logging.handlers import RotatingFileHandler

from shared.logger import JSONFormatter


def setup_service_logger(service_name: str, level: str = "INFO") -> logging.LoggerAdapter:
    """
    Создаёт логгер, который пишет в консоль И в файл.
    Использует JSON-форматтер и correlation_id из shared.
    """
    logger = logging.getLogger(service_name)

    if logger.handlers:
        return logging.LoggerAdapter(logger, {"service_name": service_name})

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False  # Чтобы логи не дублировались в root-логгер

    formatter = JSONFormatter()

    # Консольный вывод (для Docker logs / терминала)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # всегда относительно расположения этого файла
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / "service.log",
        maxBytes=10 * 1024 * 1024,  # 10 МБ на файл
        backupCount=5,              # Храним 5 последних архивов
        encoding="utf-8",
        delay=True                  # Создаём файл только при первой записи
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # B файл пишем всё (включая DEBUG)
    logger.addHandler(file_handler)

    return logging.LoggerAdapter(logger, {"service_name": service_name})
