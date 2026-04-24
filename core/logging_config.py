"""
Structured JSON logging formatter for shipping logs to Kibana.
"""
import json
import logging
import traceback
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Formats log records as a single-line JSON string.
    Fields are compatible with Kibana's default field mappings.
    """

    RESERVED_ATTRS = {
        "args", "created", "exc_info", "exc_text", "filename",
        "funcName", "id", "levelname", "levelno", "lineno",
        "module", "msecs", "message", "msg", "name", "pathname",
        "process", "processName", "relativeCreated", "stack_info",
        "thread", "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_object: dict = {
            "@timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }

        # Attach exception info if present
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
            log_object["traceback"] = traceback.format_exception(*record.exc_info)

        # Attach any extra fields passed via the `extra` kwarg
        for key, value in record.__dict__.items():
            if key not in self.RESERVED_ATTRS and not key.startswith("_"):
                log_object[key] = value

        return json.dumps(log_object, default=str)
