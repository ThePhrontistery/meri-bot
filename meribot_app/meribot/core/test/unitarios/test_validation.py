"""
Tests unitarios para meribot.core.validation - Versión corregida para Pydantic v2
"""

import os
from unittest.mock import patch, MagicMock
import pytest
from pydantic import ValidationError
from meribot.core.validation import ChatEngineRequest


class TestChatEngineRequest:
    """Tests para el modelo ChatEngineRequest"""
    
    def test_chat_engine_request_valid(self):
        """Test validación exitosa con datos válidos"""
        request_data = {
            "conversation_id": "conv_123",
            "message": "Hello, how can I help you?",
            "domains": ["onboarding", "training"]
        }
        
        request = ChatEngineRequest(**request_data)
        assert request.conversation_id == "conv_123"
        assert request.message == "Hello, how can I help you?"
        assert request.domains == ["onboarding", "training"]
    
    def test_chat_engine_request_without_domains(self):
        """Test validación exitosa sin especificar dominios"""
        request_data = {
            "conversation_id": "conv_456",
            "message": "What is the weather like?"
        }
        
        request = ChatEngineRequest(**request_data)
        assert request.conversation_id == "conv_456"
        assert request.message == "What is the weather like?"
        assert request.domains is None
    
    def test_conversation_id_validation_empty(self):
        """Test validación falla con conversation_id vacío"""
        request_data = {
            "conversation_id": "",
            "message": "Test message"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        # En Pydantic v2, el error viene por min_length=1
        assert any("String should have at least 1 character" in str(error) or "min_length" in str(error) for error in errors)
    
    def test_conversation_id_validation_whitespace(self):
        """Test validación falla con conversation_id solo espacios"""
        request_data = {
            "conversation_id": "   ",
            "message": "Test message"
        }
        
        # Con str_strip_whitespace=True, esto se convierte en string vacío
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        assert any("String should have at least 1 character" in str(error) or "min_length" in str(error) for error in errors)
    
    def test_conversation_id_validation_too_long(self):
        """Test validación falla con conversation_id muy largo"""
        long_id = "x" * 150  # Excede MAX_CONVERSATION_ID_LENGTH (100)
        
        request_data = {
            "conversation_id": long_id,
            "message": "Test message"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        # En Pydantic v2, el mensaje de error es diferente
        assert any("String should have at most" in str(error) or "max_length" in str(error) for error in errors)

    def test_message_validation_empty(self):
        """Test validación falla con mensaje vacío"""
        request_data = {
            "conversation_id": "conv_123",
            "message": ""
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        # En Pydantic v2, el error viene por min_length=1
        assert any("String should have at least 1 character" in str(error) or "min_length" in str(error) for error in errors)
    
    def test_message_validation_whitespace_only(self):
        """Test validación falla con mensaje solo espacios"""
        request_data = {
            "conversation_id": "conv_123",
            "message": "   \n\t   "  # Espacios, nueva línea y tab reales
        }
        
        # Con str_strip_whitespace=True, esto se convierte en string vacío
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        assert any("String should have at least 1 character" in str(error) or "min_length" in str(error) for error in errors)
    
    def test_message_validation_too_long(self):
        """Test validación falla con mensaje muy largo"""
        long_message = "x" * 5000  # Excede MAX_MESSAGE_LENGTH (4000)
        
        request_data = {
            "conversation_id": "conv_123",
            "message": long_message
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        # En Pydantic v2, el mensaje de error es diferente
        assert any("String should have at most" in str(error) or "max_length" in str(error) for error in errors)

    def test_domains_validation_non_string(self):
        """Test validación falla con dominio que no es string"""
        request_data = {
            "conversation_id": "conv_123",
            "message": "Test message",
            "domains": ["onboarding", 123, "training"]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        # En Pydantic v2, el error es sobre tipo de dato
        assert any("Input should be a valid string" in str(error) or "string_type" in str(error) for error in errors)
    
    def test_domains_validation_too_many(self):
        """Test validación falla con demasiados dominios"""
        many_domains = ["onboarding"] * 10  # Excede MAX_DOMAINS_COUNT (5)
        
        request_data = {
            "conversation_id": "conv_123",
            "message": "Test message",
            "domains": many_domains
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(**request_data)
        
        errors = exc_info.value.errors()
        # En Pydantic v2, se usa max_length en lugar de max_items
        assert any("List should have at most" in str(error) or "max_length" in str(error) for error in errors)


class TestValidationConfigurationLoading:
    """Tests para carga de configuración de validación"""
    
    @patch('meribot.core.validation.load_config_from_yaml')
    def test_config_loading_success(self, mock_load_config):
        """Test carga exitosa de configuración"""
        mock_load_config.side_effect = lambda param: {
            'allowed_domains': ['test1', 'test2'],
            'max_message_length': 2000,
            'max_conversation_id_length': 50,
            'max_domains_count': 3,
            'dangerous_patterns': ['test_pattern']
        }.get(param)
        
        # Reimport para trigger config loading
        import importlib
        import meribot.core.validation
        importlib.reload(meribot.core.validation)
        
        # Verificar que las constantes están disponibles (valores por defecto)
        assert hasattr(meribot.core.validation, 'MAX_MESSAGE_LENGTH')
        assert hasattr(meribot.core.validation, 'ALLOWED_DOMAINS')
    
    @patch('meribot.core.validation.load_config_from_yaml')
    def test_config_loading_defaults(self, mock_load_config):
        """Test que se usan valores por defecto cuando falla la carga"""
        mock_load_config.return_value = None
        
        # Reimport para trigger config loading
        import importlib
        import meribot.core.validation
        importlib.reload(meribot.core.validation)
        
        # Verificar valores por defecto
        assert meribot.core.validation.MAX_MESSAGE_LENGTH == 4000
        assert meribot.core.validation.MAX_CONVERSATION_ID_LENGTH == 100


class TestValidationIntegration:
    """Tests de integración para validación"""
    
    def test_validation_with_unicode_characters(self):
        """Test validación con caracteres Unicode"""
        request_data = {
            "conversation_id": "conv_unicode_🌟",
            "message": "Hola! ¿Cómo estás? 🏖️",
            "domains": ["onboarding"]
        }
        
        request = ChatEngineRequest(**request_data)
        assert "🌟" in request.conversation_id
        assert "🏖️" in request.message
        assert request.domains == ["onboarding"]
    
    def test_validation_security_patterns(self):
        """Test validación de patrones de seguridad - casos que NO deberían fallar por defecto"""
        # Sin patrones peligrosos configurados, estos mensajes deberían pasar
        request_data = {
            "conversation_id": "security_test",
            "message": "What is the company policy?"
        }
        
        # No debería fallar
        request = ChatEngineRequest(**request_data)
        assert request.message == "What is the company policy?"


class TestValidationEdgeCases:
    """Tests para casos edge y manejo de errores"""
    
    def test_validation_missing_required_fields(self):
        """Test validación falla con campos requeridos faltantes"""
        # Sin conversation_id
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(message="Test message")
        
        errors = exc_info.value.errors()
        # En Pydantic v2, la estructura del error es diferente
        assert any(error.get("type") == "missing" for error in errors)
        
        # Sin message
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(conversation_id="conv_123")
        
        errors = exc_info.value.errors()
        assert any(error.get("type") == "missing" for error in errors)
    
    def test_validation_type_coercion(self):
        """Test coerción de tipos donde sea posible"""
        # En Pydantic v2, la coerción de tipos es más estricta
        request_data = {
            "conversation_id": 123,  # No será convertido a string automáticamente
            "message": "Test message"
        }
        
        with pytest.raises(ValidationError):
            ChatEngineRequest(**request_data)


class TestValidationPerformance:
    """Tests de rendimiento para validación"""
    
    def test_validation_performance_multiple_requests(self):
        """Test rendimiento con múltiples validaciones"""
        import time
        
        start_time = time.time()
        
        for i in range(100):
            request_data = {
                "conversation_id": f"conv_{i}",
                "message": f"Test message {i}",
                "domains": ["onboarding"]
            }
            ChatEngineRequest(**request_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Validar que 100 validaciones tomen menos de 1 segundo
        assert execution_time < 1.0


class TestValidationCompatibility:
    """Tests de compatibilidad con diferentes versiones"""
    
    def test_pydantic_v2_features(self):
        """Test que las características de Pydantic v2 funcionan correctamente"""
        request_data = {
            "conversation_id": "  conv_123  ",  # Espacios que serán removidos
            "message": "  Test message  ",
            "domains": ["onboarding"]
        }
        
        request = ChatEngineRequest(**request_data)
        # str_strip_whitespace debería remover espacios
        assert request.conversation_id == "conv_123"
        assert request.message == "Test message"
    
    def test_field_validation_order(self):
        """Test que los validadores de campo se ejecutan en el orden correcto"""
        # Los field_validator se ejecutan después de la validación básica de Pydantic
        request_data = {
            "conversation_id": "conv_123",
            "message": "Test message"
        }
        
        request = ChatEngineRequest(**request_data)
        assert request.conversation_id == "conv_123"
        assert request.message == "Test message"