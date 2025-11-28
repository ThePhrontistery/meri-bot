"""
Tests unitarios para meribot.core.api.app
"""

import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from fastapi.testclient import TestClient
from fastapi import status

# Import después de configurar el entorno de test
from meribot.core.api.app import app, QueryRequest


class TestFastAPIApp:
    """Tests para la aplicación FastAPI"""
    
    @pytest.fixture
    def client(self):
        """Fixture que proporciona un cliente de test para FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_chat_engine(self):
        """Fixture que mockea ChatEngine"""
        with patch('meribot.core.api.app.ChatEngine') as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance
            yield mock_instance
    
    def test_app_creation(self):
        """Test que la aplicación FastAPI se crea correctamente"""
        assert app.title == "MeriBot API"
        assert app.description == "API para el servicio de chatbot de C&CA"
        assert app.version == "0.1.0"
    
    def test_cors_middleware_configured(self):
        """Test que CORS está configurado correctamente"""
        # Verificar que el middleware CORS está presente
        cors_middleware = None
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None


class TestQueryRequest:
    """Tests para el modelo QueryRequest"""
    
    def test_query_request_basic(self):
        """Test creación básica de QueryRequest"""
        request = QueryRequest(question="¿Cómo solicito vacaciones?")
        
        assert request.question == "¿Cómo solicito vacaciones?"
        assert request.conversation_id is None
        assert request.domains is None
    
    def test_query_request_full(self):
        """Test QueryRequest con todos los campos"""
        request = QueryRequest(
            question="¿Cuáles son las políticas de la empresa?",
            conversation_id="conv_123",
            domains=["onboarding", "training"]
        )
        
        assert request.question == "¿Cuáles son las políticas de la empresa?"
        assert request.conversation_id == "conv_123"
        assert request.domains == ["onboarding", "training"]
    
    def test_query_request_empty_question(self):
        """Test QueryRequest permite pregunta vacía pero ChatEngine la rechazará"""
        # QueryRequest no tiene validaciones estrictas, pero ChatEngine sí
        request = QueryRequest(question="")
        assert request.question == ""  # QueryRequest permite esto
        
        # Pero ChatEngineRequest lo rechazaría
        from pydantic import ValidationError
        from meribot.core.validation import ChatEngineRequest
        
        with pytest.raises(ValidationError):
            ChatEngineRequest(conversation_id="test", message="")


class TestHealthEndpoint:
    """Tests para el endpoint de health check"""
    
    def test_health_check_success(self, client):
        """Test health check retorna status OK"""
        response = client.get("/chatbot/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "meribot-api"
    
    def test_health_check_response_format(self, client):
        """Test formato correcto de respuesta del health check"""
        response = client.get("/chatbot/health")
        
        data = response.json()
        
        # Verificar estructura de respuesta
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert len(data) == 2  # Solo estos dos campos


class TestAllowedDomainsEndpoint:
    """Tests para el endpoint de dominios permitidos"""
    
    @patch('meribot.core.api.app.load_config_from_yaml')
    def test_get_allowed_domains_success(self, mock_load_config, client):
        """Test obtener dominios permitidos exitosamente"""
        mock_load_config.return_value = ["onboarding", "training", "cca", "sdo"]
        
        response = client.get("/chatbot/allowed_domains")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "allowed_domains" in data
        assert data["allowed_domains"] == ["onboarding", "training", "cca", "sdo"]
    
    @patch('meribot.core.api.app.load_config_from_yaml')
    def test_get_allowed_domains_not_found(self, mock_load_config, client):
        """Test fallo cuando no se encuentran dominios"""
        mock_load_config.return_value = None
        
        response = client.get("/chatbot/allowed_domains")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "No se encontraron dominios permitidos" in data["detail"]
    
    @patch('meribot.core.api.app.load_config_from_yaml')
    def test_get_allowed_domains_empty_list(self, mock_load_config, client):
        """Test con lista vacía de dominios"""
        mock_load_config.return_value = []
        
        response = client.get("/chatbot/allowed_domains")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["allowed_domains"] == []


class TestChatbotQueryEndpoint:
    """Tests para el endpoint principal de chatbot"""
    
    @pytest.fixture
    def sample_request_data(self):
        """Fixture con datos de request de ejemplo"""
        return {
            "question": "¿Cómo puedo solicitar vacaciones?",
            "conversation_id": "conv_123",
            "domains": ["onboarding"]
        }
    
    @patch('meribot.core.api.app.chat_engine')
    def test_chatbot_query_success(self, mock_chat_engine, client, sample_request_data):
        """Test consulta exitosa al chatbot"""
        # Configurar mock del chat engine
        mock_chat_engine.process_message = AsyncMock(return_value={
            "response": "Para solicitar vacaciones, debes acceder al portal de RR.HH.",
            "conversation_id": "conv_123",
            "type": "llm",
            "citations": [{"title": "Política de Vacaciones", "url": "http://example.com/vacaciones"}],
            "source": "llm"
        })
        
        response = client.post("/chatbot/query", json=sample_request_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "intent" in data
        assert "confidence" in data
        assert data["confidence"] == 1.0
        assert "citations" in data
    
    @patch('meribot.core.api.app.chat_engine')
    def test_chatbot_query_validation_error(self, mock_chat_engine, client):
        """Test manejo de errores de validación"""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "type": "validation_error",
            "response": "Error de validación: mensaje vacío",
            "conversation_id": "conv_123",
            "error": "El mensaje no puede estar vacío"
        })
        
        request_data = {
            "question": "",  # Pregunta vacía para provocar error
            "conversation_id": "conv_123"
        }
        
        response = client.post("/chatbot/query", json=request_data)
        
        # Debería retornar 200 pero con error en la respuesta
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["intent"] == "validation_error"
        assert data["confidence"] == 0.0
        assert "error" in data
    
    @patch('meribot.core.api.app.chat_engine')
    def test_chatbot_query_no_answer(self, mock_chat_engine, client, sample_request_data):
        """Test cuando el chatbot no puede responder"""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "response": "[Error al generar respuesta]",
            "conversation_id": "conv_123",
            "type": "llm"
        })
        
        response = client.post("/chatbot/query", json=sample_request_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["intent"] == "no_answer"
        assert data["confidence"] == 0.0
        assert "no he podido encontrar información" in data["response"]
    
    @patch('meribot.core.api.app.chat_engine')
    def test_chatbot_query_exception(self, mock_chat_engine, client, sample_request_data):
        """Test manejo de excepciones internas"""
        mock_chat_engine.process_message = AsyncMock(side_effect=Exception("Error interno"))
        
        response = client.post("/chatbot/query", json=sample_request_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["intent"] == "error"
        assert data["confidence"] == 0.0
        assert "error" in data
        assert "ha ocurrido un error" in data["response"]
    
    def test_chatbot_query_invalid_json(self, client):
        """Test con JSON inválido"""
        response = client.post(
            "/chatbot/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_chatbot_query_missing_question(self, client):
        """Test sin campo question requerido"""
        request_data = {
            "conversation_id": "conv_123",
            "domains": ["onboarding"]
            # Falta 'question'
        }
        
        response = client.post("/chatbot/query", json=request_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "detail" in data
    
    @patch('meribot.core.api.app.chat_engine')
    def test_chatbot_query_without_conversation_id(self, mock_chat_engine, client):
        """Test consulta sin conversation_id"""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "response": "Respuesta de prueba",
            "conversation_id": "anonymous",
            "type": "llm"
        })
        
        request_data = {
            "question": "¿Cómo funciona esto?"
        }
        
        response = client.post("/chatbot/query", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que se llamó con conversation_id="anonymous"
        mock_chat_engine.process_message.assert_called_once_with(
            conversation_id="anonymous",
            message="¿Cómo funciona esto?",
            domains=None
        )


class TestOptionsEndpoint:
    """Tests para el endpoint OPTIONS de CORS"""
    
    def test_options_preflight(self, client):
        """Test OPTIONS preflight request"""
        response = client.options("/chatbot/query")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "ok"
        
        # Verificar headers CORS
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers


class TestStaticFiles:
    """Tests para servir archivos estáticos"""
    
    @patch('meribot.core.api.app.web_directory')
    def test_static_files_mounted_when_directory_exists(self, mock_web_dir):
        """Test que los archivos estáticos se montan cuando el directorio existe"""
        mock_web_dir.exists.return_value = True
        
        # Verificar que las rutas están montadas
        routes = [route.path for route in app.routes]
        
        assert any("/css" in route for route in routes)
        assert any("/js" in route for route in routes)
        assert any("/img" in route for route in routes)
        assert any("/static" in route for route in routes)


class TestFrontendRoutes:
    """Tests para las rutas del frontend"""
    
    @patch('meribot.core.api.app.web_directory')
    def test_root_endpoint_with_widget(self, mock_web_dir, client):
        """Test endpoint raíz cuando existe el widget"""
        mock_widget_file = MagicMock()
        mock_widget_file.exists.return_value = True
        mock_web_dir.__truediv__.return_value = mock_widget_file
        
        # Mock FileResponse
        with patch('meribot.core.api.app.FileResponse') as mock_file_response:
            mock_file_response.return_value = "widget content"
            
            response = client.get("/")
            
            assert response.status_code == status.HTTP_200_OK
    
    @patch('meribot.core.api.app.web_directory')
    def test_root_endpoint_without_widget(self, mock_web_dir, client):
        """Test endpoint raíz cuando no existe el widget"""
        mock_widget_file = MagicMock()
        mock_widget_file.exists.return_value = False
        mock_web_dir.__truediv__.return_value = mock_widget_file
        
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "MeriBot API funcionando correctamente" in data["message"]
    
    @patch('meribot.core.api.app.web_directory')
    def test_widget_endpoint_success(self, mock_web_dir, client):
        """Test endpoint /widget exitoso"""
        mock_widget_file = MagicMock()
        mock_widget_file.exists.return_value = True
        mock_web_dir.__truediv__.return_value = mock_widget_file
        
        with patch('meribot.core.api.app.FileResponse') as mock_file_response:
            mock_file_response.return_value = "widget content"
            
            response = client.get("/widget")
            
            assert response.status_code == status.HTTP_200_OK
    
    @patch('meribot.core.api.app.web_directory')
    def test_widget_endpoint_not_found(self, mock_web_dir, client):
        """Test endpoint /widget cuando no existe el archivo"""
        mock_widget_file = MagicMock()
        mock_widget_file.exists.return_value = False
        mock_web_dir.__truediv__.return_value = mock_widget_file
        
        response = client.get("/widget")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "detail" in data
        assert "Widget no encontrado" in data["detail"]


class TestIntegration:
    """Tests de integración para la API"""
    
    @patch('meribot.core.api.app.chat_engine')
    def test_full_conversation_flow(self, mock_chat_engine, client):
        """Test flujo completo de conversación"""
        # Configurar respuestas del chat engine para una conversación
        responses = [
            {
                "response": "Hola, ¿en qué puedo ayudarte?",
                "conversation_id": "conv_123",
                "type": "llm",
                "citations": []
            },
            {
                "response": "Para solicitar vacaciones, accede al portal de RR.HH.",
                "conversation_id": "conv_123", 
                "type": "llm",
                "citations": [{"title": "Portal RR.HH.", "url": "http://example.com"}]
            }
        ]
        
        mock_chat_engine.process_message = AsyncMock(side_effect=responses)
        
        # Primera consulta
        response1 = client.post("/chatbot/query", json={
            "question": "Hola",
            "conversation_id": "conv_123"
        })
        
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert "Hola" in data1["response"]
        
        # Segunda consulta en la misma conversación
        response2 = client.post("/chatbot/query", json={
            "question": "¿Cómo solicito vacaciones?",
            "conversation_id": "conv_123"
        })
        
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert "vacaciones" in data2["response"]
        assert len(data2["citations"]) > 0
    
    def test_api_documentation_available(self, client):
        """Test que la documentación de la API está disponible"""
        response = client.get("/docs")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema_available(self, client):
        """Test que el schema OpenAPI está disponible"""
        response = client.get("/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "MeriBot API"


class TestErrorHandling:
    """Tests para manejo de errores"""
    
    def test_unhandled_route(self, client):
        """Test ruta no manejada"""
        response = client.get("/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_method_not_allowed(self, client):
        """Test método no permitido"""
        response = client.delete("/chatbot/query")
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    @patch('meribot.core.api.app.chat_engine')
    def test_large_request_payload(self, mock_chat_engine, client):
        """Test con payload muy grande"""
        mock_chat_engine.process_message = AsyncMock(return_value={
            "response": "Respuesta",
            "conversation_id": "conv_123",
            "type": "llm"
        })
        
        large_question = "x" * 10000  # Pregunta muy larga
        
        request_data = {
            "question": large_question,
            "conversation_id": "conv_123"
        }
        
        response = client.post("/chatbot/query", json=request_data)
        
        # Debería procesar la request (el límite se maneja en validación)
        assert response.status_code == status.HTTP_200_OK


class TestSecurityFeatures:
    """Tests para características de seguridad"""
    
    def test_cors_headers_present(self, client, sample_request_data):
        """Test que los headers CORS están presentes"""
        response = client.post("/chatbot/query", json={
            "question": "Test question"
        })
        
        # Verificar headers CORS en la respuesta
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"
    
    def test_no_sensitive_info_in_errors(self, client):
        """Test que los errores no exponen información sensible"""
        # Intentar acceder a archivo que no existe
        response = client.get("/widget")
        
        if response.status_code == status.HTTP_404_NOT_FOUND:
            data = response.json()
            # Verificar que no se exponen paths del sistema
            assert "/Users/" not in str(data)
            assert "C:\\" not in str(data)
            assert "__file__" not in str(data)