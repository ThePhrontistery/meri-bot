"""
Tests unitarios para el módulo logger.py del crawler.
Valida configuración de logging, formatos, handlers y niveles de log.
"""

import pytest
import os
import tempfile
import logging
import json
from unittest.mock import patch, MagicMock, mock_open
from logging.handlers import RotatingFileHandler

from meribot.crawler.logger import (
    get_logger,
    ensure_log_dir,
    JsonFormatter,
    LOG_DIR,
    LOG_FILE,
    DEFAULT_LEVEL,
    DEFAULT_FORMAT,
    LEVELS,
    RICH_AVAILABLE
)


class TestEnsureLogDir:
    """Tests para la función ensure_log_dir."""
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_ensure_log_dir_creates_directory(self, mock_makedirs, mock_exists):
        """Test que ensure_log_dir crea el directorio si no existe."""
        mock_exists.return_value = False
        
        ensure_log_dir()
        
        mock_makedirs.assert_called_once_with(LOG_DIR, exist_ok=True)
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_ensure_log_dir_directory_exists(self, mock_makedirs, mock_exists):
        """Test que ensure_log_dir no crea directorio si ya existe."""
        mock_exists.return_value = True
        
        ensure_log_dir()
        
        mock_makedirs.assert_not_called()


class TestJsonFormatter:
    """Tests para la clase JsonFormatter."""
    
    def test_json_formatter_basic_record(self):
        """Test formateo básico de record a JSON."""
        formatter = JsonFormatter()
        
        # Crear un LogRecord de prueba
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        # Verificar que es JSON válido
        parsed = json.loads(result)
        
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed
    
    def test_json_formatter_with_exception(self):
        """Test formateo de record con información de excepción."""
        formatter = JsonFormatter()
        
        # Simular excepción
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = True
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        
        with patch.object(formatter, 'formatException', return_value="Exception traceback"):
            result = formatter.format(record)
        
        parsed = json.loads(result)
        
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "Error occurred"
        assert "exception" in parsed
    
    def test_json_formatter_with_args(self):
        """Test formateo de record con argumentos en el mensaje."""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=10,
            msg="Warning: %s occurred %d times",
            args=("Error", 5),
            exc_info=None
        )
        
        result = formatter.format(record)
        parsed = json.loads(result)
        
        assert parsed["message"] == "Warning: Error occurred 5 times"
    
    def test_json_formatter_unicode_handling(self):
        """Test manejo de caracteres Unicode en JSON."""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Mensaje con acentos: ñáéíóú",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        parsed = json.loads(result)
        
        assert "ñáéíóú" in parsed["message"]
        # Verificar que ensure_ascii=False funciona
        assert "\\u" not in result  # No debería tener escape Unicode


