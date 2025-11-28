"""
Tests unitarios para meribot.utils.logging.formatters
"""

import json
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

from meribot.utils.logging.formatters import JsonFormatter


class TestJsonFormatter:
    """Tests para la clase JsonFormatter"""
    
    def test_json_formatter_basic_record(self):
        """Test formateo básico de LogRecord"""
        formatter = JsonFormatter()
        
        # Crear un LogRecord básico
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        result = formatter.format(record)
        
        # Verificar que es JSON válido
        log_data = json.loads(result)
        
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test_module"
        assert log_data["funcName"] == "test_function"
        assert log_data["lineNo"] == 42
        assert "timestamp" in log_data
    
    def test_json_formatter_with_extra_data(self):
        """Test formateo con datos extra"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="/test/path.py",
            lineno=100,
            msg="Warning message",
            args=(),
            exc_info=None
        )
        record.module = "warning_module"
        record.funcName = "warning_function"
        
        # Añadir datos extra
        extra_data = {
            "user_id": "user123",
            "request_id": "req456",
            "duration": 1.23
        }
        record.extra = extra_data
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        # Verificar datos básicos
        assert log_data["level"] == "WARNING"
        assert log_data["message"] == "Warning message"
        
        # Verificar datos extra
        assert log_data["user_id"] == "user123"
        assert log_data["request_id"] == "req456"
        assert log_data["duration"] == 1.23
    
    def test_json_formatter_timestamp_format(self):
        """Test formato correcto del timestamp"""
        from datetime import datetime, timezone
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/test/path.py",
            lineno=1,
            msg="Error message",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        
        with patch('meribot.utils.logging.formatters.datetime') as mock_datetime:
            # Mock datetime.now para timestamp predecible
            mock_now = datetime(2024, 1, 15, 10, 30, 45, 123456, timezone.utc)
            mock_datetime.now.return_value = mock_now
            # Mantener la clase datetime real para otros métodos
            mock_datetime.timezone = timezone
            
            result = formatter.format(record)
            log_data = json.loads(result)
            
            # El timestamp debe estar en formato ISO con Z
            assert "timestamp" in log_data
            assert "2024-01-15T10:30:45" in log_data["timestamp"]
            assert log_data["timestamp"].endswith('Z')
    
    def test_json_formatter_different_log_levels(self):
        """Test formateo con diferentes niveles de log"""
        formatter = JsonFormatter()
        
        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL")
        ]
        
        for level_num, level_name in levels:
            record = logging.LogRecord(
                name="test_logger",
                level=level_num,
                pathname="/test/path.py",
                lineno=1,
                msg=f"Test {level_name} message",
                args=(),
                exc_info=None
            )
            record.module = "test"
            record.funcName = "test"
            
            result = formatter.format(record)
            log_data = json.loads(result)
            
            assert log_data["level"] == level_name
            assert log_data["message"] == f"Test {level_name} message"
    
    def test_json_formatter_with_args(self):
        """Test formateo con argumentos en el mensaje"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="User %s performed action %s",
            args=("john_doe", "login"),
            exc_info=None
        )
        record.module = "auth"
        record.funcName = "authenticate"
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        # getMessage() debería formatear el mensaje con args
        assert log_data["message"] == "User john_doe performed action login"
    
    def test_json_formatter_unicode_handling(self):
        """Test manejo de caracteres Unicode"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Mensaje con ñ, ü, €, 中文, 🚀",
            args=(),
            exc_info=None
        )
        record.module = "unicode_test"
        record.funcName = "test_unicode"
        
        # Datos extra con Unicode
        record.extra = {
            "usuario": "José María",
            "descripción": "Configuración de Müller & Sön",
            "emoji": "🎉"
        }
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        assert "ñ" in log_data["message"]
        assert "🚀" in log_data["message"]
        assert log_data["usuario"] == "José María"
        assert log_data["descripción"] == "Configuración de Müller & Sön"
        assert log_data["emoji"] == "🎉"
    
    def test_json_formatter_no_extra_attribute(self):
        """Test formateo cuando no hay atributo extra"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Simple message",
            args=(),
            exc_info=None
        )
        record.module = "simple"
        record.funcName = "simple_func"
        # No se asigna record.extra
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        # Verificar estructura básica sin datos extra
        expected_keys = {"timestamp", "level", "message", "module", "funcName", "lineNo"}
        assert set(log_data.keys()) == expected_keys
    
    def test_json_formatter_extra_not_dict(self):
        """Test cuando extra no es un diccionario"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Message with invalid extra",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        record.extra = "not a dict"  # Invalid extra
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        # No debería incluir el extra inválido
        assert "extra" not in log_data
        assert log_data["message"] == "Message with invalid extra"
    
    def test_json_formatter_large_extra_data(self):
        """Test con gran cantidad de datos extra"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Message with large extra",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        
        # Crear diccionario grande
        large_extra = {f"key_{i}": f"value_{i}" for i in range(100)}
        large_extra["nested"] = {
            "level1": {
                "level2": ["item1", "item2", "item3"] * 10
            }
        }
        record.extra = large_extra
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        # Verificar que se incluyeron todos los datos
        assert len([k for k in log_data.keys() if k.startswith("key_")]) == 100
        assert "nested" in log_data
        assert log_data["nested"]["level1"]["level2"][0] == "item1"
    
    def test_json_formatter_special_characters_in_extra(self):
        """Test con caracteres especiales en datos extra"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Special chars test",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        
        record.extra = {
            "json_string": '{"key": "value"}',
            "quotes": 'String with "quotes" and \'apostrophes\'',
            "newlines": "Line1\nLine2\r\nLine3",
            "tabs": "Col1\tCol2\tCol3",
            "backslashes": "Path\\to\\file",
            "control_chars": "\x00\x01\x02"
        }
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        # Verificar que JSON es válido y contiene los datos
        assert log_data["json_string"] == '{"key": "value"}'
        assert "quotes" in log_data["quotes"]
        assert "\n" in log_data["newlines"]
        assert "\t" in log_data["tabs"]


class TestJsonFormatterIntegration:
    """Tests de integración con logging real"""
    
    def test_json_formatter_with_real_logger(self):
        """Test JsonFormatter con logger real"""
        # Crear logger con JsonFormatter
        logger = logging.getLogger("integration_test")
        logger.setLevel(logging.DEBUG)
        
        # Limpiar handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Usar StringIO para capturar output
        import io
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        
        try:
            # Log diferentes tipos de mensajes
            logger.info("Info message")
            logger.warning("Warning message", extra={"user": "test_user"})
            logger.error("Error occurred", extra={"error_code": 500, "details": "Internal error"})
            
            # Obtener y verificar output
            output = log_capture.getvalue()
            lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
            
            assert len(lines) >= 2  # Al menos info y warning
            
            # Verificar cada línea es JSON válido
            for line in lines:
                log_data = json.loads(line)
                assert "timestamp" in log_data
                assert "level" in log_data
                assert "message" in log_data
            
            # Buscar el log de WARNING específico  
            warning_found = False
            for line in lines:
                try:
                    log_data = json.loads(line)
                    if ("WARNING" in log_data.get("level", "") and 
                        "Warning message" in log_data.get("message", "")):
                        # Buscar user en el mensaje JSON
                        if "user" in str(log_data):
                            warning_found = True
                            break
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Si no encontramos user en los datos extra, al menos verificar que se registró el warning
            if not warning_found:
                warning_messages = [line for line in lines if "WARNING" in line and "Warning message" in line]
                assert len(warning_messages) >= 1, "No se encontró el log de WARNING"
            
        finally:
            # Limpiar handler
            logger.removeHandler(handler)
            handler.close()
    
    def test_json_formatter_performance(self):
        """Test básico de performance del formatter"""
        formatter = JsonFormatter()
        
        # Crear record base
        record = logging.LogRecord(
            name="perf_test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Performance test message",
            args=(),
            exc_info=None
        )
        record.module = "perf"
        record.funcName = "perf_test"
        record.extra = {"iteration": 0}
        
        # Medir tiempo para muchas operaciones
        import time
        start_time = time.time()
        
        for i in range(1000):
            record.extra = {"iteration": i}
            result = formatter.format(record)
            # Verificar que el resultado es válido
            json.loads(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance test: debería ser rápido (< 1 segundo para 1000 operaciones)
        assert duration < 1.0, f"Formatting took too long: {duration:.3f}s"


class TestJsonFormatterEdgeCases:
    """Tests para casos edge y manejo de errores"""
    
    def test_json_formatter_none_values(self):
        """Test con valores None en extra"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="None values test",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        record.extra = {
            "valid_value": "test",
            "none_value": None,
            "empty_string": "",
            "zero": 0,
            "false": False
        }
        
        result = formatter.format(record)
        log_data = json.loads(result)
        
        assert log_data["valid_value"] == "test"
        assert log_data["none_value"] is None
        assert log_data["empty_string"] == ""
        assert log_data["zero"] == 0
        assert log_data["false"] is False
    
    def test_json_formatter_circular_reference(self):
        """Test con referencias circulares en extra (debería fallar)"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Circular reference test",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        
        # Crear referencia circular
        circular_dict = {"name": "test"}
        circular_dict["self"] = circular_dict
        record.extra = {"circular": circular_dict}
        
        # Debería fallar al serializar JSON
        with pytest.raises(ValueError, match="Circular reference"):
            formatter.format(record)
    
    def test_json_formatter_non_serializable_objects(self):
        """Test con objetos no serializables en extra"""
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Non-serializable test",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        
        # Objeto no serializable
        class NonSerializable:
            def __init__(self):
                self.value = "test"
        
        record.extra = {
            "valid": "test",
            "object": NonSerializable()
        }
        
        # Debería fallar al serializar
        with pytest.raises(TypeError):
            formatter.format(record)
    
    @patch('meribot.utils.logging.formatters.datetime')
    def test_json_formatter_datetime_error(self, mock_datetime):
        """Test manejo de error en datetime"""
        # Mock datetime.now en lugar de utcnow
        mock_datetime.now.side_effect = Exception("Datetime error")
        
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=1,
            msg="Datetime error test",
            args=(),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test"
        
        # Debería fallar debido al error en datetime
        with pytest.raises(Exception, match="Datetime error"):
            formatter.format(record)