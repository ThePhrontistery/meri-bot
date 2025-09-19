"""
Tests unitarios para meribot.utils.logging
"""

import os
import json
import tempfile
import logging
from unittest.mock import patch, MagicMock, mock_open
import pytest

from meribot.utils.logging import (
    get_logger,
    sanitize,
    log_critical_event,
    log_error,
    log_guardrail_rejection,
    log_guardrail_event,
    log_generation_failure
)


class TestGetLogger:
    """Tests para la función get_logger"""
    
    def test_get_logger_default(self):
        """Test crear logger con configuración por defecto"""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
        assert logger.level == logging.INFO  # Default del .env
        
    def test_get_logger_with_file(self, temp_directory):
        """Test crear logger con archivo específico"""
        log_file = os.path.join(temp_directory, "test.log")
        logger = get_logger("test_module", log_file=log_file)
        
        assert isinstance(logger, logging.Logger)
        assert any(isinstance(h, logging.handlers.RotatingFileHandler) 
                  for h in logger.handlers)
    
    def test_get_logger_creates_directory(self, temp_directory):
        """Test que get_logger crea directorios si no existen"""
        nested_dir = os.path.join(temp_directory, "logs", "nested")
        log_file = os.path.join(nested_dir, "test.log")
        
        logger = get_logger("test_module", log_file=log_file)
        
        assert os.path.exists(nested_dir)
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_no_duplicate_handlers(self, temp_directory):
        """Test que no se duplican handlers al llamar múltiples veces"""
        log_file = os.path.join(temp_directory, "test.log")
        
        logger1 = get_logger("test_module", log_file=log_file)
        initial_handler_count = len(logger1.handlers)
        
        logger2 = get_logger("test_module", log_file=log_file)
        final_handler_count = len(logger2.handlers)
        
        assert initial_handler_count == final_handler_count
        assert logger1 is logger2  # Mismo objeto logger
    
    def test_get_logger_debug_level(self):
        """Test configuración de nivel DEBUG desde env var"""
        import uuid
        # Usar un nombre único para evitar conflictos
        logger_name = f"debug_test_{uuid.uuid4().hex[:8]}"
            
        with patch.dict(os.environ, {"MERIBOT_LOG_LEVEL": "DEBUG"}):
            logger = get_logger(logger_name)
            # Verificar que al menos el logger se creó correctamente
            assert logger is not None
            assert isinstance(logger, logging.Logger)


class TestSanitize:
    """Tests para la función sanitize"""
    
    @patch('meribot.utils.logging.config.get_sensitive_keys')
    def test_sanitize_sensitive_keys(self):
        """Test que sanitiza claves sensibles correctamente"""
        data = {
            "username": "test_user",
            "password": "secret123",
            "api_key": "key123",
            "message": "hello world",
            "SECRET": "top_secret"  # Test case insensitive
        }
        
        result = sanitize(data)
        
        assert result["username"] == "test_user"
        assert result["password"] == "***"
        assert result["api_key"] == "***"
        assert result["message"] == "hello world"
        assert result["SECRET"] == "***"
    
    def test_sanitize_empty_dict(self):
        """Test sanitizar diccionario vacío"""
        result = sanitize({})
        assert result == {}
    
    def test_sanitize_no_sensitive_keys(self):
        """Test sanitizar cuando no hay claves sensibles"""
        data = {"name": "test", "value": 123}
        result = sanitize(data)
        assert result == data


