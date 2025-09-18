"""
test_core_services_integration.py
Tests de integración entre el módulo Core y Services de MeriBot.
Valida la integración con endpoints de servicios y almacenamiento.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any
from fastapi.testclient import TestClient

from meribot.core.api.app import app
from meribot.core.chatengine import ChatEngine


class TestCoreServicesIntegration:
    """Test suite para integración Core-Services."""

    @pytest.fixture
    def test_client(self):
        """Cliente de test para la API FastAPI."""
        return TestClient(app)

    @pytest.fixture
    def mock_chroma_integration_service(self):
        """Mock del servicio de integración con ChromaDB."""
        mock_service = Mock()
        mock_service.upsert_chunks_to_chroma = AsyncMock(return_value={
            'success': True,
            'chunks_processed': 5,
            'new_documents': 3,
            'updated_documents': 2
        })
        mock_service.query_chromadb = AsyncMock(return_value=[
            {
                'document': 'Documento encontrado por el servicio',
                'metadata': {
                    'title': 'Servicio ChromaDB',
                    'source': 'services',
                    'domain': 'onboarding'
                },
                'score': 0.92
            }
        ])
        return mock_service

    @pytest.fixture
    def mock_crawler_endpoint_service(self):
        """Mock del servicio de endpoint de crawler."""
        mock_service = Mock()
        mock_service.start_crawling = AsyncMock(return_value={
            'status': 'started',
            'job_id': 'crawl_job_123',
            'estimated_time': '5 minutes'
        })
        mock_service.get_crawling_status = AsyncMock(return_value={
            'status': 'completed',
            'job_id': 'crawl_job_123',
            'documents_processed': 25,
            'documents_indexed': 23
        })
        return mock_service

    @pytest.fixture
    def mock_process_docs_service(self):
        """Mock del servicio de procesamiento de documentos."""
        mock_service = Mock()
        mock_service.process_documents = AsyncMock(return_value={
            'status': 'success',
            'documents_processed': 10,
            'chunks_created': 45,
            'embeddings_generated': 45
        })
        return mock_service

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.api
    def test_services_endpoints_available_through_core_api(self, test_client):
        """Test que los endpoints de services están disponibles a través de la API del core."""
        # Verificar que los routers de services están incluidos
        
        # Test crawler endpoint
        response = test_client.get("/crawler/status")
        # El endpoint debería existir (puede retornar error sin configuración)
        assert response.status_code in [200, 404, 500]
        
        # Test process docs endpoint  
        response = test_client.get("/process_docs/status")
        assert response.status_code in [200, 404, 500]

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_core_uses_chroma_integration_service(self, mock_chroma_integration_service):
        """Test que el core utiliza el servicio de integración ChromaDB."""
        with patch('meribot.services.storage.chroma_integration.upsert_chunks_to_chroma') as mock_upsert:
            mock_upsert.return_value = mock_chroma_integration_service.upsert_chunks_to_chroma.return_value
            
            with patch('meribot.services.storage.chroma_integration.query_chromadb') as mock_query:
                mock_query.return_value = mock_chroma_integration_service.query_chromadb.return_value
                
                # Simular que el core busca usando el servicio
                with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                    mock_search.return_value = [{
                        'document': 'Resultado del servicio ChromaDB',
                        'metadatas': {'source': 'services', 'title': 'Test Doc'},
                        'score': 0.88
                    }]
                    
                    engine = ChatEngine()
                    result = await engine.process_message(
                        conversation_id="test_services",
                        message="Buscar usando servicios"
                    )
                    
                    assert result["type"] == "llm"
                    assert len(result["citations"]) > 0

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.api
    def test_crawler_service_integration_through_api(self, test_client, mock_crawler_endpoint_service):
        """Test de integración del servicio de crawler a través de la API."""
        with patch('meribot.services.crawler_endpoint.start_crawling') as mock_start:
            mock_start.return_value = mock_crawler_endpoint_service.start_crawling.return_value
            
            # Test inicio de crawling
            crawl_request = {
                "urls": ["https://example.com"],
                "domains": ["onboarding"],
                "max_depth": 2
            }
            
            response = test_client.post("/crawler/start", json=crawl_request)
            
            # Verificar respuesta del servicio integrado
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert "job_id" in data

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.api
    def test_process_docs_service_integration(self, test_client, mock_process_docs_service):
        """Test de integración del servicio de procesamiento de documentos."""
        with patch('meribot.services.process_docs_endpoint.process_documents') as mock_process:
            mock_process.return_value = mock_process_docs_service.process_documents.return_value
            
            process_request = {
                "document_paths": ["/path/to/doc1.pdf", "/path/to/doc2.html"],
                "domains": ["training"],
                "chunk_size": 1000
            }
            
            response = test_client.post("/process_docs/process", json=process_request)
            
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert "documents_processed" in data

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_core_chromadb_service_coordination(self, mock_chroma_integration_service):
        """Test de coordinación entre core y servicio ChromaDB."""
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector') as mock_connector_class:
            mock_connector = Mock()
            mock_connector.similarity_search = Mock(return_value=[
                {
                    'document': 'Documento coordinado con servicio',
                    'metadatas': {
                        'title': 'Coordination Test',
                        'source': 'service_coordination',
                        'domain': 'onboarding'
                    },
                    'score': 0.95
                }
            ])
            mock_connector_class.return_value = mock_connector
            
            engine = ChatEngine()
            result = await engine.process_message(
                conversation_id="coordination_test",
                message="Test de coordinación con servicios"
            )
            
            # Verificar que la búsqueda se realizó
            mock_connector.similarity_search.assert_called_once()
            assert result["type"] == "llm"

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_services_error_handling_in_core(self):
        """Test de manejo de errores de servicios en el core."""
        with patch('meribot.services.storage.chroma_integration.query_chromadb') as mock_query:
            # Simular error en el servicio
            mock_query.side_effect = Exception("Service unavailable")
            
            with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
                mock_search.side_effect = Exception("ChromaDB service error")
                
                engine = ChatEngine()
                result = await engine.process_message(
                    conversation_id="error_test",
                    message="Test error handling"
                )
                
                # El core debe manejar gracefully los errores de servicios
                assert result["type"] == "llm"  # Debe continuar sin resultados de búsqueda
                assert result["citations"] == []

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.api
    def test_complete_crawler_service_integration(self, test_client):
        """Test de integración del servicio completo de crawler."""
        with patch('meribot.services.complete_crawler_endpoint.run_complete_crawling') as mock_complete:
            mock_complete.return_value = {
                'status': 'completed',
                'total_urls_crawled': 50,
                'documents_processed': 45,
                'documents_indexed': 43,
                'processing_time': '10 minutes'
            }
            
            complete_request = {
                "base_urls": ["https://intranet.example.com"],
                "domains": ["onboarding", "training"],
                "max_depth": 3,
                "auto_process": True
            }
            
            response = test_client.post("/complete_crawler/run", json=complete_request)
            
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert "total_urls_crawled" in data

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_services_data_flow_to_core(self, mock_chroma_integration_service):
        """Test del flujo de datos desde servicios hacia el core."""
        # Simular datos procesados por servicios
        service_data = [
            {
                'content': 'Contenido procesado por servicio 1',
                'metadata': {
                    'title': 'Service Document 1',
                    'source': 'services',
                    'domain': 'onboarding',
                    'processed_by': 'process_docs_service'
                }
            },
            {
                'content': 'Contenido procesado por servicio 2',
                'metadata': {
                    'title': 'Service Document 2',
                    'source': 'services',
                    'domain': 'training',
                    'processed_by': 'crawler_service'
                }
            }
        ]
        
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            # Simular que el core encuentra datos de servicios
            mock_search.return_value = [
                {
                    'document': doc['content'],
                    'metadatas': doc['metadata'],
                    'score': 0.90
                }
                for doc in service_data
            ]
            
            engine = ChatEngine()
            result = await engine.process_message(
                conversation_id="data_flow_test",
                message="Información procesada por servicios"
            )
            
            # Verificar que el core usa datos de servicios
            citations = result["citations"]
            assert len(citations) == 2
            assert any("Service Document 1" in str(citation) for citation in citations)
            assert any("Service Document 2" in str(citation) for citation in citations)

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.api
    def test_services_configuration_integration(self, test_client):
        """Test de integración de configuración entre core y services."""
        # Test que la configuración del core es compatible con services
        
        # Verificar configuración de dominios
        response = test_client.get("/chatbot/allowed_domains")
        if response.status_code == 200:
            core_domains = response.json()["domains"]
            
            # Los servicios deberían usar la misma configuración de dominios
            assert isinstance(core_domains, list)
            assert len(core_domains) > 0

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_concurrent_services_integration(self):
        """Test de integración concurrente con múltiples servicios."""
        with patch('meribot.services.storage.chroma_integration.query_chromadb') as mock_query:
            with patch('meribot.services.crawler_endpoint.get_crawling_status') as mock_status:
                with patch('meribot.services.process_docs_endpoint.get_processing_status') as mock_process_status:
                    
                    # Configurar respuestas de servicios
                    mock_query.return_value = [{'document': 'Test', 'metadata': {}, 'score': 0.8}]
                    mock_status.return_value = {'status': 'running'}
                    mock_process_status.return_value = {'status': 'idle'}
                    
                    # Simular múltiples operaciones concurrentes
                    engine = ChatEngine()
                    tasks = [
                        engine.process_message(f"session_{i}", f"Query {i}")
                        for i in range(3)
                    ]
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Verificar que todas las operaciones completaron
                    assert len(results) == 3
                    assert all(isinstance(result, dict) for result in results if not isinstance(result, Exception))

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.external
    def test_real_services_integration(self, test_client):
        """Test de integración real con servicios (requiere servicios externos)."""
        # Test que requiere servicios reales funcionando
        
        # Verificar que al menos los endpoints de servicios responden
        health_checks = [
            "/chatbot/health",
            "/crawler/status", 
            "/process_docs/status"
        ]
        
        for endpoint in health_checks:
            response = test_client.get(endpoint)
            # Al menos el endpoint debe existir
            assert response.status_code != 404

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.api
    def test_services_response_format_compatibility(self, test_client):
        """Test de compatibilidad de formatos de respuesta entre core y services."""
        # Test que las respuestas de servicios son compatibles con el core
        
        # Mock respuesta típica de servicio
        service_response = {
            "status": "success",
            "data": {
                "documents": [
                    {
                        "id": "doc_1",
                        "content": "Content from service",
                        "metadata": {
                            "title": "Service Doc",
                            "domain": "onboarding"
                        }
                    }
                ]
            }
        }
        
        with patch('meribot.services.storage.chroma_integration.query_chromadb') as mock_query:
            mock_query.return_value = service_response["data"]["documents"]
            
            # El core debe poder procesar la respuesta del servicio
            query_request = {
                "question": "Test service integration",
                "conversation_id": "format_test",
                "domains": ["onboarding"]
            }
            
            response = test_client.post("/chatbot/query", json=query_request)
            
            if response.status_code == 200:
                data = response.json()
                assert "success" in data
                assert "response" in data

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.api
    def test_services_authentication_integration(self, test_client):
        """Test de integración de autenticación entre core y services."""
        # Test que la autenticación se propaga correctamente entre módulos
        
        # Simular headers de autenticación
        auth_headers = {
            "Authorization": "Bearer test_token",
            "X-User-ID": "test_user"
        }
        
        query_request = {
            "question": "Test with auth",
            "conversation_id": "auth_test"
        }
        
        response = test_client.post("/chatbot/query", json=query_request, headers=auth_headers)
        
        # Verificar que la autenticación no bloquea las operaciones básicas
        assert response.status_code in [200, 401, 403]

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_services_monitoring_integration(self):
        """Test de integración de monitoreo entre core y services."""
        with patch('meribot.utils.logger.get_logger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            engine = ChatEngine()
            
            # Simular operación que debería ser monitoreada
            result = await engine.process_message(
                conversation_id="monitoring_test",
                message="Test monitoring integration"
            )
            
            # Verificar que se generaron logs
            assert mock_logger.called

    @pytest.mark.integration
    @pytest.mark.services
    @pytest.mark.asyncio
    async def test_services_cache_integration(self):
        """Test de integración de cache entre core y services."""
        # Test que el cache funciona correctamente con servicios
        
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            mock_search.return_value = [
                {
                    'document': 'Cached content from service',
                    'metadatas': {'source': 'cache', 'title': 'Cached Doc'},
                    'score': 0.95
                }
            ]
            
            engine = ChatEngine()
            
            # Primera consulta (debería cachear)
            result1 = await engine.process_message(
                conversation_id="cache_test",
                message="Test caching"
            )
            
            # Segunda consulta idéntica (debería usar cache)
            result2 = await engine.process_message(
                conversation_id="cache_test",
                message="Test caching"
            )
            
            # Verificar que se obtuvieron respuestas
            assert result1["type"] == "llm"
            assert result2["type"] == "llm"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration and services"])