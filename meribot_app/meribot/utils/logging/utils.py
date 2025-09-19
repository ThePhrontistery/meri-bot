"""
Utilidades para el sistema de logging de MeriBot.

Este módulo contiene funciones auxiliares para el sistema de logging,
incluyendo sanitización de datos sensibles y utilidades de formateo.
"""

from typing import Any, Dict
from .config import get_sensitive_keys


def sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitiza datos sensibles en un diccionario reemplazando valores con asteriscos.
    
    Esta función revisa las claves del diccionario contra una lista de claves sensibles
    y reemplaza los valores correspondientes con "***" para evitar filtración de
    información confidencial en los logs.
    
    Args:
        data: Diccionario con datos a sanitizar
        
    Returns:
        Dict[str, Any]: Diccionario con valores sensibles reemplazados
        
    Examples:
        >>> data = {"username": "user123", "password": "secret123", "api_key": "abc123"}
        >>> sanitize(data)
        {"username": "user123", "password": "***", "api_key": "***"}
    """
    if not isinstance(data, dict):
        return data
        
    sensitive_keys = get_sensitive_keys()
    
    return {
        k: ("***" if k.lower() in sensitive_keys else v)
        for k, v in data.items()
    }


def format_exception_for_logging(exception: Exception) -> Dict[str, Any]:
    """
    Formatea una excepción para logging estructurado.
    
    Args:
        exception: Excepción a formatear
        
    Returns:
        Dict[str, Any]: Diccionario con información estructurada de la excepción
    """
    import traceback
    
    return {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "traceback": traceback.format_exc()
    }


def safe_format_data(data: Any) -> str:
    """
    Formatea datos de manera segura para logging.
    
    Maneja diferentes tipos de datos y los convierte a string de manera segura,
    evitando errores de serialización.
    
    Args:
        data: Datos a formatear
        
    Returns:
        str: Representación string segura de los datos
    """
    try:
        if isinstance(data, dict):
            return str(sanitize(data))
        elif isinstance(data, (list, tuple)):
            return str([safe_format_data(item) for item in data])
        else:
            return str(data)
    except Exception:
        return f"<Error formatting data of type {type(data).__name__}>"