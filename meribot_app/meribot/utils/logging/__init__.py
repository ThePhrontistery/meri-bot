"""
Sistema de logging centralizado para MeriBot.

Este módulo proporciona una interfaz unificada para logging en todo el sistema MeriBot,
incluyendo formatters estructurados, handlers especializados y funciones de logging
para eventos específicos.

Uso básico:
    from meribot.utils.logging import get_logger
    
    logger = get_logger(__name__)
    logger.info("Mensaje informativo")

Funciones especializadas:
    from meribot.utils.logging import log_generation_failure
    
    log_generation_failure(logger, user_id, prompt, error)
"""

from .config import get_logger, LOG_LEVEL, LOG_MAX_BYTES, LOG_BACKUP_COUNT
from .events import (
    log_critical_event,
    log_error,
    log_guardrail_rejection,
    log_guardrail_event,
    log_generation_failure
)
from .formatters import JsonFormatter
from .utils import sanitize

__all__ = [
    # Configuración principal
    'get_logger',
    'LOG_LEVEL', 
    'LOG_MAX_BYTES',
    'LOG_BACKUP_COUNT',
    
    # Funciones de eventos especializados
    'log_critical_event',
    'log_error', 
    'log_guardrail_rejection',
    'log_guardrail_event',
    'log_generation_failure',
    
    # Formatters
    'JsonFormatter',
    
    # Utilidades
    'sanitize'
]