import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="N/A")


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service_name", "unknown"),
            "correlation_id": correlation_id_var.get(),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


def get_logger(service_name: str, level: str = "INFO", log_file: str | Path | None = None) -> logging.LoggerAdapter:
    logger = logging.getLogger(service_name)
    if not logger.handlers:
        formatter = JSONFormatter()

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(getattr(logging, level.upper()))
        logger.propagate = False
    return logging.LoggerAdapter(logger, {"service_name": service_name})
