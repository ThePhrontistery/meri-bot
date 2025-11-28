"""
Funciones especializadas de logging para eventos específicos de MeriBot.

Este módulo contiene funciones de logging para eventos específicos del sistema,
como fallos de generación LLM, eventos de guardrails, errores críticos, etc.
"""

import json
import html
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging

from .utils import sanitize


def log_critical_event(logger: logging.Logger, message: str, **kwargs) -> None:
    """
    Registra un evento crítico con datos adicionales sanitizados.
    
    Args:
        logger: Logger a usar para el registro
        message: Mensaje del evento crítico
        **kwargs: Datos adicionales a incluir (serán sanitizados)
        
    Examples:
        >>> log_critical_event(logger, "Sistema sobrecargado", cpu_usage=95, memory_usage=90)
    """
    logger.critical(message, extra={"extra": sanitize(kwargs)})


def log_error(logger: logging.Logger, message: str, **kwargs) -> None:
    """
    Registra un evento de error con datos adicionales sanitizados.
    
    Args:
        logger: Logger a usar para el registro
        message: Mensaje del error
        **kwargs: Datos adicionales a incluir (serán sanitizados)
        
    Examples:
        >>> log_error(logger, "Error de conexión a base de datos", host="localhost", port=5432)
    """
    logger.error(message, extra={"extra": sanitize(kwargs)})


def log_guardrail_rejection(logger: logging.Logger, user_id: str, input_text: str, 
                          reason: str, **kwargs) -> None:
    """
    Registra un rechazo por guardrails de seguridad.
    
    Args:
        logger: Logger a usar para el registro
        user_id: ID del usuario cuyo input fue rechazado
        input_text: Texto de entrada que fue rechazado
        reason: Razón del rechazo
        **kwargs: Datos adicionales (serán sanitizados)
        
    Examples:
        >>> log_guardrail_rejection(logger, "user123", "texto malicioso", "contenido inapropiado")
    """
    logger.warning(
        "Input rechazado por guardrail",
        extra={"extra": sanitize({
            "user_id": user_id, 
            "input": input_text, 
            "reason": reason, 
            **kwargs
        })}
    )


def log_guardrail_event(logger: logging.Logger, event_type: str, user_input: str, 
                       extra: Optional[Dict[str, Any]] = None) -> None:
    """
    Registra un evento de guardrail (input bloqueado, patrón prohibido, etc.).
    
    Args:
        logger: Logger a usar para el registro
        event_type: Tipo de evento de guardrail
        user_input: Input del usuario que activó el guardrail
        extra: Datos adicionales opcionales
        
    Examples:
        >>> log_guardrail_event(logger, "blocked_pattern", "input sospechoso", {"pattern": "injection"})
    """
    # Sanitizar y truncar input para evitar logs excesivamente largos
    sanitized_input = html.escape(str(user_input))[:256]
    
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "event": "guardrail_reject",
        "type": event_type,
        "input": sanitized_input,
    }
    
    if extra:
        log_data.update(sanitize(extra))
        
    logger.warning(json.dumps(log_data, ensure_ascii=False))


def log_generation_failure(logger: logging.Logger, user_id: str, input_text: str, 
                         error: str, **kwargs) -> None:
    """
    Registra un fallo de generación del LLM.
    
    Args:
        logger: Logger a usar para el registro
        user_id: ID del usuario que experimentó el fallo
        input_text: Texto de entrada que causó el fallo
        error: Descripción del error ocurrido
        **kwargs: Datos adicionales (serán sanitizados)
        
    Examples:
        >>> log_generation_failure(logger, "user456", "prompt complejo", "timeout", model="gpt-4")
    """
    logger.error(
        "Fallo de generación LLM",
        extra={"extra": sanitize({
            "user_id": user_id, 
            "input": input_text, 
            "error": error, 
            **kwargs
        })}
    )


def log_conversation_start(logger: logging.Logger, conversation_id: str, user_id: str, 
                         **kwargs) -> None:
    """
    Registra el inicio de una conversación.
    
    Args:
        logger: Logger a usar para el registro
        conversation_id: ID único de la conversación
        user_id: ID del usuario que inicia la conversación
        **kwargs: Datos adicionales (serán sanitizados)
    """
    logger.info(
        "Conversación iniciada",
        extra={"extra": sanitize({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "event": "conversation_start",
            **kwargs
        })}
    )


def log_conversation_end(logger: logging.Logger, conversation_id: str, user_id: str,
                        duration_seconds: float, message_count: int, **kwargs) -> None:
    """
    Registra el fin de una conversación.
    
    Args:
        logger: Logger a usar para el registro
        conversation_id: ID único de la conversación
        user_id: ID del usuario
        duration_seconds: Duración de la conversación en segundos
        message_count: Número total de mensajes intercambiados
        **kwargs: Datos adicionales (serán sanitizados)
    """
    logger.info(
        "Conversación finalizada",
        extra={"extra": sanitize({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "duration_seconds": duration_seconds,
            "message_count": message_count,
            "event": "conversation_end",
            **kwargs
        })}
    )