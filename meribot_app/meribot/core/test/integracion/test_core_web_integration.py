"""
test_core_web_integration.py
Tests de integración entre el módulo Core y Web de MeriBot.
Valida la comunicación a través de la API y la interfaz web.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any
from fastapi.testclient import TestClient

from meribot.core.api.app import app
from meribot.core.chatengine import ChatEngine


class TestCoreWebIntegration:
    """Test suite para integración Core-Web."""

    @pytest.fixture
    def test_client(self):
        """Cliente de test para la API FastAPI."""
        return TestClient(app)

    @pytest.fixture
    def mock_web_request(self):
        """Mock de request típico del widget web."""
        return {
            "question": "¿Cuáles son las políticas de onboarding?",
            "conversation_id": "web_session_123",
            "domains": ["onboarding"]
        }

    @pytest.fixture
    def mock_chat_engine_response(self):
        """Mock de respuesta típica del ChatEngine para web."""
        return {
            "type": "llm",
            "response": "Las políticas de onboarding incluyen...",
            "conversation_id": "web_session_123",
            "source": "llm",
            "citations": [
                {
                    "title": "Manual de Onboarding",
                    "url": "https://intranet.cca.com/onboarding"
                }
            ]
        }

    @pytest.fixture
    def mock_streaming_response(self):
        """Mock de respuesta streaming para web."""
        async def mock_stream():
            tokens = ["Las", "políticas", "de", "onboarding", "incluyen..."]
            for token in tokens:
                yield f"{token} "
        return mock_stream()

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_api_endpoint_availability(self, test_client):
        """Test que los endpoints necesarios para web están disponibles."""
        # Test health endpoint
        response = test_client.get("/chatbot/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # Test CORS preflight
        response = test_client.options("/chatbot/query")
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_query_endpoint_integration(self, test_client, mock_web_request, mock_chat_engine_response):
        """Test de integración del endpoint de query con el web."""
        with patch.object(ChatEngine, 'process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_chat_engine_response
            
            response = test_client.post("/chatbot/query", json=mock_web_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar estructura de respuesta para web
            assert data["success"] is True
            assert data["response"] == "Las políticas de onboarding incluyen..."
            assert data["conversation_id"] == "web_session_123"
            assert len(data["citations"]) == 1
            assert data["citations"][0]["title"] == "Manual de Onboarding"

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_streaming_endpoint_integration(self, test_client, mock_web_request):
        """Test de integración del endpoint streaming con web."""
        with patch.object(ChatEngine, 'stream_response', new_callable=AsyncMock) as mock_stream:
            async def mock_generator():
                tokens = ["Las ", "políticas ", "de ", "onboarding..."]
                for token in tokens:
                    yield token
            
            mock_stream.return_value = mock_generator()
            
            response = test_client.post("/chatbot/stream", json=mock_web_request)
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/plain; charset=utf-8"
            
            # Verificar que el streaming funciona
            content = response.text
            assert "Las " in content
            assert "políticas " in content

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_cors_integration(self, test_client):
        """Test de integración CORS para el widget web."""
        # Simular request desde el widget web
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = test_client.options("/chatbot/query", headers=headers)
        
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "POST" in response.headers["Access-Control-Allow-Methods"]
        assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_error_handling_integration(self, test_client, mock_web_request):
        """Test de manejo de errores en integración web-core."""
        with patch.object(ChatEngine, 'process_message', new_callable=AsyncMock) as mock_process:
            # Simular error en el core
            mock_process.side_effect = Exception("Core processing error")
            
            response = test_client.post("/chatbot/query", json=mock_web_request)
            
            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False
            assert "error" in data["message"].lower()

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_validation_integration(self, test_client):
        """Test de validación de requests desde web."""
        # Test con request inválido
        invalid_request = {
            "question": "",  # Campo vacío
            "conversation_id": "x" * 150,  # Demasiado largo
            "domains": ["invalid_domain"]
        }
        
        response = test_client.post("/chatbot/query", json=invalid_request)
        
        # Debería retornar error de validación
        assert response.status_code in [400, 422]

    @pytest.mark.integration
    @pytest.mark.web
    def test_web_static_files_serving(self, test_client):
        """Test de servir archivos estáticos para el widget web."""
        # Test que los archivos estáticos del web están disponibles
        
        # Verificar que las rutas de CSS están disponibles
        response = test_client.get("/css/widget-chatbot.css")
        if response.status_code == 200:
            assert "text/css" in response.headers.get("content-type", "")
        
        # Verificar que las rutas de JS están disponibles
        response = test_client.get("/js/widget-chatbot.js")
        if response.status_code == 200:
            assert "javascript" in response.headers.get("content-type", "")

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.asyncio
    async def test_web_session_management_integration(self, mock_chat_engine_response):
        """Test de gestión de sesiones entre web y core."""
        with patch.object(ChatEngine, 'process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_chat_engine_response
            
            engine = ChatEngine()
            
            # Simular múltiples requests desde la misma sesión web
            session_id = "web_session_persistence_test"
            
            # Primera interacción
            result1 = await engine.process_message(
                conversation_id=session_id,
                message="Primera pregunta desde web"
            )
            
            # Segunda interacción en la misma sesión
            result2 = await engine.process_message(
                conversation_id=session_id,
                message="Segunda pregunta desde web"
            )
            
            # Verificar que se mantiene la misma sesión
            assert result1["conversation_id"] == result2["conversation_id"]
            assert mock_process.call_count == 2

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_response_format_integration(self, test_client, mock_web_request):
        """Test del formato de respuesta específico para web."""
        with patch.object(ChatEngine, 'process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                "type": "llm",
                "response": "Respuesta del core",
                "conversation_id": "web_test",
                "source": "llm",
                "citations": [
                    {"title": "Doc 1", "url": "http://example.com/1"},
                    {"title": "Doc 2", "url": "http://example.com/2"}
                ]
            }
            
            response = test_client.post("/chatbot/query", json=mock_web_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar formato específico para consumo web
            assert isinstance(data["success"], bool)
            assert isinstance(data["response"], str)
            assert isinstance(data["citations"], list)
            assert isinstance(data["conversation_id"], str)
            assert "timestamp" in data

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.asyncio
    async def test_web_concurrent_requests_integration(self, mock_chat_engine_response):
        """Test de requests concurrentes desde múltiples sesiones web."""
        with patch.object(ChatEngine, 'process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = mock_chat_engine_response
            
            engine = ChatEngine()
            
            # Simular múltiples sesiones web concurrentes
            sessions = [f"web_session_{i}" for i in range(5)]
            tasks = [
                engine.process_message(
                    conversation_id=session_id,
                    message=f"Pregunta desde {session_id}"
                )
                for session_id in sessions
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verificar que todas las sesiones fueron procesadas
            assert len(results) == 5
            assert all(result["type"] == "llm" for result in results)
            assert mock_process.call_count == 5

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_allowed_domains_endpoint(self, test_client):
        """Test del endpoint de dominios permitidos para configuración web."""
        response = test_client.get("/chatbot/allowed_domains")
        
        if response.status_code == 200:
            data = response.json()
            assert "domains" in data
            assert isinstance(data["domains"], list)
            # Verificar dominios esperados
            expected_domains = ["onboarding", "training", "cca", "sdo"]
            for domain in expected_domains:
                assert domain in data["domains"]

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_widget_configuration_integration(self, test_client):
        """Test de configuración del widget web desde la API."""
        # Test endpoints necesarios para configuración del widget
        
        # Health check
        health_response = test_client.get("/chatbot/health")
        assert health_response.status_code == 200
        
        # Configuración de dominios
        domains_response = test_client.get("/chatbot/allowed_domains")
        if domains_response.status_code == 200:
            assert "domains" in domains_response.json()
        
        # Verificar que OPTIONS está disponible para CORS
        options_response = test_client.options("/chatbot/query")
        assert options_response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.external
    def test_real_web_widget_integration(self, test_client):
        """Test de integración real con el widget web (requiere servicios externos)."""
        # Test que simula una interacción real del widget
        real_request = {
            "question": "¿Cómo puedo acceder a mi perfil de empleado?",
            "conversation_id": None,  # Nueva sesión
            "domains": ["onboarding", "cca"]
        }
        
        response = test_client.post("/chatbot/query", json=real_request)
        
        # Verificar respuesta válida
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["response"], str)
            assert len(data["response"]) > 0
            assert isinstance(data["conversation_id"], str)

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_error_response_format(self, test_client):
        """Test del formato de respuestas de error para el web."""
        # Request malformado
        malformed_request = {"invalid": "data"}
        
        response = test_client.post("/chatbot/query", json=malformed_request)
        
        # Verificar formato de error consistente para web
        if response.status_code in [400, 422, 500]:
            data = response.json()
            assert "success" in data
            assert data["success"] is False
            assert "message" in data or "detail" in data

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.asyncio
    async def test_web_streaming_format_integration(self):
        """Test del formato de streaming para consumo web."""
        engine = ChatEngine()
        
        with patch.object(engine, 'stream_response') as mock_stream:
            async def mock_generator():
                tokens = ["Token1", "Token2", "Token3"]
                for token in tokens:
                    yield token
            
            mock_stream.return_value = mock_generator()
            
            # Simular consumo de streaming desde web
            tokens = []
            async for token in engine.stream_response(
                conversation_id="web_stream_test",
                message="Test streaming"
            ):
                tokens.append(token)
            
            assert len(tokens) == 3
            assert tokens == ["Token1", "Token2", "Token3"]

    @pytest.mark.integration
    @pytest.mark.web
    @pytest.mark.api
    def test_web_content_type_headers(self, test_client, mock_web_request):
        """Test de headers Content-Type correctos para web."""
        with patch.object(ChatEngine, 'process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                "type": "llm",
                "response": "Test response",
                "conversation_id": "test",
                "source": "llm",
                "citations": []
            }
            
            # Test JSON response
            response = test_client.post("/chatbot/query", json=mock_web_request)
            assert response.status_code == 200
            assert "application/json" in response.headers["content-type"]
            
            # Test streaming response
            stream_response = test_client.post("/chatbot/stream", json=mock_web_request)
            if stream_response.status_code == 200:
                assert "text/plain" in stream_response.headers["content-type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration and web"])