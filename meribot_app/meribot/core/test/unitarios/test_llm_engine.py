"""
test_llm_engine.py
Tests unitarios para el módulo LLMEngine de MeriBot.
Valida la orquestación del LLM, construcción de prompts y manejo de respuestas.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from meribot.core.llm.llm_engine import LLMEngine
from meribot.core.llm.llm_provider import LLMProvider


class TestLLMEngine:
    """Test suite para la clase LLMEngine."""

    @pytest.fixture
    def mock_provider(self):
        """Mock del LLMProvider."""
        provider = Mock(spec=LLMProvider)
        provider.generate = AsyncMock(return_value="Respuesta del LLM mockeado")
        provider.stream = AsyncMock()
        
        async def mock_stream_generator(prompt):
            tokens = ["Respuesta", "streaming", "del", "LLM"]
            for token in tokens:
                yield f"{token} "
        
        provider.stream.return_value = mock_stream_generator("test")
        return provider

    @pytest.fixture
    def mock_logger(self):
        """Mock del logger."""
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()
        logger.log_generation_failure = Mock()
        return logger

    @pytest.fixture
    def engine_with_mocks(self, mock_provider, mock_logger):
        """Engine con mocks inyectados."""
        return LLMEngine(provider=mock_provider, logger=mock_logger)

    @pytest.fixture
    def sample_conversation_history(self):
        """Historial de conversación de ejemplo."""
        return [
            {"role": "user", "content": "Hola, necesito información"},
            {"role": "assistant", "content": "¡Hola! ¿En qué te puedo ayudar?"},
            {"role": "user", "content": "Cuéntame sobre las políticas"}
        ]

    @pytest.fixture
    def sample_vector_texts(self):
        """Textos vectoriales de ejemplo."""
        return [
            "Las políticas de onboarding incluyen orientación inicial...",
            "El proceso de formación se realiza durante las primeras semanas...",
            "Los empleados nuevos deben completar los módulos de capacitación..."
        ]

    @pytest.mark.unit
    @pytest.mark.llm
    def test_llm_engine_initialization_default(self):
        """Test de inicialización con valores por defecto."""
        with patch.dict('os.environ', {
            'LLM_MODEL': 'gpt-4',
            'TEMPERATURE': '0.7',
            'MAX_TOKENS': '512'
        }):
            engine = LLMEngine()
            
            assert engine.model == 'gpt-4'
            assert engine.params['temperature'] == 0.7
            assert engine.params['max_tokens'] == 512
            assert engine.provider is not None

    @pytest.mark.unit
    @pytest.mark.llm
    def test_llm_engine_initialization_with_provider(self, mock_provider):
        """Test de inicialización con provider personalizado."""
        engine = LLMEngine(provider=mock_provider)
        assert engine.provider is mock_provider

    @pytest.mark.unit
    @pytest.mark.llm
    def test_build_full_prompt_basic(self, engine_with_mocks):
        """Test básico de construcción de prompt."""
        system_prompt = "Eres un asistente útil"
        conversation_history = []
        user_prompt = "¿Cuáles son las políticas?"
        vector_texts = []
        
        result = engine_with_mocks._build_full_prompt(
            system_prompt, conversation_history, user_prompt, vector_texts
        )
        
        expected = "Eres un asistente útil\n[user] ¿Cuáles son las políticas?"
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.llm
    def test_build_full_prompt_with_conversation_history(self, engine_with_mocks, sample_conversation_history):
        """Test de construcción de prompt con historial."""
        system_prompt = "Eres un asistente útil"
        user_prompt = "Nueva pregunta"
        vector_texts = []
        
        result = engine_with_mocks._build_full_prompt(
            system_prompt, sample_conversation_history, user_prompt, vector_texts
        )
        
        assert "Eres un asistente útil" in result
        assert "[user] Hola, necesito información" in result
        assert "[assistant] ¡Hola! ¿En qué te puedo ayudar?" in result
        assert "[user] Nueva pregunta" in result

    @pytest.mark.unit
    @pytest.mark.llm
    def test_build_full_prompt_with_vector_texts(self, engine_with_mocks, sample_vector_texts):
        """Test de construcción de prompt con textos vectoriales."""
        system_prompt = "Eres un asistente útil"
        conversation_history = []
        user_prompt = "Pregunta sobre políticas"
        
        result = engine_with_mocks._build_full_prompt(
            system_prompt, conversation_history, user_prompt, sample_vector_texts
        )
        
        assert "Eres un asistente útil" in result
        assert "Contexto relevante extraído de documentos internos:" in result
        assert sample_vector_texts[0] in result
        assert "---" in result  # Separador entre textos
        assert "[user] Pregunta sobre políticas" in result

    @pytest.mark.unit
    @pytest.mark.llm
    def test_build_full_prompt_complete(self, engine_with_mocks, sample_conversation_history, sample_vector_texts):
        """Test de construcción de prompt completo con todos los elementos."""
        system_prompt = "Eres un asistente útil"
        user_prompt = "Nueva pregunta completa"
        
        result = engine_with_mocks._build_full_prompt(
            system_prompt, sample_conversation_history, user_prompt, sample_vector_texts
        )
        
        # Verificar que contiene todos los elementos
        assert "Eres un asistente útil" in result
        assert "Contexto relevante extraído de documentos internos:" in result
        assert "[user] Hola, necesito información" in result
        assert "[assistant] ¡Hola! ¿En qué te puedo ayudar?" in result
        assert "[user] Nueva pregunta completa" in result

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_response_successful(self, engine_with_mocks, mock_provider):
        """Test de generación exitosa de respuesta."""
        system_prompt = "Eres un asistente útil"
        conversation_history = []
        user_prompt = "¿Cuáles son las políticas?"
        vector_texts = ["Contexto sobre políticas..."]
        metadata = {"user_id": "test_user"}
        
        result = await engine_with_mocks.generate_response(
            system_prompt, conversation_history, user_prompt, vector_texts, metadata
        )
        
        assert result == "Respuesta del LLM mockeado"
        mock_provider.generate.assert_called_once()
        
        # Verificar argumentos de la llamada
        call_args = mock_provider.generate.call_args
        assert user_prompt in call_args[0]  # user_prompt es el segundo argumento

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_response_with_exception(self, engine_with_mocks, mock_provider, mock_logger):
        """Test de manejo de excepción durante generación."""
        mock_provider.generate.side_effect = Exception("Error del LLM")
        
        result = await engine_with_mocks.generate_response(
            "System", [], "User", [], {"user_id": "test"}
        )
        
        assert result == "[Error al generar respuesta]"
        mock_logger.error.assert_called()
        mock_logger.log_generation_failure.assert_called()

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_response_without_metadata(self, engine_with_mocks, mock_provider, mock_logger):
        """Test de generación sin metadatos."""
        mock_provider.generate.side_effect = Exception("Error del LLM")
        
        result = await engine_with_mocks.generate_response(
            "System", [], "User", []  # Sin metadata
        )
        
        assert result == "[Error al generar respuesta]"
        # Verificar que se manejó correctamente la ausencia de metadata
        mock_logger.log_generation_failure.assert_called()

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_successful(self, engine_with_mocks, mock_provider):
        """Test de streaming exitoso."""
        system_prompt = "Eres un asistente útil"
        conversation_history = []
        user_prompt = "¿Cuáles son las políticas?"
        vector_texts = ["Contexto..."]
        
        tokens = []
        async for token in engine_with_mocks.stream_response(
            system_prompt, conversation_history, user_prompt, vector_texts
        ):
            tokens.append(token)
        
        expected_tokens = ["Respuesta ", "streaming ", "del ", "LLM "]
        assert tokens == expected_tokens
        mock_provider.stream.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_with_exception(self, engine_with_mocks, mock_provider, mock_logger):
        """Test de manejo de excepción durante streaming."""
        async def failing_stream(prompt):
            raise Exception("Streaming error")
            yield "This won't be reached"  # pragma: no cover
        
        mock_provider.stream.return_value = failing_stream("test")
        
        tokens = []
        async for token in engine_with_mocks.stream_response(
            "System", [], "User", []
        ):
            tokens.append(token)
        
        assert tokens == ["[Error: Streaming error]"]
        mock_logger.error.assert_called()

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_no_tokens_generated(self, engine_with_mocks, mock_provider, mock_logger):
        """Test cuando el streaming no genera tokens."""
        async def empty_stream(prompt):
            return
            yield  # pragma: no cover
        
        mock_provider.stream.return_value = empty_stream("test")
        
        tokens = []
        async for token in engine_with_mocks.stream_response(
            "System", [], "User", []
        ):
            tokens.append(token)
        
        assert tokens == ["[Error: LLM no generó tokens]"]
        mock_logger.warning.assert_called()

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_with_metadata_error_handling(self, engine_with_mocks, mock_provider, mock_logger):
        """Test de manejo de errores con metadata en streaming."""
        async def failing_stream(prompt):
            raise Exception("Stream error")
            yield  # pragma: no cover
        
        mock_provider.stream.return_value = failing_stream("test")
        metadata = {"user_id": "test_user"}
        
        tokens = []
        async for token in engine_with_mocks.stream_response(
            "System", [], "User", [], metadata
        ):
            tokens.append(token)
        
        # Verificar que se pasó el user_id correctamente al log
        mock_logger.log_generation_failure.assert_called()
        call_args = mock_logger.log_generation_failure.call_args[0]
        assert call_args[0] == "test_user"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_response_without_metadata_error_handling(self, engine_with_mocks, mock_provider, mock_logger):
        """Test de manejo de errores sin metadata en streaming."""
        async def failing_stream(prompt):
            raise Exception("Stream error")
            yield  # pragma: no cover
        
        mock_provider.stream.return_value = failing_stream("test")
        
        tokens = []
        async for token in engine_with_mocks.stream_response(
            "System", [], "User", []  # Sin metadata
        ):
            tokens.append(token)
        
        # Verificar que se manejó la ausencia de metadata
        mock_logger.log_generation_failure.assert_called()
        call_args = mock_logger.log_generation_failure.call_args[0]
        assert call_args[0] is None  # user_id debería ser None

    @pytest.mark.unit
    @pytest.mark.llm
    def test_prompt_construction_edge_cases(self, engine_with_mocks):
        """Test de casos extremos en construcción de prompts."""
        # Prompt vacío
        result = engine_with_mocks._build_full_prompt("", [], None, [])
        assert result == ""
        
        # Solo system prompt
        result = engine_with_mocks._build_full_prompt("System only", [], None, [])
        assert result == "System only"
        
        # Con historial vacío pero con user prompt
        result = engine_with_mocks._build_full_prompt("System", [], "User", [])
        assert result == "System\n[user] User"

    @pytest.mark.unit
    @pytest.mark.llm
    def test_prompt_construction_with_empty_vector_texts(self, engine_with_mocks):
        """Test de construcción con textos vectoriales vacíos."""
        result = engine_with_mocks._build_full_prompt(
            "System", [], "User", []
        )
        
        assert "Contexto relevante" not in result
        assert result == "System\n[user] User"

    @pytest.mark.unit
    @pytest.mark.llm
    def test_prompt_construction_with_single_vector_text(self, engine_with_mocks):
        """Test de construcción con un solo texto vectorial."""
        result = engine_with_mocks._build_full_prompt(
            "System", [], "User", ["Single context"]
        )
        
        assert "Contexto relevante extraído de documentos internos:" in result
        assert "Single context" in result
        assert "---" not in result  # No debería haber separadores con un solo texto

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_concurrent_generate_calls(self, engine_with_mocks):
        """Test de llamadas concurrentes a generate_response."""
        tasks = [
            engine_with_mocks.generate_response("System", [], f"User {i}", [])
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all(result == "Respuesta del LLM mockeado" for result in results)

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_concurrent_stream_calls(self, engine_with_mocks):
        """Test de llamadas concurrentes a stream_response."""
        async def collect_stream_tokens(engine, prompt_suffix):
            tokens = []
            async for token in engine.stream_response("System", [], f"User {prompt_suffix}", []):
                tokens.append(token)
            return tokens
        
        tasks = [
            collect_stream_tokens(engine_with_mocks, i)
            for i in range(2)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 2
        expected_tokens = ["Respuesta ", "streaming ", "del ", "LLM "]
        assert all(result == expected_tokens for result in results)

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_logging_during_generation(self, engine_with_mocks, mock_logger):
        """Test de logging durante generación."""
        await engine_with_mocks.generate_response("System", [], "User", [])
        
        # Verificar que se hicieron logs apropiados
        mock_logger.info.assert_called()
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Generando respuesta LLM" in call for call in info_calls)
        assert any("Respuesta LLM generada correctamente" in call for call in info_calls)

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_logging_during_streaming(self, engine_with_mocks, mock_logger):
        """Test de logging durante streaming."""
        tokens = []
        async for token in engine_with_mocks.stream_response("System", [], "User", []):
            tokens.append(token)
        
        # Verificar que se hizo log de inicio de streaming
        mock_logger.info.assert_called()
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Generando respuesta LLM en streaming" in call for call in info_calls)

    @pytest.mark.unit
    @pytest.mark.llm
    def test_environment_variable_handling(self):
        """Test de manejo de variables de entorno."""
        test_env = {
            'LLM_MODEL': 'custom-model',
            'TEMPERATURE': '0.9',
            'MAX_TOKENS': '1024'
        }
        
        with patch.dict('os.environ', test_env):
            engine = LLMEngine()
            
            assert engine.model == 'custom-model'
            assert engine.params['temperature'] == 0.9
            assert engine.params['max_tokens'] == 1024

    @pytest.mark.unit
    @pytest.mark.llm
    def test_environment_variable_fallbacks(self):
        """Test de valores por defecto cuando faltan variables de entorno."""
        with patch.dict('os.environ', {}, clear=True):
            engine = LLMEngine()
            
            assert engine.params['temperature'] == 0.7  # Valor por defecto
            assert engine.params['max_tokens'] == 512   # Valor por defecto

    @pytest.mark.unit
    @pytest.mark.llm
    def test_invalid_environment_variable_handling(self):
        """Test de manejo de variables de entorno inválidas."""
        test_env = {
            'TEMPERATURE': 'not_a_number',
            'MAX_TOKENS': 'also_not_a_number'
        }
        
        with patch.dict('os.environ', test_env):
            engine = LLMEngine()
            
            # Deberían usar valores por defecto cuando la conversión falla
            assert engine.params['temperature'] == 0.7
            assert engine.params['max_tokens'] == 512


if __name__ == "__main__":
    pytest.main([__file__, "-v"])