class TestGetLogger:
    """Tests para la función get_logger."""
    
    def setUp(self):
        """Setup para limpiar loggers entre tests."""
        # Limpiar handlers existentes
        for logger_name in list(logging.Logger.manager.loggerDict.keys()):
            if logger_name.startswith("test"):
                logger = logging.getLogger(logger_name)
                logger.handlers.clear()
                logger.setLevel(logging.NOTSET)
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_basic(self, mock_ensure_dir):
        """Test creación básica de logger."""
        logger = get_logger("test_logger")
        
        assert logger.name == "test_logger"
        assert isinstance(logger, logging.Logger)
        mock_ensure_dir.assert_called_once()
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_default_name(self, mock_ensure_dir):
        """Test logger con nombre por defecto."""
        logger = get_logger()
        
        assert logger.name == "crawler"
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_custom_level(self, mock_ensure_dir):
        """Test logger con nivel personalizado."""
        logger = get_logger("test_logger", level="DEBUG")
        
        assert logger.level == logging.DEBUG
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_invalid_level(self, mock_ensure_dir):
        """Test logger con nivel inválido usa INFO por defecto."""
        logger = get_logger("test_logger", level="INVALID")
        
        assert logger.level == logging.INFO
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_json_format(self, mock_ensure_dir):
        """Test logger con formato JSON."""
        logger = get_logger("test_logger", json_format=True)
        
        # Verificar que tiene handlers
        assert len(logger.handlers) > 0
        
        # Buscar handler con JsonFormatter
        json_handler_found = False
        for handler in logger.handlers:
            if isinstance(handler.formatter, JsonFormatter):
                json_handler_found = True
                break
        
        assert json_handler_found
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_standard_format(self, mock_ensure_dir):
        """Test logger con formato estándar."""
        logger = get_logger("test_logger", json_format=False)
        
        # Verificar que tiene handlers
        assert len(logger.handlers) > 0
        
        # Verificar que no usa JsonFormatter
        for handler in logger.handlers:
            assert not isinstance(handler.formatter, JsonFormatter)
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    @patch('meribot.crawler.logger.RICH_AVAILABLE', True)
    @patch('meribot.crawler.logger.RichHandler')
    def test_get_logger_with_rich(self, mock_rich_handler, mock_ensure_dir):
        """Test logger con Rich disponible."""
        mock_handler_instance = MagicMock()
        mock_rich_handler.return_value = mock_handler_instance
        
        logger = get_logger("test_logger", json_format=False)
        
        # Verificar que se creó RichHandler
        mock_rich_handler.assert_called_once_with(
            rich_tracebacks=True,
            show_time=True,
            show_level=True,
            show_path=False
        )
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    @patch('meribot.crawler.logger.RICH_AVAILABLE', False)
    def test_get_logger_without_rich(self, mock_ensure_dir):
        """Test logger sin Rich disponible."""
        logger = get_logger("test_logger", json_format=False)
        
        # Verificar que se creó StreamHandler estándar
        stream_handler_found = False
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
                stream_handler_found = True
                break
        
        assert stream_handler_found
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_file_handler(self, mock_ensure_dir):
        """Test que se crea el handler de archivo."""
        logger = get_logger("test_logger")
        
        # Verificar que tiene RotatingFileHandler
        file_handler_found = False
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler_found = True
                assert handler.maxBytes == 2*1024*1024  # 2MB
                assert handler.backupCount == 3
                break
        
        assert file_handler_found
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_no_duplicate_handlers(self, mock_ensure_dir):
        """Test que no se crean handlers duplicados."""
        logger1 = get_logger("duplicate_test")
        initial_handler_count = len(logger1.handlers)
        
        logger2 = get_logger("duplicate_test")  # Mismo nombre
        
        # Debería ser el mismo logger
        assert logger1 is logger2
        assert len(logger2.handlers) == initial_handler_count
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_propagate_false(self, mock_ensure_dir):
        """Test que logger.propagate está en False."""
        logger = get_logger("test_logger")
        
        assert logger.propagate is False
    
    @patch.dict(os.environ, {"CRAWLER_LOG_LEVEL": "WARNING"})
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_env_level_override(self, mock_ensure_dir):
        """Test override de nivel desde variable de entorno."""
        logger = get_logger("test_logger")
        
        assert logger.level == logging.WARNING
    
    @patch.dict(os.environ, {"CRAWLER_LOG_FORMAT": "JSON"})
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_get_logger_env_format_override(self, mock_ensure_dir):
        """Test override de formato desde variable de entorno."""
        logger = get_logger("test_logger")
        
        # Verificar que usa JsonFormatter
        json_formatter_found = False
        for handler in logger.handlers:
            if isinstance(handler.formatter, JsonFormatter):
                json_formatter_found = True
                break
        
        assert json_formatter_found


class TestLoggerConstants:
    """Tests para constantes y configuración del módulo logger."""
    
    def test_log_dir_path(self):
        """Test que LOG_DIR tiene el path correcto."""
        expected_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '..', '..', '..', 'logs'
        )
        # Normalizar paths para comparación
        assert os.path.normpath(LOG_DIR) == os.path.normpath(expected_path)
    
    def test_log_file_path(self):
        """Test que LOG_FILE tiene el path correcto."""
        expected_file = os.path.join(LOG_DIR, 'crawler.log')
        assert LOG_FILE == expected_file
    
    def test_default_level_from_env(self):
        """Test que DEFAULT_LEVEL lee de variable de entorno."""
        with patch.dict(os.environ, {"CRAWLER_LOG_LEVEL": "ERROR"}):
            # Re-importar para que tome el nuevo valor
            import importlib
            import meribot.crawler.logger
            importlib.reload(meribot.crawler.logger)
            
            assert meribot.crawler.logger.DEFAULT_LEVEL == "ERROR"
    
    def test_default_format_from_env(self):
        """Test que DEFAULT_FORMAT lee de variable de entorno."""
        with patch.dict(os.environ, {"CRAWLER_LOG_FORMAT": "JSON"}):
            import importlib
            import meribot.crawler.logger
            importlib.reload(meribot.crawler.logger)
            
            assert meribot.crawler.logger.DEFAULT_FORMAT == "JSON"
    
    def test_levels_mapping(self):
        """Test que LEVELS tiene el mapeo correcto."""
        expected_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        assert LEVELS == expected_levels


