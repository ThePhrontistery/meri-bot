"""
API endpoints para el módulo crawler de MeriBot.
Proporciona endpoints RESTful para operaciones de crawling, procesamiento de documentos
y gestión de la base de datos vectorial.
"""

from .router import router

__all__ = ["router"]