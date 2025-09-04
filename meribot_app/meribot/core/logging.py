"""
logging.py
----------
Logging centralizado y auditoría para MeriBot CORE.
"""
import logging
import logging.handlers
import json
import os
from meribot.core.config import config
from datetime import datetime
from typing import Any, Dict

LOG_LEVEL = os.getenv("MERIBOT_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("MERIBOT_LOG_FILE", "logs/meribot_core.log")
LOG_MAX_BYTES = int(os.getenv("MERIBOT_LOG_MAX_BYTES", 1048576))  # 1MB
LOG_BACKUP_COUNT = int(os.getenv("MERIBOT_LOG_BACKUP_COUNT", 5))

# Formato estructurado JSON
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)
        return json.dumps(log_record, ensure_ascii=False)

# Configuración del logger
logger = logging.getLogger("meribot.core")
logger.setLevel(LOG_LEVEL)

# Handler de archivo con rotación
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
)
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)

# Handler de consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)

# Sanitización de datos sensibles
SENSITIVE_KEYS = {"password", "api_key", "token", "secret"}

def sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k: ("***" if k.lower() in SENSITIVE_KEYS else v)
        for k, v in data.items()
    }

def log_critical_event(message: str, **kwargs):
    logger.critical(message, extra={"extra": sanitize(kwargs)})

def log_error(message: str, **kwargs):
    logger.error(message, extra={"extra": sanitize(kwargs)})

def log_guardrail_rejection(user_id: str, input_text: str, reason: str, **kwargs):
    logger.warning(
        "Input rechazado por guardrail",
        extra={"extra": sanitize({"user_id": user_id, "input": input_text, "reason": reason, **kwargs})}
    )


def log_guardrail_event(event_type: str, user_input: str, extra: dict = None):
    """
    Registra un evento de guardrail rechazado (input bloqueado, patrón prohibido, etc).
    El input se sanitiza para evitar fugas de datos sensibles.
    :param event_type: Motivo del rechazo (invalid_type, forbidden_pattern, etc)
    :param user_input: Input original (será sanitizado)
    :param extra: Diccionario opcional con más contexto
    """
    import html
    from datetime import datetime
    sanitized_input = html.escape(str(user_input))[:256]  # Limita longitud en log
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "guardrail_reject",
        "type": event_type,
        "input": sanitized_input,
    }
    if extra:
        log_data.update(extra)
    logger.warning(json.dumps(log_data, ensure_ascii=False))

def log_generation_failure(user_id: str, input_text: str, error: str, **kwargs):
    logger.error(
        "Fallo de generación LLM",
        extra={"extra": sanitize({"user_id": user_id, "input": input_text, "error": error, **kwargs})}
    )

# Ejemplo de uso:
# log_critical_event("Error crítico en el sistema", user_id="123", api_key="secreta")
# log_guardrail_rejection("123", "texto", "input prohibido")
# log_generation_failure("123", "texto", "timeout")
