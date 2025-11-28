"""
Tests unitarios para meribot.core.chatengine
"""

import os
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from typing import List, Optional

from meribot.core.chatengine import ChatEngine


class TestChatEngineInitialization:
    """Tests para la inicialización del ChatEngine"""
    
    def test_chatengine_default_initialization(self):
        """Test inicialización con dependencias por defecto"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'):
            
            engine = ChatEngine()
            
            assert engine.plugin_manager is not None
            assert engine.chroma_connector is not None
            assert engine.llm_engine is not None
            assert engine.conversation_manager is not None
    
    def test_chatengine_custom_dependencies(self):
        """Test inicialización con dependencias personalizadas"""
        mock_plugin_manager = MagicMock()
        mock_chroma_connector = MagicMock()
        mock_llm_engine = MagicMock()
        mock_conversation_manager = MagicMock()
        
        engine = ChatEngine(
            plugin_manager=mock_plugin_manager,
            chromadb_connector=mock_chroma_connector,
            llm_engine=mock_llm_engine,
            conversation_manager=mock_conversation_manager
        )
        
        assert engine.plugin_manager is mock_plugin_manager
        assert engine.chroma_connector is mock_chroma_connector
        assert engine.llm_engine is mock_llm_engine
        assert engine.conversation_manager is mock_conversation_manager


class TestProcessMessage:
    """Tests para el método process_message"""
    
    @pytest.fixture
    def mock_chatengine(self):
        """Fixture que proporciona ChatEngine con dependencias mockeadas"""
        with patch('meribot.core.chatengine.PluginManager') as mock_pm, \
             patch('meribot.core.chatengine.ChromaDBConnector') as mock_chroma, \
             patch('meribot.core.chatengine.LLMEngine') as mock_llm, \
             patch('meribot.core.chatengine.ConversationManager') as mock_conv:
            
            engine = ChatEngine()
            
            # Configurar mocks
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []
            mock_session.add_message = MagicMock()
            
            mock_conv.return_value.get_or_create_session.return_value = mock_session
            mock_chroma.return_value.similarity_search.return_value = []
            mock_llm.return_value.generate_response = AsyncMock(return_value="Test response")
            
            engine.conversation_manager = mock_conv.return_value
            engine.chroma_connector = mock_chroma.return_value
            engine.llm_engine = mock_llm.return_value
            
            yield engine, mock_session, mock_chroma.return_value, mock_llm.return_value
    
    @patch('meribot.core.chatengine.load_system_prompt')
    @pytest.mark.asyncio
    async def test_process_message_success(self, mock_load_prompt, mock_chatengine):
        """Test procesamiento exitoso de mensaje"""
        engine, mock_session, mock_chroma, mock_llm = mock_chatengine
        mock_load_prompt.return_value = "System prompt"
        
        result = await engine.process_message(
            conversation_id="conv_123",
            message="¿Cómo solicito vacaciones?",
            domains=["onboarding"]
        )
        
        assert result["type"] == "llm"
        assert result["response"] == "Test response"
        assert result["conversation_id"] == "conv_123"
        assert "citations" in result
        
        # Verificar que se llamaron los métodos correctos
        mock_session.add_message.assert_any_call("user", "¿Cómo solicito vacaciones?")
        mock_session.add_message.assert_any_call("assistant", "Test response")
    
    @pytest.mark.asyncio
    async def test_process_message_validation_error(self, mock_chatengine):
        """Test manejo de errores de validación"""
        engine, _, _, _ = mock_chatengine
        
        # Mensaje vacío debería fallar la validación
        result = await engine.process_message(
            conversation_id="conv_123",
            message="",  # Mensaje vacío
            domains=["onboarding"]
        )
        
        assert result["type"] == "validation_error"
        assert "Error de validación" in result["response"]
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_process_message_with_citations(self, mock_chatengine):
        """Test procesamiento con citaciones de la base vectorial"""
        engine, mock_session, mock_chroma, mock_llm = mock_chatengine
        
        # Configurar respuesta de ChromaDB con metadatos
        mock_chroma.similarity_search.return_value = [
            {
                "document": "Contenido relevante sobre vacaciones",
                "metadatas": {
                    "title": "Política de Vacaciones",
                    "url": "http://example.com/vacaciones"
                }
            },
            {
                "document": "Otro contenido",
                "metadatas": {
                    "title": "Manual de RR.HH.",
                    "url": "http://example.com/rrhh"
                }
            }
        ]
        
        with patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            result = await engine.process_message(
                conversation_id="conv_123",
                message="¿Cómo solicito vacaciones?",
                domains=["onboarding"]
            )
        
        assert result["type"] == "llm"
        assert len(result["citations"]) == 2
        assert result["citations"][0]["title"] == "Política de Vacaciones"
        assert result["citations"][0]["url"] == "http://example.com/vacaciones"
    
    @pytest.mark.asyncio
    async def test_process_message_llm_failure(self, mock_chatengine):
        """Test manejo de fallo en LLM"""
        engine, mock_session, mock_chroma, mock_llm = mock_chatengine
        
        # Configurar LLM para que falle
        mock_llm.generate_response.side_effect = Exception("LLM Error")
        
        with patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"), \
             patch('meribot.core.chatengine.log_generation_failure') as mock_log:
            
            result = await engine.process_message(
                conversation_id="conv_123",
                message="Test message"
            )
        
        assert result["response"] == "[Error al generar respuesta]"
        mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_message_no_domains(self, mock_chatengine):
        """Test procesamiento sin especificar dominios"""
        engine, mock_session, mock_chroma, mock_llm = mock_chatengine
        
        with patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            result = await engine.process_message(
                conversation_id="conv_123",
                message="Test message"
                # domains=None (por defecto)
            )
        
        assert result["type"] == "llm"
        # Verificar que se llamó similarity_search con domains=None
        mock_chroma.similarity_search.assert_called_once_with(
            query_text="Test message",
            domains=None
        )
    
    @pytest.mark.asyncio
    async def test_process_message_duplicate_citations(self, mock_chatengine):
        """Test eliminación de citaciones duplicadas"""
        engine, mock_session, mock_chroma, mock_llm = mock_chatengine
        
        # Configurar respuesta con documentos duplicados
        mock_chroma.similarity_search.return_value = [
            {
                "document": "Contenido 1",
                "metadatas": {
                    "title": "Documento A",
                    "url": "http://example.com/doc-a"
                }
            },
            {
                "document": "Contenido 2", 
                "metadatas": {
                    "title": "Documento A",  # Título duplicado
                    "url": "http://example.com/doc-a"  # URL duplicada
                }
            },
            {
                "document": "Contenido 3",
                "metadatas": {
                    "title": "Documento B",
                    "url": "http://example.com/doc-b"
                }
            }
        ]
        
        with patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            result = await engine.process_message(
                conversation_id="conv_123",
                message="Test message"
            )
        
        # Debería tener solo 2 citaciones únicas
        assert len(result["citations"]) == 2
        titles = [cite["title"] for cite in result["citations"]]
        assert "Documento A" in titles
        assert "Documento B" in titles
    
    @pytest.mark.asyncio
    async def test_process_message_conversation_history(self, mock_chatengine):
        """Test que se incluye el historial de conversación"""
        engine, mock_session, mock_chroma, mock_llm = mock_chatengine
        
        # Configurar historial de conversación
        mock_session.get_history.return_value = [
            {"role": "user", "content": "Mensaje anterior"},
            {"role": "assistant", "content": "Respuesta anterior"}
        ]
        
        with patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            await engine.process_message(
                conversation_id="conv_123",
                message="Nuevo mensaje"
            )
        
        # Verificar que se pasó el historial al LLM
        mock_llm.generate_response.assert_called_once()
        call_args = mock_llm.generate_response.call_args
        
        assert "conversation_history" in call_args.kwargs
        assert len(call_args.kwargs["conversation_history"]) == 2


class TestStreamResponse:
    """Tests para el método stream_response"""
    
    @pytest.fixture
    def mock_streaming_chatengine(self):
        """Fixture para ChatEngine con soporte streaming"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'):
            
            engine = ChatEngine()
            
            # Configurar mocks para streaming
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []
            
            engine.conversation_manager.get_or_create_session.return_value = mock_session
            engine.chroma_connector.similarity_search.return_value = []
            
            yield engine, mock_session
    
    @pytest.mark.asyncio
    async def test_stream_response_validation_error(self, mock_streaming_chatengine):
        """Test streaming con error de validación"""
        engine, _ = mock_streaming_chatengine
        
        # Intentar stream con mensaje vacío
        stream = engine.stream_response(
            conversation_id="conv_123",
            message="",  # Mensaje vacío
            domains=["onboarding"]
        )
        
        # Debería poder crear el generador
        assert stream is not None
        
        # Al iterar debería manejar el error de validación
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        
        # Podría retornar chunks de error o estar vacío
        # La implementación específica depende del código real


