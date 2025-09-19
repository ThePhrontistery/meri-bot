"""
Formatters personalizados para el sistema de logging de MeriBot.

Este módulo contiene diferentes formatters que pueden ser utilizados
para estructurar la salida de logs en diversos formatos.
"""

import json
from datetime import datetime, timezone
import logging


class JsonFormatter(logging.Formatter):
    """
    Formatter estructurado JSON para logs.
    
    Convierte los registros de log en formato JSON estructurado con:
    - timestamp en UTC con formato ISO
    - nivel de log
    - mensaje
    - información del módulo, función y línea
    - datos extra opcionales
    """
    
    def format(self, record):
        """
        Formatea un LogRecord en JSON estructurado.
        
        Args:
            record: LogRecord a formatear
            
        Returns:
            str: Registro formateado como JSON
        """
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        
        # Agregar datos extra si están disponibles
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)
            
        return json.dumps(log_record, ensure_ascii=False)


class EnrichedFormatter(logging.Formatter):
    """
    Formatter enriquecido para desarrollo y debugging.
    
    Proporciona una salida legible con colores y información detallada
    para facilitar el debugging durante el desarrollo.
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )