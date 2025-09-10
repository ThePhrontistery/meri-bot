
"""Centralized logging and audit for MeriBot CORE."""

# === IMPORTS ===
# Standard library
import os
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Any, Dict
# Third-party
import yaml
from dotenv import load_dotenv
# Local
from meribot.utils.json_formatter import JsonFormatter

# === CONSTANTS ===
load_dotenv()

LOG_LEVEL = os.getenv("MERIBOT_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("MERIBOT_LOG_FILE")
LOG_DIR = os.path.dirname(LOG_FILE) if LOG_FILE else None
LOG_MAX_BYTES = int(os.getenv("MERIBOT_LOG_MAX_BYTES", "1048576"))  # 1MB por defecto
LOG_BACKUP_COUNT = int(os.getenv("MERIBOT_LOG_BACKUP_COUNT", "5"))  # 5 backups por defecto
CRAWLER_CONFIG_PATH = os.getenv("CRAWLER_CONFIG_PATH")

logger = logging.getLogger("meribot.core")
logger.setLevel(LOG_LEVEL)
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
)
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)

def ensure_log_dir_exists() -> None:
    """Ensure the log directory exists for LOG_FILE."""
    print(f"Log file: {LOG_FILE}, Log dir: {LOG_DIR}")
    if not LOG_DIR:
        return
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

ensure_log_dir_exists()

def load_config_param(param: str):
    try:
        with open(CRAWLER_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            value = config.get(param, None)
            if value is None:
                raise KeyError(f"Parameter '{param}' not found in {CRAWLER_CONFIG_PATH}")
            return value
    except Exception as e:
        raise RuntimeError(f"Error loading '{param}' from {CRAWLER_CONFIG_PATH}: {e}")

SENSITIVE_KEYS = set(k.lower() for k in load_config_param("SENSITIVE_KEYS"))

def sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize sensitive keys in a dict."""
    return {
        k: ("***" if k.lower() in SENSITIVE_KEYS else v)
        for k, v in data.items()
    }

def log_critical_event(message: str, **kwargs) -> None:
    """Log a critical event with sanitized extra data."""
    logger.critical(message, extra={"extra": sanitize(kwargs)})

def log_error(message: str, **kwargs) -> None:
    """Log an error event with sanitized extra data."""
    logger.error(message, extra={"extra": sanitize(kwargs)})

def log_guardrail_rejection(user_id: str, input_text: str, reason: str, **kwargs) -> None:
    """Log a guardrail rejection event."""
    logger.warning(
        "Input rechazado por guardrail",
        extra={"extra": sanitize({"user_id": user_id, "input": input_text, "reason": reason, **kwargs})}
    )

def log_guardrail_event(event_type: str, user_input: str, extra: dict = None) -> None:
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

def log_generation_failure(user_id: str, input_text: str, error: str, **kwargs) -> None:
    """Log an LLM generation failure event."""
    logger.error(
        "Fallo de generación LLM",
        extra={"extra": sanitize({"user_id": user_id, "input": input_text, "error": error, **kwargs})}
    )