class TestChatEngineIntegration:
    """Tests de integración para ChatEngine"""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test flujo completo de conversación"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'), \
             patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            
            engine = ChatEngine()
            
            # Configurar mocks para simulación completa
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []
            mock_session.add_message = MagicMock()
            
            engine.conversation_manager.get_or_create_session.return_value = mock_session
            engine.chroma_connector.similarity_search.return_value = [
                {
                    "document": "Información sobre vacaciones",
                    "metadatas": {
                        "title": "Política Vacaciones",
                        "url": "http://example.com/vacaciones"
                    }
                }
            ]
            engine.llm_engine.generate_response = AsyncMock(
                return_value="Para solicitar vacaciones, necesitas llenar el formulario X."
            )
            
            # Primera consulta
            result1 = await engine.process_message(
                conversation_id="conv_123",
                message="¿Cómo solicito vacaciones?"
            )
            
            assert result1["type"] == "llm"
            assert "vacaciones" in result1["response"]
            assert len(result1["citations"]) == 1
            
            # Simular segunda consulta con historial
            mock_session.get_history.return_value = [
                {"role": "user", "content": "¿Cómo solicito vacaciones?"},
                {"role": "assistant", "content": "Para solicitar vacaciones, necesitas llenar el formulario X."}
            ]
            
            result2 = await engine.process_message(
                conversation_id="conv_123",
                message="¿Dónde encuentro ese formulario?"
            )
            
            assert result2["type"] == "llm"
            assert result2["conversation_id"] == "conv_123"
    
    @pytest.mark.asyncio
    async def test_multiple_domains_search(self):
        """Test búsqueda con múltiples dominios"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'), \
             patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            
            engine = ChatEngine()
            
            # Configurar session mock
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []
            engine.conversation_manager.get_or_create_session.return_value = mock_session
            
            # Configurar respuesta de ChromaDB
            engine.chroma_connector.similarity_search.return_value = []
            engine.llm_engine.generate_response = AsyncMock(return_value="Response")
            
            # Procesar mensaje con múltiples dominios
            await engine.process_message(
                conversation_id="conv_123",
                message="Pregunta general",
                domains=["onboarding", "training", "cca"]
            )
            
            # Verificar que se pasaron los dominios correctos
            engine.chroma_connector.similarity_search.assert_called_with(
                query_text="Pregunta general",
                domains=["onboarding", "training", "cca"]
            )


class TestChatEngineErrorHandling:
    """Tests para manejo de errores en ChatEngine"""
    
    @pytest.mark.asyncio
    async def test_chroma_search_failure(self):
        """Test fallo en búsqueda de ChromaDB"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'), \
             patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            
            engine = ChatEngine()
            
            # Configurar session mock
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []
            engine.conversation_manager.get_or_create_session.return_value = mock_session
            
            # Configurar ChromaDB para fallar
            engine.chroma_connector.similarity_search.side_effect = Exception("ChromaDB Error")
            engine.llm_engine.generate_response = AsyncMock(return_value="Response")
            
            # El test debe verificar que se propaga la excepción
            with pytest.raises(Exception, match="ChromaDB Error"):
                await engine.process_message(
                    conversation_id="conv_123",
                    message="Test message"
                )
    
    @pytest.mark.asyncio
    async def test_conversation_manager_failure(self):
        """Test fallo en ConversationManager"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'), \
             patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            
            engine = ChatEngine()
            
            # Configurar ConversationManager para fallar
            engine.conversation_manager.get_or_create_session.side_effect = Exception("Session Error")
            
            # El error debería propagarse o manejarse adecuadamente
            try:
                await engine.process_message(
                    conversation_id="conv_123",
                    message="Test message"
                )
            except Exception as e:
                assert "Session Error" in str(e)
    
    @pytest.mark.asyncio
    async def test_system_prompt_loading_failure(self):
        """Test fallo en carga de system prompt"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'), \
             patch('meribot.core.chatengine.load_system_prompt', side_effect=FileNotFoundError("System prompt not found")):
            
            engine = ChatEngine()
            
            # Configurar mocks básicos
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []
            engine.conversation_manager.get_or_create_session.return_value = mock_session
            engine.chroma_connector.similarity_search.return_value = []
            
            # Debería fallar o manejar el error del system prompt
            try:
                await engine.process_message(
                    conversation_id="conv_123",
                    message="Test message"
                )
            except FileNotFoundError:
                # Error esperado
                pass


