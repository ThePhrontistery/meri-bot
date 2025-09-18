"""
test_validation.py
Tests unitarios para el módulo validation de MeriBot.
Valida la validación de datos de entrada usando Pydantic.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from pydantic import ValidationError

from meribot.core.validation import ChatEngineRequest


class TestChatEngineRequest:
    """Test suite para la clase ChatEngineRequest."""

    @pytest.fixture
    def valid_request_data(self):
        """Datos válidos para request."""
        return {
            "conversation_id": "test_conversation_123",
            "message": "¿Cuáles son las políticas de onboarding?",
            "domains": ["onboarding", "training"]
        }

    @pytest.fixture
    def mock_config_valid(self):
        """Mock de configuración válida."""
        return {
            'allowed_domains': ['onboarding', 'training', 'cca', 'sdo'],
            'max_message_length': 4000,
            'max_conversation_id_length': 100,
            'max_domains_count': 5,
            'dangerous_patterns': ['<script', 'javascript:', 'eval(']
        }

    @pytest.mark.unit
    @pytest.mark.validation
    def test_chat_engine_request_valid_full(self, valid_request_data, temp_config_file):
        """Test de validación exitosa con todos los campos."""
        request = ChatEngineRequest(**valid_request_data)
        
        assert request.conversation_id == "test_conversation_123"
        assert request.message == "¿Cuáles son las políticas de onboarding?"
        assert request.domains == ["onboarding", "training"]

    @pytest.mark.unit
    @pytest.mark.validation
    def test_chat_engine_request_minimal_valid(self, temp_config_file):
        """Test de validación exitosa con campos mínimos."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message"
        )
        
        assert request.conversation_id == "test_123"
        assert request.message == "Test message"
        assert request.domains is None

    @pytest.mark.unit
    @pytest.mark.validation
    def test_conversation_id_validation_empty_fails(self, temp_config_file):
        """Test que conversation_id vacío falla."""
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="",
                message="Test message"
            )
        
        errors = exc_info.value.errors()
        assert any("conversation_id no puede estar vacío" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_conversation_id_validation_whitespace_only_fails(self, temp_config_file):
        """Test que conversation_id solo con espacios falla."""
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="   ",
                message="Test message"
            )
        
        errors = exc_info.value.errors()
        assert any("conversation_id no puede estar vacío" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_conversation_id_validation_too_long_fails(self, temp_config_file):
        """Test que conversation_id demasiado largo falla."""
        long_id = "x" * 101  # Excede MAX_CONVERSATION_ID_LENGTH (100)
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id=long_id,
                message="Test message"
            )
        
        errors = exc_info.value.errors()
        assert any("ensure this value has at most 100 characters" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_conversation_id_validation_strips_whitespace(self, temp_config_file):
        """Test que conversation_id elimina espacios en blanco."""
        request = ChatEngineRequest(
            conversation_id="  test_id  ",
            message="Test message"
        )
        
        assert request.conversation_id == "test_id"

    @pytest.mark.unit
    @pytest.mark.validation
    def test_message_validation_empty_fails(self, temp_config_file):
        """Test que mensaje vacío falla."""
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="test_123",
                message=""
            )
        
        errors = exc_info.value.errors()
        assert any("El mensaje no puede estar vacío" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_message_validation_whitespace_only_fails(self, temp_config_file):
        """Test que mensaje solo con espacios falla."""
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="test_123",
                message="   \n\t   "
            )
        
        errors = exc_info.value.errors()
        assert any("El mensaje no puede contener solo espacios en blanco" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_message_validation_too_long_fails(self, temp_config_file):
        """Test que mensaje demasiado largo falla."""
        long_message = "x" * 4001  # Excede MAX_MESSAGE_LENGTH (4000)
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="test_123",
                message=long_message
            )
        
        errors = exc_info.value.errors()
        assert any("excede la longitud máxima permitida" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_message_validation_dangerous_patterns_fail(self, temp_config_file):
        """Test que mensajes con patrones peligrosos fallan."""
        dangerous_messages = [
            "Hola <script>alert('xss')</script>",
            "Test javascript:void(0)",
            "Mensaje con eval(malicious_code)"
        ]
        
        for dangerous_msg in dangerous_messages:
            with pytest.raises(ValidationError) as exc_info:
                ChatEngineRequest(
                    conversation_id="test_123",
                    message=dangerous_msg
                )
            
            errors = exc_info.value.errors()
            assert any("patrones potencialmente peligrosos" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_message_validation_strips_whitespace(self, temp_config_file):
        """Test que mensaje elimina espacios en blanco."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="  Test message  "
        )
        
        assert request.message == "Test message"

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_none_allowed(self, temp_config_file):
        """Test que domains None es válido."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=None
        )
        
        assert request.domains is None

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_empty_list_allowed(self, temp_config_file):
        """Test que lista vacía de dominios es válida."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=[]
        )
        
        assert request.domains == []

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_valid_domains(self, temp_config_file):
        """Test de validación exitosa de dominios válidos."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=["onboarding", "training", "cca"]
        )
        
        assert request.domains == ["onboarding", "training", "cca"]

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_invalid_domain_fails(self, temp_config_file):
        """Test que dominios inválidos fallan."""
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="test_123",
                message="Test message",
                domains=["onboarding", "invalid_domain"]
            )
        
        errors = exc_info.value.errors()
        assert any("Dominio no permitido" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_too_many_domains_fails(self, temp_config_file):
        """Test que demasiados dominios falla."""
        many_domains = ["onboarding", "training", "cca", "sdo", "extra1", "extra2"]  # Excede MAX_DOMAINS_COUNT (5)
        
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="test_123",
                message="Test message",
                domains=many_domains
            )
        
        errors = exc_info.value.errors()
        assert any("ensure this value has at most 5 items" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_normalizes_case(self, temp_config_file):
        """Test que dominios se normalizan a minúsculas."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=["ONBOARDING", "Training", "CCA"]
        )
        
        assert request.domains == ["onboarding", "training", "cca"]

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_removes_duplicates(self, temp_config_file):
        """Test que se eliminan dominios duplicados."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=["onboarding", "training", "onboarding", "cca", "training"]
        )
        
        # Debería mantener el orden y eliminar duplicados
        assert request.domains == ["onboarding", "training", "cca"]

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_empty_domain_fails(self, temp_config_file):
        """Test que dominio vacío falla."""
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="test_123",
                message="Test message",
                domains=["onboarding", "", "training"]
            )
        
        errors = exc_info.value.errors()
        assert any("Los dominios no pueden estar vacíos" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_non_string_domain_fails(self, temp_config_file):
        """Test que dominio no string falla."""
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(
                conversation_id="test_123",
                message="Test message",
                domains=["onboarding", 123, "training"]
            )
        
        errors = exc_info.value.errors()
        assert any("Cada dominio debe ser una cadena de texto" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_validation_strips_whitespace(self, temp_config_file):
        """Test que dominios eliminan espacios en blanco."""
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=["  onboarding  ", " training ", "cca"]
        )
        
        assert request.domains == ["onboarding", "training", "cca"]

    @pytest.mark.unit
    @pytest.mark.validation
    def test_missing_required_fields_fail(self):
        """Test que campos requeridos faltantes fallan."""
        # Falta conversation_id
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(message="Test message")
        
        errors = exc_info.value.errors()
        assert any(error['type'] == 'missing' for error in errors)
        
        # Falta message
        with pytest.raises(ValidationError) as exc_info:
            ChatEngineRequest(conversation_id="test_123")
        
        errors = exc_info.value.errors()
        assert any(error['type'] == 'missing' for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    @patch('meribot.core.validation.load_config_from_yaml')
    def test_config_loading_failure_uses_defaults(self, mock_load_config):
        """Test que falla de configuración usa valores por defecto."""
        mock_load_config.return_value = None
        
        # Debería usar valores por defecto cuando la configuración falla
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=["onboarding"]  # Debería usar dominios por defecto
        )
        
        assert request.domains == ["onboarding"]

    @pytest.mark.unit
    @pytest.mark.validation
    def test_field_descriptions_present(self):
        """Test que los campos tienen descripciones."""
        schema = ChatEngineRequest.schema()
        properties = schema['properties']
        
        assert 'description' in properties['conversation_id']
        assert 'description' in properties['message']
        assert 'description' in properties['domains']
        
        # Verificar contenido de descripciones
        assert "ID de la conversación" in properties['conversation_id']['description']
        assert "Mensaje del usuario" in properties['message']['description']
        assert "dominios para filtrar" in properties['domains']['description']

    @pytest.mark.unit
    @pytest.mark.validation
    def test_field_constraints_in_schema(self):
        """Test que las restricciones están en el schema."""
        schema = ChatEngineRequest.schema()
        properties = schema['properties']
        
        # conversation_id constraints
        conv_id_props = properties['conversation_id']
        assert conv_id_props['minLength'] == 1
        assert conv_id_props['maxLength'] == 100
        
        # message constraints
        msg_props = properties['message']
        assert msg_props['minLength'] == 1
        assert msg_props['maxLength'] == 4000
        
        # domains constraints
        domains_props = properties['domains']
        assert domains_props['maxItems'] == 5

    @pytest.mark.unit
    @pytest.mark.validation
    def test_unicode_message_handling(self, temp_config_file):
        """Test de manejo de mensajes con caracteres Unicode."""
        unicode_message = "Hola, ¿cómo están? Necesito información sobre políticas 📋"
        
        request = ChatEngineRequest(
            conversation_id="test_123",
            message=unicode_message
        )
        
        assert request.message == unicode_message

    @pytest.mark.unit
    @pytest.mark.validation
    def test_special_characters_in_conversation_id(self, temp_config_file):
        """Test de caracteres especiales en conversation_id."""
        special_ids = [
            "test-123",
            "test_456",
            "test.789",
            "test@example.com",
            "test#123",
            "test$456"
        ]
        
        for special_id in special_ids:
            request = ChatEngineRequest(
                conversation_id=special_id,
                message="Test message"
            )
            assert request.conversation_id == special_id

    @pytest.mark.unit
    @pytest.mark.validation
    @patch('meribot.core.validation.get_logger')
    def test_validation_logging(self, mock_get_logger, temp_config_file):
        """Test de logging durante validación."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Test de validación exitosa con logging
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=None
        )
        
        # Debería haber log de información sobre dominios None
        # (Este test depende de la implementación actual del validator)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_case_insensitive_dangerous_pattern_detection(self, temp_config_file):
        """Test que detección de patrones peligrosos es case-insensitive."""
        dangerous_messages = [
            "Test <Script>alert('xss')</Script>",
            "Test JAVASCRIPT:void(0)",
            "Test EVAL(code)"
        ]
        
        for dangerous_msg in dangerous_messages:
            with pytest.raises(ValidationError) as exc_info:
                ChatEngineRequest(
                    conversation_id="test_123",
                    message=dangerous_msg
                )
            
            errors = exc_info.value.errors()
            assert any("patrones potencialmente peligrosos" in str(error) for error in errors)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_maximum_length_boundaries(self, temp_config_file):
        """Test de límites exactos de longitud."""
        # Test conversation_id en el límite
        max_conv_id = "x" * 100  # Exactamente MAX_CONVERSATION_ID_LENGTH
        request = ChatEngineRequest(
            conversation_id=max_conv_id,
            message="Test"
        )
        assert len(request.conversation_id) == 100
        
        # Test message en el límite
        max_message = "x" * 4000  # Exactamente MAX_MESSAGE_LENGTH
        request = ChatEngineRequest(
            conversation_id="test",
            message=max_message
        )
        assert len(request.message) == 4000

    @pytest.mark.unit
    @pytest.mark.validation
    def test_domains_count_boundary(self, temp_config_file):
        """Test de límite exacto de cantidad de dominios."""
        # Exactamente MAX_DOMAINS_COUNT (5) dominios
        max_domains = ["onboarding", "training", "cca", "sdo"]
        # Necesitamos solo 4 porque solo hay 4 dominios permitidos en temp_config_file
        
        request = ChatEngineRequest(
            conversation_id="test_123",
            message="Test message",
            domains=max_domains
        )
        
        assert len(request.domains) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])