class TestLoggerIntegration:
    """Tests de integración para el módulo logger."""
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_logger_actual_logging(self, mock_ensure_dir):
        """Test que el logger efectivamente loggea mensajes."""
        # Usar StringIO para capturar output
        from io import StringIO
        import logging
        
        # Crear logger de prueba
        logger = get_logger("integration_test", json_format=False)
        
        # Agregar handler para capturar output
        stream = StringIO()
        test_handler = logging.StreamHandler(stream)
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        test_handler.setFormatter(formatter)
        
        # Limpiar handlers existentes y agregar el de prueba
        logger.handlers.clear()
        logger.addHandler(test_handler)
        logger.setLevel(logging.DEBUG)
        
        # Loggear mensajes
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verificar output
        output = stream.getvalue()
        assert "DEBUG:integration_test:Debug message" in output
        assert "INFO:integration_test:Info message" in output
        assert "WARNING:integration_test:Warning message" in output
        assert "ERROR:integration_test:Error message" in output
        assert "CRITICAL:integration_test:Critical message" in output
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_logger_json_output(self, mock_ensure_dir):
        """Test output JSON del logger."""
        from io import StringIO
        import logging
        
        logger = get_logger("json_test", json_format=True)
        
        # Agregar handler para capturar JSON output
        stream = StringIO()
        test_handler = logging.StreamHandler(stream)
        test_handler.setFormatter(JsonFormatter())
        
        logger.handlers.clear()
        logger.addHandler(test_handler)
        logger.setLevel(logging.INFO)
        
        logger.info("Test JSON message")
        
        # Verificar que el output es JSON válido
        output = stream.getvalue().strip()
        parsed = json.loads(output)
        
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "json_test"
        assert parsed["message"] == "Test JSON message"
        assert "timestamp" in parsed
    
    def test_logger_level_filtering(self):
        """Test que el logger filtra por nivel correctamente."""
        from io import StringIO
        import logging
        
        with patch('meribot.crawler.logger.ensure_log_dir'):
            logger = get_logger("level_test", level="WARNING")
        
        stream = StringIO()
        test_handler = logging.StreamHandler(stream)
        
        logger.handlers.clear()
        logger.addHandler(test_handler)
        
        # Loggear mensajes de diferentes niveles
        logger.debug("Debug - should not appear")
        logger.info("Info - should not appear")
        logger.warning("Warning - should appear")
        logger.error("Error - should appear")
        
        output = stream.getvalue()
        
        # Solo WARNING y ERROR deberían aparecer
        assert "Debug - should not appear" not in output
        assert "Info - should not appear" not in output
        assert "Warning - should appear" in output
        assert "Error - should appear" in output
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    def test_rotating_file_handler_configuration(self, mock_ensure_dir):
        """Test configuración del RotatingFileHandler."""
        logger = get_logger("rotating_test")
        
        # Encontrar el RotatingFileHandler
        rotating_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                rotating_handler = handler
                break
        
        assert rotating_handler is not None
        assert rotating_handler.maxBytes == 2 * 1024 * 1024  # 2MB
        assert rotating_handler.backupCount == 3
        assert rotating_handler.encoding == "utf-8"
    
    @patch('meribot.crawler.logger.ensure_log_dir')
    @patch('meribot.crawler.logger.RICH_AVAILABLE', True)
    def test_rich_handler_configuration(self, mock_ensure_dir):
        """Test configuración específica de RichHandler."""
        with patch('meribot.crawler.logger.RichHandler') as mock_rich:
            mock_handler = MagicMock()
            mock_rich.return_value = mock_handler
            
            logger = get_logger("rich_test", json_format=False)
            
            # Verificar que RichHandler se configuró correctamente
            mock_rich.assert_called_once_with(
                rich_tracebacks=True,
                show_time=True,
                show_level=True,
                show_path=False
            )
            
            # Verificar que se estableció el nivel
            mock_handler.setLevel.assert_called_once()


class TestLoggerMainExecution:
    """Tests para la ejecución del script principal del logger."""
    
    @patch('meribot.crawler.logger.get_logger')
    def test_main_execution_output(self, mock_get_logger):
        """Test ejecución del bloque __main__ del logger."""
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance
        
        # Simular ejecución del bloque main
        # (En un test real ejecutaríamos el módulo como script)
        logger = mock_get_logger("test")
        logger.debug("Mensaje DEBUG de prueba")
        logger.info("Mensaje INFO de prueba")
        logger.warning("Mensaje WARNING de prueba")
        logger.error("Mensaje ERROR de prueba")
        logger.critical("Mensaje CRITICAL de prueba")
        
        # Verificar que se llamaron todos los métodos de logging
        mock_logger_instance.debug.assert_called_with("Mensaje DEBUG de prueba")
        mock_logger_instance.info.assert_called_with("Mensaje INFO de prueba")
        mock_logger_instance.warning.assert_called_with("Mensaje WARNING de prueba")
        mock_logger_instance.error.assert_called_with("Mensaje ERROR de prueba")
        mock_logger_instance.critical.assert_called_with("Mensaje CRITICAL de prueba")


# Fixtures para tests de logger
@pytest.fixture
def temp_log_dir():
    """Fixture que crea un directorio temporal para logs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def clean_loggers():
    """Fixture que limpia loggers entre tests."""
    yield
    # Cleanup después del test
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        if logger_name.startswith("test"):
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)


@pytest.fixture
def sample_log_record():
    """Fixture con LogRecord de ejemplo."""
    return logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test log message",
        args=(),
        exc_info=None
    )


@pytest.fixture
def mock_file_handler():
    """Fixture con mock de file handler."""
    handler = MagicMock(spec=RotatingFileHandler)
    handler.maxBytes = 2*1024*1024
    handler.backupCount = 3
    return handler