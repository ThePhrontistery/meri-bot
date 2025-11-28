"""
Tests unitarios para el módulo core de MeriBot.

Este paquete contiene tests unitarios completos para validar el correcto
funcionamiento de todos los componentes del core de MeriBot.

Módulos testados:
- logger: Sistema de logging centralizado
- config: Funciones de configuración
- json_formatter: Formateador JSON para logs
- validation: Validación de datos de entrada
- api.app: API FastAPI
- chatengine: Motor principal de conversación

Para ejecutar todos los tests:
    pytest meribot/core/test/unitarios/

Para ejecutar tests específicos:
    pytest meribot/core/test/unitarios/test_logger.py
    pytest meribot/core/test/unitarios/test_config.py -v
    pytest meribot/core/test/unitarios/test_api_app.py::TestHealthEndpoint
"""

__version__ = "1.0.0"
__author__ = "MeriBot Development Team"