import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

import logging
from logging.handlers import RotatingFileHandler
from shared.logger import correlation_id_var

# Московский часовой пояс (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))


class JSONFormatter(logging.Formatter):    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=MOSCOW_TZ).isoformat()

        service = getattr(record, 'service', None) or record.__dict__.get('service', 'player_search_service')
        if service == 'unknown':
            service = 'player_search_service'

        correlation_id = correlation_id_var.get()
        
        log_entry = {
            "timestamp": timestamp,
            "level": record.levelname,
            "service": service,
            "correlation_id": correlation_id,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ServiceFilter(logging.Filter):
    """Добавляет поле 'service' во все логи"""
    
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.service = self.service_name
        return True

def setup_service_logger(service_name: str, level: str = "INFO") -> logging.LoggerAdapter:
    src_level = getattr(logging, level.upper(), logging.INFO)
    
    service_logger = logging.getLogger(service_name)
    
    if not service_logger.handlers:
        service_logger.setLevel(src_level)
        service_logger.propagate = False
        
        service_filter = ServiceFilter(service_name)
        service_logger.addFilter(service_filter)
        
        formatter = JSONFormatter()
        
        # Консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(src_level)
        service_logger.addHandler(console_handler)
        
        # Файл
        log_file = ROOT_DIRECTORY / "logs/player_search_service.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
            delay=True
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        service_logger.addHandler(file_handler)
    
    return logging.LoggerAdapter(service_logger, {"service": service_name})