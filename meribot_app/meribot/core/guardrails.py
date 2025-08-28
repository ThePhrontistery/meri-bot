"""
Módulo de guardrails y sanitización para MeriBot CORE.
Incluye validación de entradas, sanitización, y reglas configurables para bloquear prompts o respuestas peligrosas.
Cumple estándares de seguridad y accesibilidad.

@author: MeriBot Team
"""
import re
import html
from typing import Any, Dict, Optional
from .logging import log_guardrail_event

# Configuración de reglas de guardrails (puede ser extendida o cargada desde config)
DEFAULT_GUARDRAILS = {
    'max_length': 2048,
    'forbidden_patterns': [
        r'<script.*?>.*?</script>',  # XSS básico
        r'(drop|delete|truncate)\s+table',  # SQLi
        r'(prompt injection|ignore previous instructions)',
        r'\b(password|ssn|credit card|tarjeta|contraseña|clave)\b',
    ],
    'min_contrast_ratio': 4.5,  # WCAG AA
}

def validate_input(user_input: str, guardrails: Optional[Dict[str, Any]] = None) -> bool:
    """
    Valida la entrada del usuario según reglas de longitud, formato y patrones peligrosos.
    Llama a log_guardrail_event si se rechaza la entrada.
    :param user_input: Texto a validar
    :param guardrails: Reglas opcionales
    :return: True si es válida, False si se rechaza
    """
    rules = guardrails or DEFAULT_GUARDRAILS
    if not isinstance(user_input, str):
        log_guardrail_event('invalid_type', user_input)
        return False
    if len(user_input) > rules['max_length']:
        log_guardrail_event('input_too_long', user_input)
        return False
    for pattern in rules['forbidden_patterns']:
        if re.search(pattern, user_input, re.IGNORECASE):
            log_guardrail_event('forbidden_pattern', user_input)
            return False
    return True

def sanitize_input(user_input: str) -> str:
    """
    Sanitiza la entrada del usuario eliminando scripts, etiquetas peligrosas y escapando HTML.
    :param user_input: Texto a sanitizar
    :return: Texto seguro
    """
    # Elimina scripts y etiquetas peligrosas
    sanitized = re.sub(r'<script.*?>.*?</script>', '', user_input, flags=re.IGNORECASE|re.DOTALL)
    sanitized = re.sub(r'<.*?>', '', sanitized)  # Elimina cualquier etiqueta HTML
    sanitized = html.escape(sanitized)
    return sanitized

def enforce_accessibility(text: str, min_contrast: float = 4.5) -> bool:
    """
    Placeholder: Verifica que el texto cumpla contraste mínimo (WCAG AA).
    En producción, se debe calcular el contraste real entre texto y fondo.
    :param text: Texto a verificar
    :param min_contrast: Ratio mínimo
    :return: True si cumple, False si no
    """
    # Aquí solo se retorna True por defecto (implementación real requiere contexto visual)
    return True

def apply_guardrails(user_input: str, guardrails: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Aplica validación y sanitización. Si la entrada es rechazada, retorna None.
    :param user_input: Texto a procesar
    :param guardrails: Reglas opcionales
    :return: Texto seguro o None si se rechaza
    """
    if not validate_input(user_input, guardrails):
        return None
    return sanitize_input(user_input)

# Ejemplo de extensión: añadir nuevas reglas desde config o plugins
# Se recomienda usar apply_guardrails() antes de procesar cualquier input de usuario.
