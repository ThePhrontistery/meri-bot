"""
test_api_app.py
Tests unitarios para el módulo API de MeriBot (FastAPI).
Valida endpoints, manejo de errores, CORS y respuestas del chatbot.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
import json
import os
from typing import Dict, Any

# Import the FastAPI app
from meribot.core.api.app import app, QueryRequest


class TestFastAPIApp:
    """Test suite para la aplicación FastAPI principal."""

    @pytest.fixture
    def client(self):
        """Cliente de test para FastAPI."""
        return TestClient(app)

    @pytest.fixture
    def valid_query_request(self):
        """Request válido para el endpoint de query."""
        return {
            "question": "¿Cuáles son las políticas de onboarding?",
            "conversation_id": "test_123",
            "domains": ["onboarding", "training"]
        }

    @pytest.fixture
    def minimal_query_request(self):
        """Request mínimo válido."""
        return {
            "question": "¿Qué es el onboarding?"
        }

    @pytest.mark.unit
    @pytest.mark.api
    def test_health_check_endpoint(self, client):
        """Test del endpoint de health check."""
        response = client.get("/chatbot/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "meribot-api"

    @pytest.mark.unit
    @pytest.mark.api
    def test_options_chatbot_endpoint(self, client):
        """Test del endpoint OPTIONS para CORS preflight."""
        response = client.options("/chatbot/query")
        
        assert response.status_code == status.HTTP_200_OK
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "Access-Control-Allow-Methods" in response.headers
        
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.core.api.app.chat_engine')
    async def test_query_chatbot_successful_response(self, mock_chat_engine, client, valid_query_request):
        """Test de consulta exitosa al chatbot."""
        # Configurar mock del chat engine
        mock_chat_engine.process_message = AsyncMock(return_value={
            "type": "llm",
            "response": "Las políticas de onboarding incluyen orientación inicial...",
            "citations": [
                {"title": "Manual de Onboarding", "url": "https://intranet.cca.com/onboarding"}
            ],
            "source": "llm",
            "conversation_id": "test_123"
        })

        response = client.post("/chatbot/query", json=valid_query_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "response" in data
        assert "conversation_id" in data
        assert "intent" in data
        assert "confidence" in data
        assert "citations" in data
        
        # Verificar contenido
        assert data["response"] == "Las políticas de onboarding incluyen orientación inicial..."
        assert data["conversation_id"] == "test_123"
        assert data["intent"] == "llm"
        assert data["confidence"] == 1.0
        assert len(data["citations"]) == 1
        assert data["citations"][0]["title"] == "Manual de Onboarding"
        
        # Verificar headers CORS
        assert "Access-Control-Allow-Origin" in response.headers

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.core.api.app.chat_engine')
    def test_query_chatbot_minimal_request(self, mock_chat_engine, client, minimal_query_request):
        """Test con request mínimo (solo question)."""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "type": "llm",
            "response": "Respuesta básica",
            "citations": [],
            "source": "llm",
            "conversation_id": "anonymous"
        })

        response = client.post("/chatbot/query", json=minimal_query_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversation_id"] == "anonymous"
        assert "response" in data

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.core.api.app.chat_engine')
    def test_query_chatbot_validation_error(self, mock_chat_engine, client):
        """Test de error de validación."""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "type": "validation_error",
            "response": "Error de validación: El mensaje no puede estar vacío",
            "citations": [],
            "source": "validation",
            "error": "El mensaje no puede estar vacío",
            "conversation_id": "test_123"
        })

        invalid_request = {
            "question": "",  # Question vacía
            "conversation_id": "test_123"
        }

        response = client.post("/chatbot/query", json=invalid_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["intent"] == "validation_error"
        assert data["confidence"] == 0.0
        assert "error" in data

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.core.api.app.chat_engine')
    def test_query_chatbot_llm_error(self, mock_chat_engine, client, valid_query_request):
        """Test cuando el LLM falla."""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "type": "llm",
            "response": "[Error al generar respuesta]",
            "citations": [],
            "source": "llm",
            "conversation_id": "test_123"
        })

        response = client.post("/chatbot/query", json=valid_query_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["intent"] == "no_answer"
        assert data["confidence"] == 0.0
        assert "Lo siento, no he podido encontrar información relevante" in data["response"]

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.core.api.app.chat_engine')
    def test_query_chatbot_exception_handling(self, mock_chat_engine, client, valid_query_request):
        """Test de manejo de excepciones inesperadas."""
        mock_chat_engine.process_message = AsyncMock(side_effect=Exception("Error inesperado"))

        response = client.post("/chatbot/query", json=valid_query_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["intent"] == "error"
        assert data["confidence"] == 0.0
        assert "error" in data
        assert "Lo siento, ha ocurrido un error" in data["response"]

    @pytest.mark.unit
    @pytest.mark.api
    def test_query_chatbot_invalid_json(self, client):
        """Test con JSON inválido."""
        response = client.post(
            "/chatbot/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.unit
    @pytest.mark.api
    def test_query_chatbot_missing_question(self, client):
        """Test sin el campo question requerido."""
        invalid_request = {
            "conversation_id": "test_123"
            # Falta "question"
        }

        response = client.post("/chatbot/query", json=invalid_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.utils.utils.load_config_from_yaml')
    def test_get_allowed_domains_success(self, mock_load_config, client):
        """Test exitoso del endpoint de dominios permitidos."""
        mock_load_config.return_value = ["onboarding", "training", "cca", "sdo"]

        response = client.get("/chatbot/allowed_domains")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "allowed_domains" in data
        assert len(data["allowed_domains"]) == 4
        assert "onboarding" in data["allowed_domains"]

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.utils.utils.load_config_from_yaml')
    def test_get_allowed_domains_not_found(self, mock_load_config, client):
        """Test cuando no se encuentran dominios en la configuración."""
        mock_load_config.return_value = None

        response = client.get("/chatbot/allowed_domains")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "No se encontraron dominios permitidos" in data["detail"]

    @pytest.mark.unit
    @pytest.mark.api
    def test_root_endpoint_widget_exists(self, client):
        """Test del endpoint raíz cuando existe el widget."""
        # Para este test, asumimos que el widget no existe en el entorno de test
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        # Debería devolver JSON cuando no encuentra el archivo
        data = response.json()
        assert "message" in data
        assert "MeriBot API funcionando correctamente" in data["message"]

    @pytest.mark.unit
    @pytest.mark.api
    def test_widget_endpoint_not_found(self, client):
        """Test del endpoint /widget cuando no existe el archivo."""
        response = client.get("/widget")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Widget no encontrado" in data["detail"]

    @pytest.mark.unit
    @pytest.mark.api
    def test_cors_headers_present(self, client, valid_query_request):
        """Test que verifica la presencia de headers CORS."""
        with patch('meribot.core.api.app.chat_engine.process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                "type": "llm",
                "response": "Test response",
                "citations": [],
                "source": "llm",
                "conversation_id": "test"
            }
            
            response = client.post("/chatbot/query", json=valid_query_request)
            
            # Verificar headers CORS
            assert "Access-Control-Allow-Origin" in response.headers
            assert response.headers["Access-Control-Allow-Origin"] == "*"

    @pytest.mark.unit
    @pytest.mark.api
    @patch('meribot.core.api.app.chat_engine')
    def test_query_response_format_validation(self, mock_chat_engine, client, valid_query_request):
        """Test que valida el formato de respuesta."""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "type": "llm",
            "response": "Respuesta de prueba",
            "citations": [{"title": "Test", "url": "http://test.com"}],
            "source": "llm",
            "conversation_id": "test_123"
        })

        response = client.post("/chatbot/query", json=valid_query_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar campos requeridos
        required_fields = ["response", "conversation_id", "intent", "confidence"]
        for field in required_fields:
            assert field in data, f"Campo requerido '{field}' no encontrado"
        
        # Verificar tipos de datos
        assert isinstance(data["confidence"], (int, float))
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["citations"], list)

    @pytest.mark.unit
    @pytest.mark.api
    def test_multiple_domains_handling(self, client):
        """Test con múltiples dominios en la request."""
        multi_domain_request = {
            "question": "¿Información sobre políticas?",
            "conversation_id": "test_multi",
            "domains": ["onboarding", "training", "cca"]
        }

        with patch('meribot.core.api.app.chat_engine.process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                "type": "llm",
                "response": "Información de múltiples dominios",
                "citations": [],
                "source": "llm",
                "conversation_id": "test_multi"
            }
            
            response = client.post("/chatbot/query", json=multi_domain_request)
            
            assert response.status_code == status.HTTP_200_OK
            
            # Verificar que se pasaron los dominios correctamente al chat engine
            mock_process.assert_called_once()
            call_args = mock_process.call_args
            assert call_args[1]["domains"] == ["onboarding", "training", "cca"]


class TestQueryRequestModel:
    """Tests para el modelo Pydantic QueryRequest."""

    @pytest.mark.unit
    @pytest.mark.validation
    def test_query_request_valid_full(self):
        """Test de QueryRequest con todos los campos."""
        request = QueryRequest(
            question="¿Cuáles son las políticas?",
            conversation_id="test_123",
            domains=["onboarding", "training"]
        )
        
        assert request.question == "¿Cuáles son las políticas?"
        assert request.conversation_id == "test_123"
        assert request.domains == ["onboarding", "training"]

    @pytest.mark.unit
    @pytest.mark.validation
    def test_query_request_minimal(self):
        """Test de QueryRequest con campos mínimos."""
        request = QueryRequest(question="Test question")
        
        assert request.question == "Test question"
        assert request.conversation_id is None
        assert request.domains is None

    @pytest.mark.unit
    @pytest.mark.validation
    def test_query_request_empty_question_fails(self):
        """Test que falla con question vacía."""
        with pytest.raises(ValueError):
            QueryRequest(question="")

    @pytest.mark.unit
    @pytest.mark.validation
    def test_query_request_missing_question_fails(self):
        """Test que falla sin question."""
        with pytest.raises(TypeError):
            QueryRequest(conversation_id="test")

    @pytest.mark.unit
    @pytest.mark.validation
    def test_query_request_empty_domains_list(self):
        """Test con lista de dominios vacía."""
        request = QueryRequest(
            question="Test",
            domains=[]
        )
        assert request.domains == []

    @pytest.mark.unit
    @pytest.mark.validation
    def test_query_request_none_domains(self):
        """Test con dominios None."""
        request = QueryRequest(
            question="Test",
            domains=None
        )
        assert request.domains is None


class TestCORSConfiguration:
    """Tests específicos para la configuración CORS."""

    @pytest.mark.unit
    @pytest.mark.api
    def test_cors_middleware_configuration(self, client):
        """Test de configuración del middleware CORS."""
        # Hacer una request para activar el middleware
        response = client.get("/chatbot/health")
        
        # El middleware debería estar configurado para permitir todos los origins
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.unit
    @pytest.mark.api
    def test_preflight_request_handling(self, client):
        """Test de manejo de requests preflight CORS."""
        # Simular una request preflight OPTIONS
        response = client.options(
            "/chatbot/query",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "Access-Control-Allow-Origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])