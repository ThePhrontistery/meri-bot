"""
test_conversation_manager.py
Tests unitarios para el módulo ConversationManager de MeriBot.
Valida la gestión de sesiones de conversación, creación y cierre.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from meribot.core.conversation.conversation_manager import ConversationManager
from meribot.core.conversation.conversation_context import ConversationContext


class TestConversationManager:
    """Test suite para la clase ConversationManager."""

    @pytest.fixture
    def manager(self):
        """Fixture que proporciona una instancia de ConversationManager."""
        return ConversationManager()

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_manager_initialization(self, manager):
        """Test de inicialización del ConversationManager."""
        assert isinstance(manager.sessions, dict)
        assert len(manager.sessions) == 0
        assert hasattr(manager, 'logger')

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_or_create_session_new_id(self, manager):
        """Test de crear nueva sesión con ID específico."""
        conversation_id = "test_conversation_123"
        
        session = manager.get_or_create_session(conversation_id)
        
        assert isinstance(session, ConversationContext)
        assert session.conversation_id == conversation_id
        assert conversation_id in manager.sessions
        assert manager.sessions[conversation_id] is session

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_or_create_session_existing_id(self, manager):
        """Test de recuperar sesión existente."""
        conversation_id = "existing_conversation"
        
        # Crear sesión inicial
        session1 = manager.get_or_create_session(conversation_id)
        session1.add_message("user", "First message")
        
        # Recuperar la misma sesión
        session2 = manager.get_or_create_session(conversation_id)
        
        assert session1 is session2
        assert len(session2.get_history()) == 1
        assert session2.get_history()[0]["content"] == "First message"

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_or_create_session_anonymous(self, manager):
        """Test de crear sesión anónima."""
        session = manager.get_or_create_session("anonymous")
        
        assert isinstance(session, ConversationContext)
        assert session.conversation_id != "anonymous"  # Debe generar nuevo ID
        assert session.conversation_id in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_or_create_session_empty_id(self, manager):
        """Test de crear sesión con ID vacío."""
        session = manager.get_or_create_session("")
        
        assert isinstance(session, ConversationContext)
        assert session.conversation_id != ""  # Debe generar nuevo ID
        assert session.conversation_id in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_or_create_session_none_id(self, manager):
        """Test de crear sesión con ID None."""
        session = manager.get_or_create_session(None)
        
        assert isinstance(session, ConversationContext)
        assert session.conversation_id is not None
        assert session.conversation_id in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_create_session_without_metadata(self, manager):
        """Test de crear sesión sin metadatos."""
        session = manager.create_session()
        
        assert isinstance(session, ConversationContext)
        assert session.conversation_id in manager.sessions
        assert session.metadata == {}

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_create_session_with_metadata(self, manager):
        """Test de crear sesión con metadatos."""
        metadata = {"user_id": "user123", "session_type": "support"}
        session = manager.create_session(metadata=metadata)
        
        assert isinstance(session, ConversationContext)
        assert session.metadata == metadata
        assert session.conversation_id in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_session_existing(self, manager):
        """Test de obtener sesión existente."""
        conversation_id = "test_get_session"
        created_session = manager.get_or_create_session(conversation_id)
        
        retrieved_session = manager.get_session(conversation_id)
        
        assert retrieved_session is created_session
        assert retrieved_session.conversation_id == conversation_id

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_session_non_existing(self, manager):
        """Test de obtener sesión que no existe."""
        non_existing_id = "non_existing_session"
        
        session = manager.get_session(non_existing_id)
        
        assert session is None

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_close_session_existing(self, manager):
        """Test de cerrar sesión existente."""
        conversation_id = "session_to_close"
        session = manager.get_or_create_session(conversation_id)
        session.add_message("user", "Test message")
        
        result = manager.close_session(conversation_id)
        
        assert result is True
        assert conversation_id not in manager.sessions
        assert not session.is_active

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_close_session_non_existing(self, manager):
        """Test de cerrar sesión que no existe."""
        non_existing_id = "non_existing_session"
        
        result = manager.close_session(non_existing_id)
        
        assert result is False

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_close_session_with_runtime_error(self, manager):
        """Test de cerrar sesión que lanza RuntimeError."""
        conversation_id = "problematic_session"
        session = manager.get_or_create_session(conversation_id)
        
        # Mock el método close para que lance RuntimeError
        with patch.object(session, 'close', side_effect=RuntimeError("Test error")):
            result = manager.close_session(conversation_id)
            
            assert result is False
            # La sesión no debería eliminarse si hay error
            assert conversation_id in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_manager.get_logger')
    def test_logging_get_or_create_new_session(self, mock_get_logger, manager):
        """Test de logging al crear nueva sesión."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        conversation_id = "new_session_log_test"
        manager.get_or_create_session(conversation_id)
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Sesión creada con ID" in call_args
        assert conversation_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_manager.get_logger')
    def test_logging_get_or_create_existing_session(self, mock_get_logger, manager):
        """Test de logging al recuperar sesión existente."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        conversation_id = "existing_session_log_test"
        manager.get_or_create_session(conversation_id)  # Crear
        mock_logger.reset_mock()  # Reset para limpiar el log de creación
        
        manager.get_or_create_session(conversation_id)  # Recuperar
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Sesión recuperada" in call_args
        assert conversation_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_manager.get_logger')
    def test_logging_anonymous_session(self, mock_get_logger, manager):
        """Test de logging al crear sesión anónima."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        session = manager.get_or_create_session("anonymous")
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Sesión anónima creada" in call_args
        assert session.conversation_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_manager.get_logger')
    def test_logging_create_session_with_metadata(self, mock_get_logger, manager):
        """Test de logging al crear sesión con metadatos."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        metadata = {"user_id": "test_user"}
        session = manager.create_session(metadata=metadata)
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Sesión creada con metadatos" in call_args
        assert session.conversation_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_manager.get_logger')
    def test_logging_close_session_success(self, mock_get_logger, manager):
        """Test de logging al cerrar sesión exitosamente."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        conversation_id = "session_to_close_log"
        manager.get_or_create_session(conversation_id)
        mock_logger.reset_mock()
        
        manager.close_session(conversation_id)
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Sesión cerrada" in call_args
        assert conversation_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_manager.get_logger')
    def test_logging_close_non_existing_session(self, mock_get_logger, manager):
        """Test de logging al intentar cerrar sesión inexistente."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        non_existing_id = "non_existing_session"
        manager.close_session(non_existing_id)
        
        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Intento de cerrar sesión inexistente" in call_args
        assert non_existing_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    @patch('meribot.core.conversation.conversation_manager.get_logger')
    def test_logging_close_session_error(self, mock_get_logger, manager):
        """Test de logging cuando falla el cierre de sesión."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        manager.logger = mock_logger
        
        conversation_id = "problematic_session"
        session = manager.get_or_create_session(conversation_id)
        mock_logger.reset_mock()
        
        with patch.object(session, 'close', side_effect=RuntimeError("Test error")):
            manager.close_session(conversation_id)
            
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Error al cerrar sesión" in call_args
            assert conversation_id in call_args

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_multiple_sessions_management(self, manager):
        """Test de manejo de múltiples sesiones simultáneas."""
        session_ids = ["session_1", "session_2", "session_3"]
        sessions = []
        
        # Crear múltiples sesiones
        for session_id in session_ids:
            session = manager.get_or_create_session(session_id)
            session.add_message("user", f"Message for {session_id}")
            sessions.append(session)
        
        # Verificar que todas las sesiones existen
        assert len(manager.sessions) == 3
        for i, session_id in enumerate(session_ids):
            assert session_id in manager.sessions
            assert manager.sessions[session_id] is sessions[i]
        
        # Cerrar una sesión y verificar que las otras permanecen
        manager.close_session("session_2")
        assert len(manager.sessions) == 2
        assert "session_1" in manager.sessions
        assert "session_3" in manager.sessions
        assert "session_2" not in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_session_isolation(self, manager):
        """Test de aislamiento entre sesiones."""
        session1 = manager.get_or_create_session("session_1")
        session2 = manager.get_or_create_session("session_2")
        
        session1.add_message("user", "Message in session 1")
        session2.add_message("user", "Message in session 2")
        
        # Verificar que los mensajes están aislados
        history1 = session1.get_history()
        history2 = session2.get_history()
        
        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] == "Message in session 1"
        assert history2[0]["content"] == "Message in session 2"

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_session_lifecycle_complete(self, manager):
        """Test del ciclo de vida completo de una sesión."""
        conversation_id = "lifecycle_test"
        
        # 1. Crear sesión
        session = manager.get_or_create_session(conversation_id)
        assert session.is_active
        assert conversation_id in manager.sessions
        
        # 2. Usar sesión
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")
        assert len(session.get_history()) == 2
        
        # 3. Cerrar sesión
        result = manager.close_session(conversation_id)
        assert result is True
        assert not session.is_active
        assert conversation_id not in manager.sessions
        assert len(session.get_history()) == 0  # Historia se limpia al cerrar

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_conversation_id_case_sensitivity(self, manager):
        """Test de sensibilidad a mayúsculas en IDs de conversación."""
        session1 = manager.get_or_create_session("TestSession")
        session2 = manager.get_or_create_session("testsession")
        
        # Los IDs deben ser tratados como diferentes (case-sensitive)
        assert session1 is not session2
        assert "TestSession" in manager.sessions
        assert "testsession" in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_special_characters_in_conversation_id(self, manager):
        """Test de caracteres especiales en IDs de conversación."""
        special_ids = [
            "session-with-hyphens",
            "session_with_underscores",
            "session.with.dots",
            "session123with456numbers",
            "session@with#special$chars"
        ]
        
        for session_id in special_ids:
            session = manager.get_or_create_session(session_id)
            assert session.conversation_id == session_id
            assert session_id in manager.sessions

    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_or_create_session_whitespace_handling(self, manager):
        """Test de manejo de espacios en blanco en IDs."""
        # IDs con espacios en blanco deberían generar sesión anónima
        whitespace_ids = ["", "   ", "\t", "\n", "  \t\n  "]
        
        sessions = []
        for whitespace_id in whitespace_ids:
            session = manager.get_or_create_session(whitespace_id)
            sessions.append(session)
            assert session.conversation_id != whitespace_id
            assert session.conversation_id not in whitespace_ids
        
        # Todas las sesiones deberían ser diferentes
        conversation_ids = [s.conversation_id for s in sessions]
        assert len(set(conversation_ids)) == len(conversation_ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])