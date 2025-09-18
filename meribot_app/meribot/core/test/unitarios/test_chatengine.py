"""
test_chatengine.py
Tests unitarios para el módulo ChatEngine de MeriBot.
Valida la orquestación principal del core, flujo de procesamiento y manejo de errores.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from meribot.core.chatengine import ChatEngine
from meribot.core.validation import ChatEngineRequest


class TestChatEngine:
    """Test suite para la clase ChatEngine."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock de todas las dependencias del ChatEngine."""
        plugin_manager = Mock()
        plugin_manager.run_pre_llm_plugins = AsyncMock(return_value=None)
        plugin_manager.run_post_llm_plugins = AsyncMock()
        
        chromadb_connector = Mock()
        chromadb_connector.similarity_search = Mock(return_value=[])
        
        llm_engine = Mock()
        llm_engine.generate_response = AsyncMock(return_value="Respuesta del LLM")
        llm_engine.stream_response = AsyncMock()
        
        conversation_manager = Mock()
        session_mock = Mock()
        session_mock.get_history = Mock(return_value=[])
        session_mock.add_message = Mock()
        session_mock.conversation_id = "test_conversation"
        conversation_manager.get_or_create_session = Mock(return_value=session_mock)
        
        return {
            'plugin_manager': plugin_manager,
            'chromadb_connector': chromadb_connector,
            'llm_engine': llm_engine,
            'conversation_manager': conversation_manager,
            'session_mock': session_mock
        }

    @pytest.fixture
    def chat_engine(self, mock_dependencies):
        """Instancia de ChatEngine con dependencias mockeadas."""
        return ChatEngine(
            plugin_manager=mock_dependencies['plugin_manager'],
            chromadb_connector=mock_dependencies['chromadb_connector'],
            llm_engine=mock_dependencies['llm_engine'],
            conversation_manager=mock_dependencies['conversation_manager']
        )

    @pytest.fixture
    def sample_vector_results(self):
        """Resultados de búsqueda vectorial de ejemplo."""
        return [
            {
                'id': 'doc_1',
                'document': 'Las políticas de onboarding incluyen orientación inicial...',
                'score': 0.95,
                'metadatas': {
                    'title': 'Manual de Onboarding',
                    'url': 'https://intranet.cca.com/onboarding',
                    'domain': 'onboarding'
                }
            },
            {
                'id': 'doc_2',
                'document': 'El proceso de formación requiere completar módulos...',
                'score': 0.87,
                'metadatas': {
                    'title': 'Proceso de Formación',
                    'url': 'https://intranet.cca.com/training',
                    'domain': 'training'
                }
            }
        ]

    @pytest.mark.unit
    @pytest.mark.llm
    def test_chat_engine_initialization_default(self):
        """Test de inicialización con dependencias por defecto."""
        engine = ChatEngine()
        
        assert engine.plugin_manager is not None
        assert engine.chroma_connector is not None
        assert engine.llm_engine is not None
        assert engine.conversation_manager is not None

    @pytest.mark.unit
    @pytest.mark.llm
    def test_chat_engine_initialization_with_dependencies(self, mock_dependencies):
        """Test de inicialización con dependencias inyectadas."""
        engine = ChatEngine(
            plugin_manager=mock_dependencies['plugin_manager'],
            chromadb_connector=mock_dependencies['chromadb_connector'],
            llm_engine=mock_dependencies['llm_engine'],
            conversation_manager=mock_dependencies['conversation_manager']
        )
        
        assert engine.plugin_manager is mock_dependencies['plugin_manager']
        assert engine.chroma_connector is mock_dependencies['chromadb_connector']
        assert engine.llm_engine is mock_dependencies['llm_engine']
        assert engine.conversation_manager is mock_dependencies['conversation_manager']

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_successful_basic(self, chat_engine, mock_dependencies, sample_vector_results):
        """Test de procesamiento exitoso básico."""
        # Configurar mocks
        mock_dependencies['chromadb_connector'].similarity_search.return_value = sample_vector_results
        
        result = await chat_engine.process_message(
            conversation_id="test_conv",
            message="¿Cuáles son las políticas de onboarding?",
            domains=["onboarding"]
        )
        
        # Verificar estructura de respuesta
        assert result["type"] == "llm"
        assert result["response"] == "Respuesta del LLM"
        assert result["source"] == "llm"
        assert result["conversation_id"] == "test_conversation"
        assert "citations" in result
        
        # Verificar que se llamaron los métodos correctos
        mock_dependencies['conversation_manager'].get_or_create_session.assert_called_once_with("test_conv")
        mock_dependencies['chromadb_connector'].similarity_search.assert_called_once()
        mock_dependencies['llm_engine'].generate_response.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_with_citations(self, chat_engine, mock_dependencies, sample_vector_results):
        """Test de procesamiento que incluye citaciones."""
        mock_dependencies['chromadb_connector'].similarity_search.return_value = sample_vector_results
        
        result = await chat_engine.process_message(
            conversation_id="test_conv",
            message="Pregunta sobre políticas",
            domains=["onboarding", "training"]
        )
        
        # Verificar citaciones
        citations = result["citations"]
        assert len(citations) == 2
        assert citations[0]["title"] == "Manual de Onboarding"
        assert citations[0]["url"] == "https://intranet.cca.com/onboarding"
        assert citations[1]["title"] == "Proceso de Formación"
        assert citations[1]["url"] == "https://intranet.cca.com/training"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_validation_error(self, chat_engine):
        """Test de error de validación."""
        result = await chat_engine.process_message(
            conversation_id="",  # ID vacío debería fallar
            message="Test message"
        )
        
        assert result["type"] == "validation_error"
        assert "Error de validación" in result["response"]
        assert result["citations"] == []
        assert result["source"] == "validation"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_llm_exception(self, chat_engine, mock_dependencies):
        """Test de manejo de excepción en LLM."""
        mock_dependencies['llm_engine'].generate_response.side_effect = Exception("LLM error")
        
        result = await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message"
        )
        
        assert result["response"] == "[Error al generar respuesta]"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_no_vector_results(self, chat_engine, mock_dependencies):
        """Test de procesamiento sin resultados vectoriales."""
        mock_dependencies['chromadb_connector'].similarity_search.return_value = []
        
        result = await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message"
        )
        
        assert result["type"] == "llm"
        assert result["citations"] == []
        
        # Verificar que se pasó lista vacía al LLM
        llm_call_args = mock_dependencies['llm_engine'].generate_response.call_args
        vector_texts = llm_call_args[1]['vector_db_texts']
        assert vector_texts == []

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_updates_conversation_history(self, chat_engine, mock_dependencies):
        """Test que el historial de conversación se actualiza."""
        await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message"
        )
        
        session_mock = mock_dependencies['session_mock']
        
        # Verificar que se añadieron los mensajes
        calls = session_mock.add_message.call_args_list
        assert len(calls) == 2
        
        # Primer call: mensaje del usuario
        assert calls[0][0] == ("user", "Test message")
        
        # Segundo call: respuesta del asistente
        assert calls[1][0] == ("assistant", "Respuesta del LLM")

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_with_conversation_history(self, chat_engine, mock_dependencies):
        """Test con historial de conversación existente."""
        # Configurar historial existente
        existing_history = [
            {"role": "user", "content": "Mensaje anterior"},
            {"role": "assistant", "content": "Respuesta anterior"}
        ]
        mock_dependencies['session_mock'].get_history.return_value = existing_history
        
        await chat_engine.process_message(
            conversation_id="test_conv",
            message="Nuevo mensaje"
        )
        
        # Verificar que se pasó el historial al LLM
        llm_call_args = mock_dependencies['llm_engine'].generate_response.call_args
        conversation_history = llm_call_args[1]['conversation_history']
        assert conversation_history == existing_history

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_successful(self, chat_engine, mock_dependencies):
        """Test de streaming exitoso."""
        # Configurar mock para streaming
        async def mock_stream_generator(*args, **kwargs):
            tokens = ["Respuesta", "streaming", "del", "LLM"]
            for token in tokens:
                yield f"{token} "
        
        mock_dependencies['llm_engine'].stream_response.return_value = mock_stream_generator()
        
        tokens = []
        async for token in chat_engine.stream_response(
            conversation_id="test_conv",
            message="Test message"
        ):
            tokens.append(token)
        
        expected_tokens = ["Respuesta ", "streaming ", "del ", "LLM "]
        assert tokens == expected_tokens

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_validation_error(self, chat_engine):
        """Test de error de validación en streaming."""
        tokens = []
        async for token in chat_engine.stream_response(
            conversation_id="",  # ID vacío
            message="Test message"
        ):
            tokens.append(token)
        
        assert len(tokens) == 1
        assert "Error de validación" in tokens[0]

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_llm_exception(self, chat_engine, mock_dependencies):
        """Test de manejo de excepción en streaming."""
        async def failing_stream(*args, **kwargs):
            raise Exception("Streaming error")
            yield  # pragma: no cover
        
        mock_dependencies['llm_engine'].stream_response.return_value = failing_stream()
        
        tokens = []
        async for token in chat_engine.stream_response(
            conversation_id="test_conv",
            message="Test message"
        ):
            tokens.append(token)
        
        assert len(tokens) == 1
        assert "[Error al generar respuesta]" in tokens[0]

    @pytest.mark.unit
    @pytest.mark.llm
    def test_close_session(self, chat_engine, mock_dependencies):
        """Test de cierre de sesión."""
        chat_engine.close_session("test_conv")
        
        mock_dependencies['conversation_manager'].close_session.assert_called_once_with("test_conv")

    @pytest.mark.unit
    @pytest.mark.llm
    def test_get_context(self, chat_engine, mock_dependencies):
        """Test de obtención de contexto."""
        expected_history = [{"role": "user", "content": "Test"}]
        mock_dependencies['session_mock'].get_history.return_value = expected_history
        
        context = chat_engine.get_context("test_conv")
        
        assert context == expected_history
        mock_dependencies['conversation_manager'].get_or_create_session.assert_called_once_with("test_conv")

    @pytest.mark.unit
    @pytest.mark.llm
    def test_filter_chunks_by_domain(self, chat_engine):
        """Test de filtrado de chunks por dominio."""
        chunks = [
            {"domain": "onboarding", "content": "Onboarding info"},
            {"domain": "training", "content": "Training info"},
            {"domain": "security", "content": "Security info"}
        ]
        
        filtered = chat_engine.filter_chunks(chunks, domain="onboarding")
        
        assert len(filtered) == 1
        assert filtered[0]["domain"] == "onboarding"

    @pytest.mark.unit
    @pytest.mark.llm
    def test_filter_chunks_by_metadata(self, chat_engine):
        """Test de filtrado de chunks por metadatos."""
        chunks = [
            {"category": "policy", "priority": "high"},
            {"category": "guide", "priority": "medium"},
            {"category": "policy", "priority": "low"}
        ]
        
        filtered = chat_engine.filter_chunks(chunks, metadata={"category": "policy"})
        
        assert len(filtered) == 2
        assert all(chunk["category"] == "policy" for chunk in filtered)

    @pytest.mark.unit
    @pytest.mark.llm
    def test_filter_chunks_combined_filters(self, chat_engine):
        """Test de filtrado combinado."""
        chunks = [
            {"domain": "onboarding", "category": "policy"},
            {"domain": "onboarding", "category": "guide"},
            {"domain": "training", "category": "policy"}
        ]
        
        filtered = chat_engine.filter_chunks(
            chunks,
            domain="onboarding",
            metadata={"category": "policy"}
        )
        
        assert len(filtered) == 1
        assert filtered[0]["domain"] == "onboarding"
        assert filtered[0]["category"] == "policy"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_with_domains_filter(self, chat_engine, mock_dependencies, sample_vector_results):
        """Test de procesamiento con filtro de dominios."""
        mock_dependencies['chromadb_connector'].similarity_search.return_value = sample_vector_results
        
        await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message",
            domains=["onboarding", "training"]
        )
        
        # Verificar que se pasaron los dominios al connector
        search_call_args = mock_dependencies['chromadb_connector'].similarity_search.call_args
        assert search_call_args[1]['domains'] == ["onboarding", "training"]

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_citations_deduplication(self, chat_engine, mock_dependencies):
        """Test de deduplicación de citaciones."""
        # Resultados con citaciones duplicadas
        duplicate_results = [
            {
                'metadatas': {
                    'title': 'Manual de Onboarding',
                    'url': 'https://intranet.cca.com/onboarding'
                }
            },
            {
                'metadatas': {
                    'title': 'Manual de Onboarding',  # Duplicado
                    'url': 'https://intranet.cca.com/onboarding'
                }
            },
            {
                'metadatas': {
                    'title': 'Proceso de Formación',
                    'url': 'https://intranet.cca.com/training'
                }
            }
        ]
        
        mock_dependencies['chromadb_connector'].similarity_search.return_value = duplicate_results
        
        result = await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message"
        )
        
        # Verificar que las citaciones están deduplicadas
        citations = result["citations"]
        assert len(citations) == 2  # No 3
        titles = [c["title"] for c in citations]
        assert "Manual de Onboarding" in titles
        assert "Proceso de Formación" in titles

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    @patch('meribot.core.chatengine.load_system_prompt')
    async def test_process_message_uses_system_prompt(self, mock_load_prompt, chat_engine, mock_dependencies):
        """Test que se carga y usa el system prompt."""
        mock_load_prompt.return_value = "System prompt from file"
        
        await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message"
        )
        
        # Verificar que se cargó el system prompt
        mock_load_prompt.assert_called_once()
        
        # Verificar que se pasó al LLM
        llm_call_args = mock_dependencies['llm_engine'].generate_response.call_args
        system_prompt = llm_call_args[1]['system_prompt']
        assert system_prompt == "System prompt from file"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_process_message_metadata_handling(self, chat_engine, mock_dependencies, sample_vector_results):
        """Test de manejo de metadatos."""
        mock_dependencies['chromadb_connector'].similarity_search.return_value = sample_vector_results
        
        await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message"
        )
        
        # Verificar que se pasaron metadatos al LLM
        llm_call_args = mock_dependencies['llm_engine'].generate_response.call_args
        metadata = llm_call_args[1]['metadata']
        
        assert 'citar_fuentes' in metadata
        assert metadata['citar_fuentes'] is True

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    @patch('meribot.core.chatengine.log_generation_failure')
    async def test_process_message_logs_llm_failure(self, mock_log_failure, chat_engine, mock_dependencies):
        """Test de logging cuando falla el LLM."""
        mock_dependencies['llm_engine'].generate_response.side_effect = Exception("LLM failure")
        
        await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message"
        )
        
        # Verificar que se hizo log del fallo
        mock_log_failure.assert_called_once()
        call_args = mock_log_failure.call_args[0]
        assert "test_conv" in call_args[1]  # conversation_id
        assert "Test message" in call_args[2]  # message
        assert "LLM failure" in call_args[3]  # error

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_concurrent_message_processing(self, chat_engine, mock_dependencies):
        """Test de procesamiento concurrente de mensajes."""
        # Configurar diferentes respuestas para cada llamada
        responses = ["Respuesta 1", "Respuesta 2", "Respuesta 3"]
        mock_dependencies['llm_engine'].generate_response.side_effect = responses
        
        tasks = [
            chat_engine.process_message("conv_1", f"Message {i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all(result["type"] == "llm" for result in results)

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_empty_message_handling(self, chat_engine):
        """Test de manejo de mensaje vacío."""
        result = await chat_engine.process_message(
            conversation_id="test_conv",
            message=""  # Mensaje vacío
        )
        
        # Debería devolver error de validación
        assert result["type"] == "validation_error"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_none_domains_handling(self, chat_engine, mock_dependencies):
        """Test de manejo de dominios None."""
        await chat_engine.process_message(
            conversation_id="test_conv",
            message="Test message",
            domains=None
        )
        
        # Verificar que se pasó None al connector
        search_call_args = mock_dependencies['chromadb_connector'].similarity_search.call_args
        assert search_call_args[1]['domains'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])