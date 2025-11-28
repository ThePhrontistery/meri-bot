"""
Configuración centralizada del sistema de logging para MeriBot.

Este módulo maneja toda la configuración del sistema de logging,
incluyendo la creación de loggers, configuración de handlers
y variables de entorno.
"""

import os
import logging
import logging.handlers
from typing import Optional
from dotenv import load_dotenv

from .formatters import JsonFormatter
from meribot.core.config import load_config_from_yaml

# === CONFIGURATION ===
load_dotenv()

LOG_LEVEL = os.getenv("MERIBOT_LOG_LEVEL", "INFO").upper()
LOG_MAX_BYTES = int(os.getenv("MERIBOT_LOG_MAX_BYTES", "1048576"))  # 1MB default
LOG_BACKUP_COUNT = int(os.getenv("MERIBOT_LOG_BACKUP_COUNT", "5"))  # 5 backups default


def get_logger(module_name: str = "meribot", log_file: Optional[str] = None) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado.
    
    Args:
        module_name: Nombre del módulo para el logger
        log_file: Archivo de log opcional. Si no se especifica, solo log a consola
        
    Returns:
        logging.Logger: Logger configurado con handlers apropiados
        
    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("Mensaje informativo")
        
        >>> logger = get_logger("mi_modulo", "logs/mi_modulo.log")
        >>> logger.error("Error con archivo de log")
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(LOG_LEVEL)

    # Configurar archivo de log si se especifica
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # Evitar duplicar handlers
        if not any(isinstance(h, logging.handlers.RotatingFileHandler) 
                  and h.baseFilename == os.path.abspath(log_file) 
                  for h in logger.handlers):
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, 
                maxBytes=LOG_MAX_BYTES, 
                backupCount=LOG_BACKUP_COUNT, 
                encoding="utf-8"
            )
            file_handler.setFormatter(JsonFormatter())
            logger.addHandler(file_handler)

    # Añadir handler de consola si no existe
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)

    return logger


def configure_logger_level(level: str) -> None:
    """
    Configura el nivel de logging globalmente.
    
    Args:
        level: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    global LOG_LEVEL
    LOG_LEVEL = level.upper()
    
    # Actualizar nivel en el logger root
    logging.getLogger().setLevel(getattr(logging, LOG_LEVEL))


def get_sensitive_keys() -> set:
    """
    Obtiene las claves sensibles para sanitización desde configuración.
    
    Returns:
        set: Conjunto de claves sensibles en minúsculas
    """
    try:
        keys = load_config_from_yaml("SENSITIVE_KEYS") or []
        return set(k.lower() for k in keys)
    except Exception:
        # Claves por defecto si no se puede cargar la configuración
        return {"password", "key", "secret", "token", "auth"}