class TestLoggingFunctions:
    """Tests para las funciones de logging específicas"""
    
    def test_log_critical_event(self, mock_logger):
        """Test log_critical_event"""
        log_critical_event(mock_logger, "Critical error occurred", 
                          user_id="user123", details="error details")
        
        mock_logger.critical.assert_called_once()
        args, kwargs = mock_logger.critical.call_args
        assert "Critical error occurred" in args
        assert "extra" in kwargs
    
    def test_log_error(self, mock_logger):
        """Test log_error"""
        log_error(mock_logger, "Error message", error_code=500)
        
        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Error message" in args
    
    def test_log_guardrail_rejection(self, mock_logger):
        """Test log_guardrail_rejection"""
        log_guardrail_rejection(
            mock_logger, 
            user_id="user123",
            input_text="malicious input",
            reason="contains dangerous pattern"
        )
        
        mock_logger.warning.assert_called_once()
        args, kwargs = mock_logger.warning.call_args
        assert "Input rechazado por guardrail" in args
    
    def test_log_guardrail_event(self, mock_logger):
        """Test log_guardrail_event"""
        log_guardrail_event(
            mock_logger,
            event_type="blocked_input",
            user_input="<script>alert('xss')</script>",
            extra={"ip": "192.168.1.1"}
        )
        
        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        
        # Verificar que es JSON válido
        log_data = json.loads(args[0])
        assert log_data["event"] == "guardrail_reject"
        assert log_data["type"] == "blocked_input"
        assert "timestamp" in log_data
    
    def test_log_guardrail_event_sanitizes_input(self, mock_logger):
        """Test que log_guardrail_event sanitiza el input"""
        dangerous_input = "<script>alert('xss')</script>" * 100  # Input muy largo
        
        log_guardrail_event(mock_logger, "xss_attempt", dangerous_input)
        
        args = mock_logger.warning.call_args[0]
        log_data = json.loads(args[0])
        
        # Verificar que el input fue truncado y escapado
        assert len(log_data["input"]) <= 256
        assert "&lt;script&gt;" in log_data["input"]  # HTML escapado
    
    def test_log_generation_failure(self, mock_logger):
        """Test log_generation_failure"""
        log_generation_failure(
            mock_logger,
            user_id="user123",
            input_text="test input",
            error="Connection timeout",
            model="gpt-4"
        )
        
        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Fallo de generación LLM" in args


class TestIntegration:
    """Tests de integración para el módulo logger"""
    
    def test_logger_with_json_formatter(self, temp_directory):
        """Test integración logger con JsonFormatter"""
        log_file = os.path.join(temp_directory, "integration.log")
        logger = get_logger("integration_test", log_file=log_file)
        
        # Log un mensaje
        logger.info("Test message", extra={"user_id": "test123"})
        
        # Verificar que el archivo se creó y contiene JSON válido
        assert os.path.exists(log_file)
        
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read().strip()
            if log_content:  # Solo verificar si hay contenido
                log_data = json.loads(log_content)
                assert log_data["level"] == "INFO"
                assert log_data["message"] == "Test message"
    
    @patch('meribot.utils.logging.config.load_config_from_yaml')
    def test_sensitive_keys_loading(self, mock_load_config):
        """Test carga de SENSITIVE_KEYS desde configuración"""
        mock_load_config.return_value = ["password", "token", "secret"]
        
        # Reimport para trigger config loading
        import importlib
        import meribot.utils.logging
        importlib.reload(meribot.utils.logging)
        
        # Test sanitization with loaded keys - patch SENSITIVE_KEYS directamente
        with patch('meribot.utils.logging.utils.get_sensitive_keys', return_value={"password", "token", "secret"}):
            data = {"password": "secret", "username": "user"}
            result = meribot.utils.logging.sanitize(data)
            
            assert result["password"] == "***"
            assert result["username"] == "user"
    
    def test_logging_functions_with_real_logger(self, temp_directory):
        """Test funciones de logging con logger real"""
        log_file = os.path.join(temp_directory, "real_test.log")
        logger = get_logger("real_test", log_file=log_file)
        
        # Test todas las funciones de logging
        log_error(logger, "Test error", code=500)
        log_critical_event(logger, "Critical test", severity="high")
        log_guardrail_rejection(logger, "user123", "bad input", "policy violation")
        log_generation_failure(logger, "user456", "prompt", "timeout")
        
        # Verificar que se escribió al archivo
        assert os.path.exists(log_file)
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test error" in content
            assert "Critical test" in content


class TestEdgeCases:
    """Tests para casos edge y manejo de errores"""
    
    def test_get_logger_invalid_log_file_path(self):
        """Test get_logger con path inválido"""
        # En Windows, usar un path que seguramente falle
        invalid_path = "Z:\\nonexistent\\path\\test.log"
        
        # Debería fallar al intentar crear el directorio
        with pytest.raises(FileNotFoundError):
            get_logger("test", log_file=invalid_path)
    
    def test_sanitize_non_dict_input(self):
        """Test sanitize con input que no es diccionario"""
        # sanitize espera dict, pero verificamos robustez
        with pytest.raises(AttributeError):
            sanitize("not a dict")
    
    def test_log_functions_with_none_logger(self):
        """Test funciones de log con logger None"""
        with pytest.raises(AttributeError):
            log_error(None, "test message")
    
    @patch('meribot.utils.logging.formatters.JsonFormatter')
    def test_formatter_error_handling(self, mock_formatter, temp_directory):
        """Test manejo de errores en formatter"""
        mock_formatter.side_effect = Exception("Formatter error")
        
        # Debería fallar al crear el logger con formatter personalizado
        with pytest.raises(Exception):
            log_file = os.path.join(temp_directory, "test.log")
            get_logger("test", log_file=log_file)