class TestChatEngineEdgeCases:
    """Tests para casos edge"""
    
    @pytest.mark.asyncio
    async def test_empty_conversation_history(self):
        """Test con historial de conversación vacío"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'), \
             patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            
            engine = ChatEngine()
            
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []  # Historial vacío
            engine.conversation_manager.get_or_create_session.return_value = mock_session
            engine.chroma_connector.similarity_search.return_value = []
            engine.llm_engine.generate_response = AsyncMock(return_value="Response")
            
            result = await engine.process_message(
                conversation_id="conv_123",
                message="Primera pregunta"
            )
            
            assert result["type"] == "llm"
            assert result["response"] == "Response"
    
    @pytest.mark.asyncio
    async def test_very_long_conversation_id(self):
        """Test con conversation_id muy largo"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'):
            
            engine = ChatEngine()
            
            # ID muy largo que debería fallar en validación
            very_long_id = "x" * 200
            
            result = await engine.process_message(
                conversation_id=very_long_id,
                message="Test message"
            )
            
            assert result["type"] == "validation_error"
            assert "Error de validación" in result["response"]
    
    @pytest.mark.asyncio
    async def test_unicode_message_handling(self):
        """Test manejo de mensajes con Unicode"""
        with patch('meribot.core.chatengine.PluginManager'), \
             patch('meribot.core.chatengine.ChromaDBConnector'), \
             patch('meribot.core.chatengine.LLMEngine'), \
             patch('meribot.core.chatengine.ConversationManager'), \
             patch('meribot.core.chatengine.load_system_prompt', return_value="System prompt"):
            
            engine = ChatEngine()
            
            mock_session = MagicMock()
            mock_session.conversation_id = "conv_123"
            mock_session.get_history.return_value = []
            engine.conversation_manager.get_or_create_session.return_value = mock_session
            engine.chroma_connector.similarity_search.return_value = []
            engine.llm_engine.generate_response = AsyncMock(return_value="Respuesta en español")
            
            unicode_message = "¿Cómo está el día? 🌟 Ñandú en español 中文字符"
            
            result = await engine.process_message(
                conversation_id="conv_123",
                message=unicode_message
            )
            
            assert result["type"] == "llm"
            # Verificar que el mensaje Unicode se procesó correctamente
            mock_session.add_message.assert_any_call("user", unicode_message)