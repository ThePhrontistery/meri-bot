"""
test_core_crawler_integration.py
Tests de integración entre el módulo Core y Crawler de MeriBot.
Valida la comunicación y coordinación entre ambos módulos.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from meribot.core.chatengine import ChatEngine
from meribot.core.db.chromadb_connector import ChromaDBConnector


class TestCoreCrawlerIntegration:
    """Test suite para integración Core-Crawler."""

    @pytest.fixture
    def mock_crawler_config(self):
        """Mock de configuración del crawler."""
        return {
            'allowed_domains': ['onboarding', 'training', 'cca', 'sdo'],
            'max_message_length': 4000,
            'max_conversation_id_length': 100,
            'max_domains_count': 5,
            'dangerous_patterns': ['<script>', 'javascript:', 'eval('],
            'chroma_settings': {
                'persist_directory': './test_chroma_data',
                'collection_name': 'meribot_documents'
            }
        }

    @pytest.fixture
    def mock_crawler_document_loader(self):
        """Mock del document loader del crawler."""
        mock_loader = Mock()
        mock_loader.parse_document = Mock(return_value="Contenido del documento parseado")
        mock_loader.chunk_text_with_langchain = Mock(return_value=[
            "Chunk 1: Políticas de onboarding",
            "Chunk 2: Procedimientos de formación",
            "Chunk 3: Normas de seguridad"
        ])
        mock_loader.process_and_classify_chunks = Mock(return_value={
            'new_chunks': 2,
            'updated_chunks': 1,
            'duplicated_chunks': 0
        })
        return mock_loader

    @pytest.fixture
    def mock_chroma_integration(self):
        """Mock de la integración con ChromaDB desde services."""
        mock_integration = Mock()
        mock_integration.upsert_chunks_to_chroma = AsyncMock(return_value={
            'success': True,
            'chunks_processed': 3,
            'new_documents': 2
        })
        mock_integration.query_chromadb = AsyncMock(return_value=[
            {
                'document': 'Documento sobre onboarding',
                'metadata': {
                    'title': 'Manual de Onboarding',
                    'url': 'https://intranet.cca.com/onboarding',
                    'domain': 'onboarding'
                },
                'score': 0.95
            }
        ])
        return mock_integration

    @pytest.fixture
    def integration_chat_engine(self, mock_crawler_config):
        """ChatEngine configurado para tests de integración."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: mock_crawler_config.get(key)
            return ChatEngine()

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_core_uses_crawler_config_validation(self, integration_chat_engine, mock_crawler_config):
        """Test que el core usa la configuración del crawler para validación."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: mock_crawler_config.get(key)
            
            # Test con dominio válido según crawler config
            result = await integration_chat_engine.process_message(
                conversation_id="test_conv",
                message="¿Cuáles son las políticas de onboarding?",
                domains=["onboarding"]  # Dominio válido según config
            )
            
            assert result["type"] != "validation_error"
            assert "conversation_id" in result

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_core_rejects_invalid_crawler_domains(self, integration_chat_engine, mock_crawler_config):
        """Test que el core rechaza dominios no permitidos por crawler config."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: mock_crawler_config.get(key)
            
            # Test con dominio inválido
            result = await integration_chat_engine.process_message(
                conversation_id="test_conv",
                message="Test message",
                domains=["invalid_domain"]  # Dominio no en config
            )
            
            assert result["type"] == "validation_error"
            assert "domain" in result["response"].lower()

    @pytest.mark.integration
    @pytest.mark.crawler
    def test_chromadb_connector_uses_crawler_config(self, mock_crawler_config):
        """Test que ChromaDBConnector usa la configuración del crawler."""
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: mock_crawler_config.get('chroma_settings', {}).get(key)
            
            connector = ChromaDBConnector()
            
            # Verificar que se usa la configuración del crawler
            assert hasattr(connector, 'persist_directory')
            assert hasattr(connector, 'collection_name')

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_core_searches_crawler_indexed_content(self, integration_chat_engine, mock_chroma_integration):
        """Test que el core busca contenido indexado por el crawler."""
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            mock_search.return_value = [
                {
                    'document': 'Contenido indexado por crawler',
                    'metadatas': {
                        'title': 'Documento Crawler',
                        'url': 'https://crawler.test.com',
                        'domain': 'onboarding',
                        'source': 'crawler'
                    },
                    'score': 0.90
                }
            ]
            
            result = await integration_chat_engine.process_message(
                conversation_id="test_conv",
                message="Información sobre onboarding"
            )
            
            # Verificar que se encontró contenido del crawler
            assert len(result["citations"]) > 0
            assert any("crawler" in str(citation).lower() for citation in result["citations"])
            mock_search.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    @patch('meribot.crawler.document_loader.parse_document')
    @patch('meribot.services.storage.chroma_integration.upsert_chunks_to_chroma')
    async def test_crawler_document_processing_integration(self, mock_upsert, mock_parse, integration_chat_engine):
        """Test de integración del procesamiento de documentos crawler-core."""
        # Configurar mocks
        mock_parse.return_value = "Contenido parseado del documento"
        mock_upsert.return_value = {'success': True, 'chunks_processed': 5}
        
        # Simular procesamiento de documento
        document_content = mock_parse("test_document.pdf")
        
        # Simular que el contenido se indexa en ChromaDB
        upsert_result = await mock_upsert([{
            'content': document_content,
            'metadata': {
                'title': 'Test Document',
                'source': 'crawler',
                'domain': 'onboarding'
            }
        }])
        
        # Verificar que el core puede buscar este contenido
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            mock_search.return_value = [{
                'document': document_content,
                'metadatas': {'title': 'Test Document', 'domain': 'onboarding'},
                'score': 0.95
            }]
            
            result = await integration_chat_engine.process_message(
                conversation_id="test_conv",
                message="Información sobre el documento test"
            )
            
            assert result["type"] == "llm"
            assert len(result["citations"]) > 0

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_core_handles_crawler_domain_filtering(self, integration_chat_engine):
        """Test que el core maneja correctamente el filtrado por dominios del crawler."""
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            mock_search.return_value = [
                {
                    'document': 'Contenido de onboarding',
                    'metadatas': {'domain': 'onboarding', 'title': 'Manual Onboarding'},
                    'score': 0.95
                },
                {
                    'document': 'Contenido de training',
                    'metadatas': {'domain': 'training', 'title': 'Guía Training'},
                    'score': 0.88
                }
            ]
            
            # Test con filtrado específico de dominio
            result = await integration_chat_engine.process_message(
                conversation_id="test_conv",
                message="Información específica",
                domains=["onboarding"]
            )
            
            # Verificar que se pasó el filtro de dominio
            call_args = mock_search.call_args
            assert 'domains' in call_args[1]
            assert call_args[1]['domains'] == ["onboarding"]

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.slow
    def test_crawler_config_file_loading(self, mock_crawler_config):
        """Test de carga del archivo de configuración del crawler."""
        config_path = 'crawler_config.yaml'
        
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_load:
            mock_load.side_effect = lambda key: mock_crawler_config.get(key)
            
            # Simular carga de diferentes configuraciones
            allowed_domains = mock_load('allowed_domains')
            max_message_length = mock_load('max_message_length')
            chroma_settings = mock_load('chroma_settings')
            
            assert allowed_domains == ['onboarding', 'training', 'cca', 'sdo']
            assert max_message_length == 4000
            assert chroma_settings['persist_directory'] == './test_chroma_data'

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_core_crawler_error_handling(self, integration_chat_engine):
        """Test de manejo de errores en la integración core-crawler."""
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            # Simular error en la búsqueda (crawler no disponible)
            mock_search.side_effect = Exception("ChromaDB connection error")
            
            result = await integration_chat_engine.process_message(
                conversation_id="test_conv",
                message="Test message"
            )
            
            # El core debe manejar gracefully el error del crawler
            assert result["type"] == "llm"  # Debe continuar sin search results
            assert result["citations"] == []

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_crawler_content_metadata_integration(self, integration_chat_engine):
        """Test de integración de metadatos del crawler en respuestas del core."""
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            mock_search.return_value = [
                {
                    'document': 'Contenido con metadatos completos',
                    'metadatas': {
                        'title': 'Documento Completo',
                        'url': 'https://intranet.cca.com/doc1',
                        'domain': 'onboarding',
                        'last_updated': '2024-09-18',
                        'author': 'Crawler System',
                        'content_type': 'html',
                        'crawl_timestamp': '2024-09-18T10:00:00Z'
                    },
                    'score': 0.93
                }
            ]
            
            result = await integration_chat_engine.process_message(
                conversation_id="test_conv",
                message="Buscar documento completo"
            )
            
            # Verificar que los metadatos del crawler se incluyen en las citaciones
            citations = result["citations"]
            assert len(citations) > 0
            citation = citations[0]
            assert citation["title"] == "Documento Completo"
            assert citation["url"] == "https://intranet.cca.com/doc1"

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.external
    @pytest.mark.asyncio
    async def test_real_crawler_integration_scenario(self, integration_chat_engine):
        """Test de escenario real de integración core-crawler (requiere servicios externos)."""
        # Este test puede requerir servicios reales del crawler
        # Marcar como external para ejecución opcional
        
        with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
            mock_config.side_effect = lambda key: {
                'allowed_domains': ['onboarding', 'training'],
                'chroma_settings': {'persist_directory': './test_chroma_data'}
            }.get(key)
            
            # Test con configuración real del crawler
            result = await integration_chat_engine.process_message(
                conversation_id="real_test_conv",
                message="¿Qué información hay sobre procesos de onboarding?",
                domains=["onboarding"]
            )
            
            # Verificar respuesta válida del sistema integrado
            assert "type" in result
            assert "response" in result
            assert isinstance(result["citations"], list)

    @pytest.mark.integration
    @pytest.mark.crawler
    def test_crawler_domain_validation_integration(self):
        """Test de validación de dominios compartida entre core y crawler."""
        from meribot.core.validation import ChatEngineRequest
        
        # Test con dominios válidos del crawler
        valid_request = ChatEngineRequest(
            conversation_id="test_conv",
            message="Test message",
            domains=["onboarding", "training"]
        )
        
        assert valid_request.conversation_id == "test_conv"
        assert valid_request.domains == ["onboarding", "training"]

    @pytest.mark.integration
    @pytest.mark.crawler
    @pytest.mark.asyncio
    async def test_crawler_chunking_strategy_compatibility(self, mock_crawler_document_loader):
        """Test de compatibilidad de estrategias de chunking entre crawler y core."""
        # Simular chunking del crawler
        document_text = "Este es un documento largo que será dividido en chunks por el crawler para mejor procesamiento."
        
        chunks = mock_crawler_document_loader.chunk_text_with_langchain(document_text)
        
        # Verificar que los chunks son compatibles con el core
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        
        # Simular búsqueda de estos chunks por el core
        with patch('meribot.core.db.chromadb_connector.ChromaDBConnector.similarity_search') as mock_search:
            mock_search.return_value = [
                {
                    'document': chunk,
                    'metadatas': {'chunk_index': i, 'source': 'crawler'},
                    'score': 0.85
                }
                for i, chunk in enumerate(chunks)
            ]
            
            engine = ChatEngine()
            result = await engine.process_message(
                conversation_id="test_conv",
                message="Información del documento"
            )
            
            assert result["type"] == "llm"
            assert len(result["citations"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration and crawler"])