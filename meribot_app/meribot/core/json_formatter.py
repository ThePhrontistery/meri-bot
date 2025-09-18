import json
from datetime import datetime, timezone
import logging

class JsonFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)
        return json.dumps(log_record, ensure_ascii=False)