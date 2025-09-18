"""
test_end_to_end_integration.py
Tests end-to-end que validan workflows completos de MeriBot.
Integra todos los módulos (core, crawler, web, services, utils) en escenarios reales.
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any
from fastapi.testclient import TestClient

from meribot.core.api.app import app
from meribot.core.chatengine import ChatEngine


class TestEndToEndIntegration:
    """Test suite para integración end-to-end completa."""

    @pytest.fixture
    def test_client(self):
        """Cliente de test para la API FastAPI."""
        return TestClient(app)

    @pytest.fixture
    def e2e_config(self):
        """Configuración completa para tests E2E."""
        return {
            'allowed_domains': ['onboarding', 'training', 'cca', 'sdo'],
            'max_message_length': 4000,
            'max_conversation_id_length': 100,
            'max_domains_count': 5,
            'dangerous_patterns': ['<script>', 'javascript:', 'eval('],
            'chroma_settings': {
                'persist_directory': './e2e_test_chroma_data',
                'collection_name': 'meribot_e2e_documents'
            },
            'llm_settings': {
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        }

    @pytest.fixture
    def e2e_documents(self):
        """Documentos de ejemplo para tests E2E."""
        return [
            {
                'id': 'e2e_doc_1',
                'content': 'El proceso de onboarding en C&CA incluye orientación inicial, configuración de accesos y formación básica.',
                'metadata': {
                    'title': 'Guía de Onboarding C&CA',
                    'url': 'https://intranet.cca.com/onboarding-guide',
                    'domain': 'onboarding',
                    'source': 'crawler',
                    'last_updated': '2024-09-18'
                }
            },
            {
                'id': 'e2e_doc_2',
                'content': 'Los procedimientos de seguridad requieren autenticación de dos factores y actualización regular de contraseñas.',
                'metadata': {
                    'title': 'Políticas de Seguridad',
                    'url': 'https://intranet.cca.com/security-policies',
                    'domain': 'cca',
                    'source': 'crawler',
                    'last_updated': '2024-09-15'
                }
            },
            {
                'id': 'e2e_doc_3',
                'content': 'El programa de formación continua incluye cursos técnicos, soft skills y certificaciones profesionales.',
                'metadata': {
                    'title': 'Programa de Formación Continua',
                    'url': 'https://intranet.cca.com/training-program',
                    'domain': 'training',
                    'source': 'services',
                    'last_updated': '2024-09-10'
                }
            }
        ]

    @pytest.fixture
    def e2e_system_prompt(self):
        """System prompt para tests E2E."""
        return """
        Eres MeriBot, el asistente virtual oficial de C&CA.
        Tu objetivo es ayudar a los empleados con información sobre:
        - Procesos de onboarding
        - Políticas de la empresa
        - Programas de formación
        - Procedimientos de seguridad
        
        Siempre responde de manera profesional y cita las fuentes cuando sea posible.
        Si no tienes información específica, indícalo claramente.
        """

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_complete_onboarding_workflow(self, e2e_config, e2e_documents, e2e_system_prompt):
        """Test del workflow completo: pregunta sobre onboarding desde web hasta respuesta."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            with patch('meribot.utils.utils.load_system_prompt') as mock_prompt:
                mock_prompt.return_value = e2e_system_prompt
                
                with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                    # Simular documentos encontrados por crawler
                    mock_search.return_value = [
                        {
                            'document': e2e_documents[0]['content'],
                            'metadatas': e2e_documents[0]['metadata'],
                            'score': 0.95
                        }
                    ]
                    
                    with patch('meribot.core.llm.llm_engine.LLMEngine.generate_response') as mock_llm:
                        mock_llm.return_value = "El proceso de onboarding en C&CA está bien estructurado e incluye orientación inicial, configuración de accesos y formación básica, según se describe en la Guía de Onboarding C&CA."
                        
                        # Simular el workflow completo
                        engine = ChatEngine()
                        
                        result = await engine.process_message(
                            conversation_id="e2e_onboarding_session",
                            message="¿Cómo es el proceso de onboarding en C&CA?",
                            domains=["onboarding"]
                        )
                        
                        # Verificar workflow completo
                        assert result["type"] == "llm"
                        assert "onboarding" in result["response"].lower()
                        assert len(result["citations"]) == 1
                        assert result["citations"][0]["title"] == "Guía de Onboarding C&CA"
                        assert result["conversation_id"] == "e2e_onboarding_session"
                        
                        # Verificar que se usaron todos los componentes
                        mock_config.assert_called()
                        mock_prompt.assert_called_once()
                        mock_search.assert_called_once()
                        mock_llm.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.web
    def test_web_to_core_complete_flow(self, test_client, e2e_config, e2e_documents):
        """Test del flujo completo desde widget web hasta respuesta del core."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                mock_search.return_value = [
                    {
                        'document': e2e_documents[1]['content'],
                        'metadatas': e2e_documents[1]['metadata'],
                        'score': 0.92
                    }
                ]
                
                with patch('meribot.core.llm.llm_engine.LLMEngine.generate_response') as mock_llm:
                    mock_llm.return_value = "Las políticas de seguridad de C&CA establecen que se requiere autenticación de dos factores y actualización regular de contraseñas para mantener la seguridad de los sistemas."
                    
                    # Request desde widget web
                    web_request = {
                        "question": "¿Cuáles son las políticas de seguridad?",
                        "conversation_id": "web_e2e_security_session",
                        "domains": ["cca"]
                    }
                    
                    response = test_client.post("/chatbot/query", json=web_request)
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Verificar flujo completo web -> API -> core -> respuesta
                    assert data["success"] is True
                    assert "seguridad" in data["response"].lower()
                    assert data["conversation_id"] == "web_e2e_security_session"
                    assert len(data["citations"]) == 1
                    assert data["citations"][0]["title"] == "Políticas de Seguridad"
                    assert "timestamp" in data

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_crawler_to_core_indexing_flow(self, e2e_config, e2e_documents):
        """Test del flujo desde crawling de documentos hasta búsqueda en core."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            # Simular documentos procesados por crawler
            with patch('meribot.crawler.document_loader.parse_document') as mock_parse:
                mock_parse.return_value = e2e_documents[2]['content']
                
                with patch('meribot.services.storage.chroma_integration.upsert_chunks_to_chroma') as mock_upsert:
                    mock_upsert.return_value = {
                        'success': True,
                        'chunks_processed': 3,
                        'new_documents': 1
                    }
                    
                    # Simular que el contenido está disponible para el core
                    with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                        mock_search.return_value = [
                            {
                                'document': e2e_documents[2]['content'],
                                'metadatas': e2e_documents[2]['metadata'],
                                'score': 0.89
                            }
                        ]
                        
                        with patch('meribot.core.llm.llm_engine.LLMEngine.generate_response') as mock_llm:
                            mock_llm.return_value = "El programa de formación continua de C&CA ofrece una amplia gama de oportunidades de desarrollo profesional."
                            
                            # Workflow completo: crawler -> indexing -> core search
                            engine = ChatEngine()
                            
                            result = await engine.process_message(
                                conversation_id="e2e_training_session",
                                message="¿Qué ofrece el programa de formación?",
                                domains=["training"]
                            )
                            
                            # Verificar que el core encuentra contenido indexado por crawler
                            assert result["type"] == "llm"
                            assert "formación" in result["response"].lower()
                            assert len(result["citations"]) == 1
                            assert result["citations"][0]["title"] == "Programa de Formación Continua"

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_services_orchestration_workflow(self, e2e_config, e2e_documents):
        """Test del workflow de orquestación completa con servicios."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            # Simular servicios funcionando en paralelo
            with patch('meribot.services.crawler_endpoint.get_crawling_status') as mock_crawler_status:
                mock_crawler_status.return_value = {'status': 'running', 'progress': 75}
                
                with patch('meribot.services.process_docs_endpoint.get_processing_status') as mock_docs_status:
                    mock_docs_status.return_value = {'status': 'idle', 'last_processed': 10}
                    
                    with patch('meribot.services.storage.chroma_integration.query_chromadb') as mock_service_query:
                        mock_service_query.return_value = e2e_documents
                        
                        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_core_search:
                            mock_core_search.return_value = [
                                {
                                    'document': doc['content'],
                                    'metadatas': doc['metadata'],
                                    'score': 0.85 + (i * 0.05)
                                }
                                for i, doc in enumerate(e2e_documents)
                            ]
                            
                            with patch('meribot.core.llm.llm_engine.LLMEngine.generate_response') as mock_llm:
                                mock_llm.return_value = "Basándome en la información disponible de onboarding, seguridad y formación..."
                                
                                # Workflow completo con todos los servicios
                                engine = ChatEngine()
                                
                                result = await engine.process_message(
                                    conversation_id="e2e_services_session",
                                    message="Dame información general sobre C&CA",
                                    domains=["onboarding", "cca", "training"]
                                )
                                
                                # Verificar orquestación completa
                                assert result["type"] == "llm"
                                assert len(result["citations"]) == 3
                                assert result["conversation_id"] == "e2e_services_session"

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.streaming
    @pytest.mark.asyncio
    async def test_streaming_e2e_workflow(self, e2e_config, e2e_system_prompt):
        """Test del workflow completo con streaming."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            with patch('meribot.utils.utils.load_system_prompt') as mock_prompt:
                mock_prompt.return_value = e2e_system_prompt
                
                with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                    mock_search.return_value = []  # Sin resultados para simplificar
                    
                    async def mock_streaming():
                        tokens = [
                            "El ", "sistema ", "de ", "streaming ", "funciona ", 
                            "correctamente ", "y ", "permite ", "respuestas ", 
                            "en ", "tiempo ", "real."
                        ]
                        for token in tokens:
                            yield token
                    
                    with patch('meribot.core.llm.llm_engine.LLMEngine.stream_response') as mock_stream:
                        mock_stream.return_value = mock_streaming()
                        
                        # Test streaming completo
                        engine = ChatEngine()
                        
                        tokens = []
                        async for token in engine.stream_response(
                            conversation_id="e2e_streaming_session",
                            message="Test streaming completo"
                        ):
                            tokens.append(token)
                        
                        # Verificar streaming completo
                        assert len(tokens) == 12
                        complete_response = "".join(tokens)
                        assert "streaming" in complete_response
                        assert "tiempo real" in complete_response

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.web
    def test_web_streaming_e2e_flow(self, test_client, e2e_config):
        """Test del flujo completo de streaming desde web."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            async def mock_web_streaming():
                tokens = ["Respuesta ", "streaming ", "desde ", "web ", "completada."]
                for token in tokens:
                    yield token
            
            with patch('meribot.core.chatengine.ChatEngine.stream_response') as mock_stream:
                mock_stream.return_value = mock_web_streaming()
                
                stream_request = {
                    "question": "Test streaming desde web",
                    "conversation_id": "web_e2e_streaming",
                    "domains": ["onboarding"]
                }
                
                response = test_client.post("/chatbot/stream", json=stream_request)
                
                assert response.status_code == 200
                assert "text/plain" in response.headers["content-type"]
                
                # Verificar contenido streaming
                content = response.text
                assert "streaming" in content
                assert "completada" in content

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_sessions_e2e_workflow(self, e2e_config, e2e_documents):
        """Test de múltiples sesiones concurrentes end-to-end."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                # Diferentes documentos para cada sesión
                def search_side_effect(*args, **kwargs):
                    query = kwargs.get('query', '')
                    if 'onboarding' in query.lower():
                        return [{'document': e2e_documents[0]['content'], 'metadatas': e2e_documents[0]['metadata'], 'score': 0.95}]
                    elif 'security' in query.lower():
                        return [{'document': e2e_documents[1]['content'], 'metadatas': e2e_documents[1]['metadata'], 'score': 0.92}]
                    else:
                        return [{'document': e2e_documents[2]['content'], 'metadatas': e2e_documents[2]['metadata'], 'score': 0.89}]
                
                mock_search.side_effect = search_side_effect
                
                with patch('meribot.core.llm.llm_engine.LLMEngine.generate_response') as mock_llm:
                    def llm_side_effect(*args, **kwargs):
                        message = kwargs.get('user_message', '')
                        if 'onboarding' in message.lower():
                            return "Información sobre onboarding procesada correctamente."
                        elif 'security' in message.lower():
                            return "Políticas de seguridad explicadas."
                        else:
                            return "Información general proporcionada."
                    
                    mock_llm.side_effect = llm_side_effect
                    
                    # Simular múltiples sesiones concurrentes
                    engine = ChatEngine()
                    
                    sessions = [
                        ("e2e_session_1", "¿Cómo es el onboarding?", ["onboarding"]),
                        ("e2e_session_2", "¿Cuáles son las políticas de security?", ["cca"]),
                        ("e2e_session_3", "Información sobre formación", ["training"]),
                        ("e2e_session_4", "Procesos generales", None),
                        ("e2e_session_5", "Ayuda con onboarding", ["onboarding"])
                    ]
                    
                    tasks = [
                        engine.process_message(session_id, message, domains)
                        for session_id, message, domains in sessions
                    ]
                    
                    results = await asyncio.gather(*tasks)
                    
                    # Verificar todas las sesiones concurrentes
                    assert len(results) == 5
                    assert all(result["type"] == "llm" for result in results)
                    
                    # Verificar respuestas específicas
                    assert "onboarding" in results[0]["response"].lower()
                    assert "seguridad" in results[1]["response"].lower()
                    assert "información" in results[2]["response"].lower()

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.external
    @pytest.mark.docker
    def test_docker_environment_e2e(self, test_client):
        """Test E2E en entorno Docker (requiere servicios externos)."""
        # Test que requiere entorno Docker completo
        
        # Verificar que los servicios principales responden
        health_endpoints = [
            "/chatbot/health",
            "/crawler/status",
            "/process_docs/status"
        ]
        
        for endpoint in health_endpoints:
            response = test_client.get(endpoint)
            # Al menos los endpoints deben existir
            assert response.status_code != 404

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_error_recovery_e2e_workflow(self, e2e_config):
        """Test de recuperación de errores en workflow E2E."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            # Simular errores en diferentes componentes
            with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                mock_search.side_effect = Exception("Database temporarily unavailable")
                
                with patch('meribot.core.llm.llm_engine.LLMEngine.generate_response') as mock_llm:
                    mock_llm.return_value = "Sistema funcionando en modo de recuperación."
                    
                    engine = ChatEngine()
                    
                    # El sistema debe recuperarse de errores
                    result = await engine.process_message(
                        conversation_id="e2e_error_recovery",
                        message="Test error recovery"
                    )
                    
                    # Verificar recuperación graceful
                    assert result["type"] == "llm"
                    assert result["citations"] == []  # Sin resultados por error de BD
                    assert "recuperación" in result["response"]

    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_e2e_workflow(self, e2e_config, e2e_documents):
        """Test de rendimiento del workflow E2E completo."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: e2e_config.get(key)
            
            with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                mock_search.return_value = [
                    {
                        'document': doc['content'],
                        'metadatas': doc['metadata'],
                        'score': 0.90
                    }
                    for doc in e2e_documents
                ]
                
                with patch('meribot.core.llm.llm_engine.LLMEngine.generate_response') as mock_llm:
                    mock_llm.return_value = "Respuesta optimizada para rendimiento."
                    
                    engine = ChatEngine()
                    
                    # Medir tiempo de operación completa
                    start_time = time.time()
                    
                    result = await engine.process_message(
                        conversation_id="e2e_performance",
                        message="Test de rendimiento completo"
                    )
                    
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    # Verificar rendimiento aceptable
                    assert execution_time < 2.0  # Menos de 2 segundos
                    assert result["type"] == "llm"
                    assert len(result["citations"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration and e2e"])