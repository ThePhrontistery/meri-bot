"""
test_conversation_context.py
Tests unitarios para el módulo ConversationContext de MeriBot.
Valida el manejo de contexto de conversación, historial de mensajes y estados.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid

from meribot.core.conversation.conversation_context import ConversationContext


class TestConversationContext:
    """Test suite para la clase ConversationContext."""

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_context_initialization_default(self):
        """Test de inicialización con valores por defecto."""
        context = ConversationContext()
        
        # Verificar que se genera un UUID válido
        assert context.conversation_id is not None
        assert isinstance(context.conversation_id, str)
        assert len(context.conversation_id) > 0
        
        # Verificar valores por defecto
        assert context.messages == []
        assert context.is_active is True
        assert isinstance(context.created_at, datetime)
        assert isinstance(context.updated_at, datetime)
        assert context.metadata == {}

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_context_initialization_with_id(self):
        """Test de inicialización con ID específico."""
        test_id = "test_conversation_123"
        context = ConversationContext(conversation_id=test_id)
        
        assert context.conversation_id == test_id
        assert context.messages == []
        assert context.is_active is True

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_context_initialization_with_metadata(self):
        """Test de inicialización con metadata."""
        test_metadata = {"user_id": "user123", "session_type": "customer_support"}
        context = ConversationContext(metadata=test_metadata)
        
        assert context.metadata == test_metadata
        assert context.is_active is True

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_add_message_user(self):
        """Test de añadir mensaje de usuario."""
        context = ConversationContext()
        message_content = "Hola, necesito ayuda con onboarding"
        
        context.add_message("user", message_content)
        
        assert len(context.messages) == 1
        assert context.messages[0]["role"] == "user"
        assert context.messages[0]["content"] == message_content
        assert isinstance(context.messages[0]["timestamp"], datetime)

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_add_message_assistant(self):
        """Test de añadir mensaje del asistente."""
        context = ConversationContext()
        message_content = "¡Hola! Te puedo ayudar con información sobre onboarding."
        
        context.add_message("assistant", message_content)
        
        assert len(context.messages) == 1
        assert context.messages[0]["role"] == "assistant"
        assert context.messages[0]["content"] == message_content

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_add_message_with_custom_timestamp(self):
        """Test de añadir mensaje con timestamp personalizado."""
        context = ConversationContext()
        custom_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        
        context.add_message("user", "Test message", timestamp=custom_timestamp)
        
        assert context.messages[0]["timestamp"] == custom_timestamp

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_add_message_updates_updated_at(self):
        """Test que añadir mensaje actualiza updated_at."""
        context = ConversationContext()
        initial_updated_at = context.updated_at
        
        # Esperar un momento para asegurar diferencia en timestamp
        import time
        time.sleep(0.001)
        
        context.add_message("user", "Test message")
        
        assert context.updated_at > initial_updated_at

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_add_multiple_messages(self):
        """Test de añadir múltiples mensajes."""
        context = ConversationContext()
        
        context.add_message("user", "Primera pregunta")
        context.add_message("assistant", "Primera respuesta")
        context.add_message("user", "Segunda pregunta")
        
        assert len(context.messages) == 3
        assert context.messages[0]["role"] == "user"
        assert context.messages[1]["role"] == "assistant"
        assert context.messages[2]["role"] == "user"

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_history_returns_copy(self):
        """Test que get_history devuelve una copia del historial."""
        context = ConversationContext()
        context.add_message("user", "Test message")
        
        history1 = context.get_history()
        history2 = context.get_history()
        
        # Verificar que son copias independientes
        assert history1 == history2
        assert history1 is not history2
        assert history1 is not context.messages

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_history_modification_does_not_affect_original(self):
        """Test que modificar el historial devuelto no afecta al original."""
        context = ConversationContext()
        context.add_message("user", "Original message")
        
        history = context.get_history()
        history[0]["content"] = "Modified message"
        
        # Verificar que el original no cambió
        original_history = context.get_history()
        assert original_history[0]["content"] == "Original message"

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_close_conversation(self):
        """Test de cerrar conversación."""
        context = ConversationContext()
        context.add_message("user", "Test message")
        
        assert context.is_active is True
        assert len(context.messages) == 1
        
        context.close()
        
        assert context.is_active is False
        assert len(context.messages) == 0  # Mensajes se eliminan al cerrar

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_close_updates_updated_at(self):
        """Test que cerrar conversación actualiza updated_at."""
        context = ConversationContext()
        initial_updated_at = context.updated_at
        
        import time
        time.sleep(0.001)
        
        context.close()
        
        assert context.updated_at > initial_updated_at

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_add_message_to_closed_conversation_raises_error(self):
        """Test que añadir mensaje a conversación cerrada lanza error."""
        context = ConversationContext()
        context.close()
        
        with pytest.raises(RuntimeError) as exc_info:
            context.add_message("user", "This should fail")
        
        assert "está cerrada" in str(exc_info.value)
        assert context.conversation_id in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_close_already_closed_conversation_raises_error(self):
        """Test que cerrar conversación ya cerrada lanza error."""
        context = ConversationContext()
        context.close()
        
        with pytest.raises(RuntimeError) as exc_info:
            context.close()
        
        assert "ya está cerrada" in str(exc_info.value)
        assert context.conversation_id in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_context.get_logger')
    def test_add_message_logs_correctly(self, mock_get_logger):
        """Test que añadir mensaje registra logs correctamente."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        context = ConversationContext()
        context.add_message("user", "Test message")
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Mensaje añadido" in call_args
        assert context.conversation_id in call_args
        assert "role=user" in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_context.get_logger')
    def test_close_logs_correctly(self, mock_get_logger):
        """Test que cerrar conversación registra logs correctamente."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        context = ConversationContext()
        context.close()
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "cerrada correctamente" in call_args
        assert context.conversation_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_context.get_logger')
    def test_add_message_to_closed_logs_error(self, mock_get_logger):
        """Test que intentar añadir mensaje a conversación cerrada registra error."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        context = ConversationContext()
        context.close()
        
        try:
            context.add_message("user", "This should fail")
        except RuntimeError:
            pass
        
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args[0][0]
        assert "conversación cerrada" in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_context.get_logger')
    def test_close_already_closed_logs_warning(self, mock_get_logger):
        """Test que cerrar conversación ya cerrada registra warning."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        context = ConversationContext()
        context.close()
        
        try:
            context.close()
        except RuntimeError:
            pass
        
        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args[0][0]
        assert "ya está cerrada" in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_id_uniqueness(self):
        """Test que los IDs de conversación son únicos."""
        context1 = ConversationContext()
        context2 = ConversationContext()
        
        assert context1.conversation_id != context2.conversation_id

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_id_is_valid_uuid(self):
        """Test que el ID de conversación es un UUID válido."""
        context = ConversationContext()
        
        # Intentar parsear como UUID - no debería lanzar excepción
        parsed_uuid = uuid.UUID(context.conversation_id)
        assert str(parsed_uuid) == context.conversation_id

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_context_immutable_after_close(self):
        """Test que el contexto es inmutable después de cerrar."""
        context = ConversationContext()
        context.add_message("user", "Before close")
        original_message_count = len(context.messages)
        
        context.close()
        
        # Verificar que no se pueden añadir mensajes
        with pytest.raises(RuntimeError):
            context.add_message("user", "After close")
        
        # Verificar que el historial permanece vacío
        assert len(context.messages) == 0

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_message_timestamp_ordering(self):
        """Test que los timestamps de los mensajes están en orden."""
        context = ConversationContext()
        
        context.add_message("user", "First message")
        import time
        time.sleep(0.001)  # Pequeña pausa para asegurar diferencia de timestamp
        context.add_message("assistant", "Second message")
        time.sleep(0.001)
        context.add_message("user", "Third message")
        
        history = context.get_history()
        assert history[0]["timestamp"] <= history[1]["timestamp"]
        assert history[1]["timestamp"] <= history[2]["timestamp"]

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_metadata_persistence(self):
        """Test que los metadatos se mantienen durante el ciclo de vida."""
        metadata = {"user_id": "test_user", "session_type": "support"}
        context = ConversationContext(metadata=metadata)
        
        context.add_message("user", "Test message")
        
        assert context.metadata == metadata
        
        # Los metadatos deberían persistir incluso después de cerrar
        context.close()
        assert context.metadata == metadata

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_empty_message_content_allowed(self):
        """Test que se permite contenido de mensaje vacío."""
        context = ConversationContext()
        
        # Debe permitir mensajes vacíos (la validación se hace en otros niveles)
        context.add_message("user", "")
        
        assert len(context.messages) == 1
        assert context.messages[0]["content"] == ""

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_message_roles_flexibility(self):
        """Test que se permiten diferentes roles de mensaje."""
        context = ConversationContext()
        
        # Test de roles estándar
        context.add_message("user", "User message")
        context.add_message("assistant", "Assistant message")
        context.add_message("system", "System message")
        
        history = context.get_history()
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert history[2]["role"] == "system"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])