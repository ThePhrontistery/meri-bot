"""Centralized logging and audit for MeriBot (CORE & CRAWLER).
Unifies logging setup, sanitization, and event functions.
"""

# === IMPORTS ===
import os
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Any, Dict
from dotenv import load_dotenv
from meribot.core.json_formatter import JsonFormatter
from meribot.core.config import load_config_from_yaml

# === CONFIGURATION ===
load_dotenv()

LOG_LEVEL = os.getenv("MERIBOT_LOG_LEVEL", "INFO").upper()
LOG_MAX_BYTES = int(os.getenv("MERIBOT_LOG_MAX_BYTES", "1048576"))  # 1MB default
LOG_BACKUP_COUNT = int(os.getenv("MERIBOT_LOG_BACKUP_COUNT", "5"))  # 5 backups default
CRAWLER_CONFIG_PATH = os.getenv("CRAWLER_CONFIG_PATH")


# === LOGGER FACTORY ===
def get_logger(module_name: str = "meribot", log_file: str = None) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado.
    Si se indica log_file, escribe en ese archivo; si no, usa MERIBOT_LOG_FILE.
    Evita duplicar handlers si el logger ya está configurado.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(LOG_LEVEL)

    # Determinar archivo de log
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        # Evitar duplicar handlers
        if not any(isinstance(h, logging.handlers.RotatingFileHandler) and h.baseFilename == os.path.abspath(log_file) for h in logger.handlers):
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
            )
            file_handler.setFormatter(JsonFormatter())
            logger.addHandler(file_handler)

    # Añadir consola si no existe
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)

    return logger

## Use shared config loader from core

# === SENSITIVE KEYS ===
try:
    SENSITIVE_KEYS = set(k.lower() for k in (load_config_from_yaml("SENSITIVE_KEYS") or []))
except Exception:
    SENSITIVE_KEYS = set()

# === SANITIZATION ===
def sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize sensitive keys in a dict."""
    return {
        k: ("***" if k.lower() in SENSITIVE_KEYS else v)
        for k, v in data.items()
    }

# === LOGGING FUNCTIONS ===

# === LOGGING FUNCTIONS (accept logger) ===
def log_critical_event(logger, message: str, **kwargs) -> None:
    """Log a critical event with sanitized extra data."""
    logger.critical(message, extra={"extra": sanitize(kwargs)})

def log_error(logger, message: str, **kwargs) -> None:
    """Log an error event with sanitized extra data."""
    logger.error(message, extra={"extra": sanitize(kwargs)})

def log_guardrail_rejection(logger, user_id: str, input_text: str, reason: str, **kwargs) -> None:
    """Log a guardrail rejection event."""
    logger.warning(
        "Input rechazado por guardrail",
        extra={"extra": sanitize({"user_id": user_id, "input": input_text, "reason": reason, **kwargs})}
    )

def log_guardrail_event(logger, event_type: str, user_input: str, extra: dict = None) -> None:
    """Log a guardrail event (input blocked, forbidden pattern, etc)."""
    import html
    sanitized_input = html.escape(str(user_input))[:256]
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "guardrail_reject",
        "type": event_type,
        "input": sanitized_input,
    }
    if extra:
        log_data.update(extra)
    logger.warning(json.dumps(log_data, ensure_ascii=False))

def log_generation_failure(logger, user_id: str, input_text: str, error: str, **kwargs) -> None:
    """Log an LLM generation failure event."""
    logger.error(
        "Fallo de generación LLM",
        extra={"extra": sanitize({"user_id": user_id, "input": input_text, "error": error, **kwargs})}
    )