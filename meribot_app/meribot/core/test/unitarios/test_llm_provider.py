"""
test_llm_provider.py
Tests unitarios para el módulo LLMProvider de MeriBot.
Valida las llamadas a Azure OpenAI, manejo de errores y streaming.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import requests
from typing import AsyncGenerator

from meribot.core.llm.llm_provider import LLMProvider


class TestLLMProvider:
    """Test suite para la clase LLMProvider."""

    @pytest.fixture
    def provider_config(self):
        """Configuración de ejemplo para el provider."""
        return {
            "temperature": 0.7,
            "max_tokens": 512
        }

    @pytest.fixture
    def mock_env_vars(self):
        """Variables de entorno mockeadas."""
        return {
            'AZURE_OPENAI_API_KEY': 'test_api_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test_deployment',
            'AZURE_OPENAI_API_VERSION': '2023-12-01-preview'
        }

    @pytest.fixture
    def provider(self, provider_config, mock_env_vars):
        """Instancia de LLMProvider para tests."""
        with patch.dict('os.environ', mock_env_vars):
            return LLMProvider("gpt-4", provider_config)

    @pytest.mark.unit
    @pytest.mark.llm
    def test_llm_provider_initialization(self, provider_config, mock_env_vars):
        """Test de inicialización del LLMProvider."""
        with patch.dict('os.environ', mock_env_vars):
            provider = LLMProvider("gpt-4", provider_config)
            
            assert provider.model == "gpt-4"
            assert provider.params == provider_config
            assert provider.azure_api_key == "test_api_key"
            assert provider.azure_endpoint == "https://test.openai.azure.com"
            assert provider.azure_deployment == "test_deployment"
            assert provider.azure_api_version == "2023-12-01-preview"

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_successful_response(self, provider):
        """Test de generación exitosa de respuesta."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Esta es una respuesta de prueba del LLM."
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            result = await provider.generate(
                "You are a helpful assistant",
                "¿Cuáles son las políticas de onboarding?"
            )
            
            assert result == "Esta es una respuesta de prueba del LLM."
            
            # Verificar que se hizo la llamada correcta
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            
            # Verificar URL
            expected_url = f"{provider.azure_endpoint}/openai/deployments/{provider.azure_deployment}/chat/completions?api-version={provider.azure_api_version}"
            assert call_args[1]['url'] == expected_url
            
            # Verificar headers
            headers = call_args[1]['headers']
            assert headers['Content-Type'] == 'application/json'
            assert headers['api-key'] == provider.azure_api_key
            
            # Verificar payload
            payload = json.loads(call_args[1]['data'])
            assert len(payload['messages']) == 2
            assert payload['messages'][0]['role'] == 'system'
            assert payload['messages'][1]['role'] == 'user'
            assert payload['temperature'] == 0.7
            assert payload['max_tokens'] == 512

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_request_exception(self, provider):
        """Test de manejo de excepción en request."""
        with patch('requests.post', side_effect=requests.RequestException("Connection error")):
            result = await provider.generate(
                "System prompt",
                "User prompt"
            )
            
            assert "[Error Azure OpenAI]" in result
            assert "Connection error" in result

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_http_error(self, provider):
        """Test de manejo de error HTTP."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP 429: Rate limit exceeded")
        
        with patch('requests.post', return_value=mock_response):
            result = await provider.generate(
                "System prompt",
                "User prompt"
            )
            
            assert "[Error Azure OpenAI]" in result
            assert "HTTP 429" in result

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_json_decode_error(self, provider):
        """Test de manejo de error en decodificación JSON."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with patch('requests.post', return_value=mock_response):
            result = await provider.generate(
                "System prompt",
                "User prompt"
            )
            
            assert "[Error Azure OpenAI]" in result

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_timeout_error(self, provider):
        """Test de manejo de timeout."""
        with patch('requests.post', side_effect=requests.Timeout("Request timeout")):
            result = await provider.generate(
                "System prompt",
                "User prompt"
            )
            
            assert "[Error Azure OpenAI]" in result
            assert "Request timeout" in result

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_empty_response(self, provider):
        """Test de respuesta vacía del LLM."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": ""
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.post', return_value=mock_response):
            result = await provider.generate(
                "System prompt",
                "User prompt"
            )
            
            assert result == ""

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_malformed_response(self, provider):
        """Test de respuesta malformada del LLM."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": []  # Sin choices
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.post', return_value=mock_response):
            result = await provider.generate(
                "System prompt",
                "User prompt"
            )
            
            assert "[Error Azure OpenAI]" in result

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_with_custom_parameters(self, mock_env_vars):
        """Test con parámetros personalizados."""
        custom_params = {
            "temperature": 0.9,
            "max_tokens": 1024
        }
        
        with patch.dict('os.environ', mock_env_vars):
            provider = LLMProvider("gpt-4", custom_params)
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Custom response"
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            await provider.generate("System", "User")
            
            # Verificar que se usaron los parámetros personalizados
            payload = json.loads(mock_post.call_args[1]['data'])
            assert payload['temperature'] == 0.9
            assert payload['max_tokens'] == 1024

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_basic_functionality(self, provider):
        """Test básico de funcionalidad de streaming."""
        prompt = "Generate a streaming response"
        
        result_tokens = []
        async for token in provider.stream(prompt):
            result_tokens.append(token)
        
        # El método stream actual simula splitting por palabras
        expected_words = prompt.split()
        assert len(result_tokens) == len(expected_words)
        
        # Verificar que cada token termina con espacio
        for token in result_tokens:
            assert token.endswith(" ")

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_empty_prompt(self, provider):
        """Test de streaming con prompt vacío."""
        prompt = ""
        
        result_tokens = []
        async for token in provider.stream(prompt):
            result_tokens.append(token)
        
        assert len(result_tokens) == 0

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_single_word(self, provider):
        """Test de streaming con una sola palabra."""
        prompt = "Hello"
        
        result_tokens = []
        async for token in provider.stream(prompt):
            result_tokens.append(token)
        
        assert len(result_tokens) == 1
        assert result_tokens[0] == "Hello "

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_timing(self, provider):
        """Test de timing en streaming."""
        import time
        
        prompt = "Word1 Word2 Word3"
        start_time = time.time()
        
        tokens = []
        async for token in provider.stream(prompt):
            tokens.append(token)
        
        end_time = time.time()
        
        # Verificar que hubo algún delay (cada token espera 0.001s)
        assert end_time - start_time >= 0.003  # 3 palabras * 0.001s cada una

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    @patch('meribot.core.llm.llm_provider.get_logger')
    async def test_generate_logging(self, mock_get_logger, provider):
        """Test de logging durante generación."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        provider.logger = mock_logger
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.post', return_value=mock_response):
            await provider.generate("System", "User")
            
            # Verificar que se hicieron logs
            assert mock_logger.info.called
            
            # Verificar contenido de logs
            info_calls = mock_logger.info.call_args_list
            assert any("Generando respuesta con Azure OpenAI" in str(call) for call in info_calls)
            assert any("Respuesta recibida correctamente" in str(call) for call in info_calls)

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    @patch('meribot.core.llm.llm_provider.get_logger')
    async def test_generate_error_logging(self, mock_get_logger, provider):
        """Test de logging de errores."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        provider.logger = mock_logger
        
        with patch('requests.post', side_effect=Exception("Test error")):
            await provider.generate("System", "User")
            
            # Verificar que se registró el error
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args[0][0]
            assert "Error en Azure OpenAI" in error_call

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    @patch('meribot.core.llm.llm_provider.get_logger')
    async def test_stream_logging(self, mock_get_logger, provider):
        """Test de logging durante streaming."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        provider.logger = mock_logger
        
        async for token in provider.stream("Test prompt"):
            pass
        
        # Verificar que se hizo log de inicio de streaming
        mock_logger.info.assert_called()
        info_call = mock_logger.info.call_args[0][0]
        assert "Simulando streaming" in info_call

    @pytest.mark.unit
    @pytest.mark.llm
    def test_environment_variables_fallback(self):
        """Test de fallback cuando faltan variables de entorno."""
        # Test sin variables de entorno
        with patch.dict('os.environ', {}, clear=True):
            provider = LLMProvider("gpt-4", {"temperature": 0.7})
            
            assert provider.azure_api_key is None
            assert provider.azure_endpoint is None
            assert provider.azure_deployment is None
            assert provider.azure_api_version is None

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_request_timeout_configuration(self, provider):
        """Test de configuración de timeout en requests."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            await provider.generate("System", "User")
            
            # Verificar que se configuró timeout
            call_kwargs = mock_post.call_args[1]
            assert 'timeout' in call_kwargs
            assert call_kwargs['timeout'] == 30

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_generate_concurrent_calls(self, provider):
        """Test de llamadas concurrentes al LLM."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Concurrent response"
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('requests.post', return_value=mock_response):
            # Crear múltiples llamadas concurrentes
            tasks = [
                provider.generate("System", f"User prompt {i}")
                for i in range(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all(result == "Concurrent response" for result in results)

    @pytest.mark.unit
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_stream_async_generator_behavior(self, provider):
        """Test del comportamiento de generador asíncrono en stream."""
        prompt = "Test streaming behavior"
        
        stream_gen = provider.stream(prompt)
        
        # Verificar que es un generador asíncrono
        assert hasattr(stream_gen, '__aiter__')
        assert hasattr(stream_gen, '__anext__')
        
        # Consumir manualmente el generador
        first_token = await stream_gen.__anext__()
        assert first_token == "Test "


if __name__ == "__main__":
    pytest.main([__file__, "-v"])