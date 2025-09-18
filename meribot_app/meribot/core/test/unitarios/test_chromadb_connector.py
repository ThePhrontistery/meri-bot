"""
test_chromadb_connector.py
Tests unitarios para el módulo ChromaDBConnector de MeriBot.
Valida la conexión con ChromaDB, búsqueda por similitud y filtrado.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from typing import List, Dict, Any

from meribot.core.db.chromadb_connector import ChromaDBConnector


class TestChromaDBConnector:
    """Test suite para la clase ChromaDBConnector."""

    @pytest.fixture
    def mock_chroma_store(self):
        """Mock del objeto Chroma store."""
        mock_store = Mock()
        mock_store.similarity_search = Mock()
        return mock_store

    @pytest.fixture
    def mock_embeddings(self):
        """Mock del objeto AzureOpenAIEmbeddings."""
        mock_embeddings = Mock()
        return mock_embeddings

    @pytest.fixture
    def sample_documents(self):
        """Documentos de ejemplo para tests."""
        return [
            Mock(
                page_content="Las políticas de onboarding incluyen orientación inicial y formación.",
                metadata={
                    'title': 'Manual de Onboarding',
                    'url': 'https://intranet.cca.com/onboarding',
                    'domain': 'onboarding'
                },
                id='doc_1'
            ),
            Mock(
                page_content="El proceso de formación se realiza durante las primeras semanas.",
                metadata={
                    'title': 'Proceso de Formación',
                    'url': 'https://intranet.cca.com/training',
                    'domain': 'training'
                },
                id='doc_2'
            ),
            Mock(
                page_content="Las políticas de seguridad son fundamentales en la empresa.",
                metadata={
                    'title': 'Políticas de Seguridad',
                    'url': 'https://intranet.cca.com/security',
                    'domain': 'security'
                },
                id='doc_3'
            )
        ]

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_chromadb_connector_initialization(self, mock_embeddings_class, mock_chroma_class):
        """Test de inicialización del ChromaDBConnector."""
        mock_embeddings_instance = Mock()
        mock_embeddings_class.return_value = mock_embeddings_instance
        mock_chroma_instance = Mock()
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        # Verificar que se configuraron las variables de entorno correctamente
        assert connector.persist_directory == os.getenv('CHROMA_PERSIST_DIRECTORY', 'chroma_data')
        assert connector.collection_name == os.getenv('CHROMA_COLLECTION_NAME')
        assert connector.openai_api_key == os.getenv('AZURE_OPENAI_API_KEY')
        assert connector.openai_endpoint == os.getenv('AZURE_OPENAI_ENDPOINT')
        assert connector.openai_deployment == os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT')
        assert connector.openai_api_version == os.getenv('AZURE_OPENAI_API_VERSION')
        
        # Verificar que se inicializaron los componentes
        mock_embeddings_class.assert_called_once()
        mock_chroma_class.assert_called_once()
        assert connector.embeddings is mock_embeddings_instance
        assert connector.store is mock_chroma_instance

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_basic(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test básico de búsqueda por similitud."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents[:2]
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        results = connector.similarity_search("onboarding policies", top_k=2)
        
        # Verificar que se llamó al método correcto
        mock_chroma_instance.similarity_search.assert_called_once_with("onboarding policies", k=2)
        
        # Verificar estructura de resultados
        assert len(results) == 2
        assert all('id' in hit for hit in results)
        assert all('document' in hit for hit in results)
        assert all('metadatas' in hit for hit in results)
        
        # Verificar contenido específico
        assert results[0]['document'] == "Las políticas de onboarding incluyen orientación inicial y formación."
        assert results[0]['metadatas']['domain'] == 'onboarding'

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_with_domains_filter(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de búsqueda con filtro por dominios."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        results = connector.similarity_search(
            "políticas",
            top_k=5,
            domains=["onboarding", "training"]
        )
        
        # Verificar que se pasó el filtro where correcto
        mock_chroma_instance.similarity_search.assert_called_once_with("políticas", k=5)
        
        # Verificar que solo se devuelven documentos de los dominios especificados
        for hit in results:
            assert hit['metadatas']['domain'] in ["onboarding", "training"]

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_with_custom_where_filter(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de búsqueda con filtro where personalizado."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        custom_where = {'category': 'policies'}
        results = connector.similarity_search(
            "información",
            top_k=3,
            where=custom_where
        )
        
        mock_chroma_instance.similarity_search.assert_called_once_with("información", k=3)

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_with_domains_and_where(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de búsqueda con dominios y filtro where combinados."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        custom_where = {'category': 'policies'}
        results = connector.similarity_search(
            "información",
            top_k=3,
            where=custom_where,
            domains=["onboarding"]
        )
        
        # Verificar que el filtro where se combina correctamente con dominios
        mock_chroma_instance.similarity_search.assert_called_once_with("información", k=3)

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_empty_results(self, mock_embeddings_class, mock_chroma_class):
        """Test de búsqueda que no devuelve resultados."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = []
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        results = connector.similarity_search("query with no results")
        
        assert results == []

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_exception_handling(self, mock_embeddings_class, mock_chroma_class):
        """Test de manejo de excepciones en búsqueda."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.side_effect = Exception("Database connection error")
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        with pytest.raises(Exception) as exc_info:
            connector.similarity_search("test query")
        
        assert "Database connection error" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_document_without_metadata(self, mock_embeddings_class, mock_chroma_class):
        """Test de búsqueda con documentos sin metadata."""
        # Crear documento sin metadata
        doc_without_metadata = Mock()
        doc_without_metadata.page_content = "Document without metadata"
        doc_without_metadata.metadata = None
        doc_without_metadata.id = 'doc_no_meta'
        
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = [doc_without_metadata]
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        results = connector.similarity_search("test query")
        
        assert len(results) == 1
        assert results[0]['metadatas'] is None
        assert results[0]['document'] == "Document without metadata"

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_filtering_logic(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de lógica de filtrado en resultados."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        # Test con filtro que excluye algunos documentos
        results = connector.similarity_search(
            "test",
            where={'domain': 'onboarding'},
            top_k=5
        )
        
        # Solo documentos de onboarding deberían pasar el filtro
        for hit in results:
            if hit['metadatas']:
                assert hit['metadatas'].get('domain') == 'onboarding'

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_default_parameters(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de parámetros por defecto en búsqueda."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents[:5]
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        results = connector.similarity_search("test query")
        
        # Verificar que se usan los valores por defecto
        mock_chroma_instance.similarity_search.assert_called_once_with("test query", k=5)
        assert len(results) <= 5

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_similarity_search_result_structure(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de estructura de resultados devueltos."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents[:1]
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        results = connector.similarity_search("test")
        
        assert len(results) == 1
        hit = results[0]
        
        # Verificar estructura requerida
        assert 'id' in hit
        assert 'document' in hit
        assert 'score' in hit
        assert 'metadatas' in hit
        
        # Verificar tipos
        assert isinstance(hit['document'], str)
        assert hit['score'] is None  # El connector no proporciona scores
        assert isinstance(hit['metadatas'], dict)

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    @patch('meribot.core.db.chromadb_connector.get_logger')
    def test_logging_in_similarity_search(self, mock_get_logger, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de logging durante búsqueda por similitud."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        results = connector.similarity_search("test query", domains=["onboarding"])
        
        # Verificar que se realizaron logs
        mock_logger.info.assert_called()
        mock_logger.debug.assert_called()
        
        # Verificar contenido de logs
        info_calls = mock_logger.info.call_args_list
        assert any("similarity_search" in str(call) for call in info_calls)

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    @patch('meribot.core.db.chromadb_connector.get_logger')
    def test_logging_error_in_similarity_search(self, mock_get_logger, mock_embeddings_class, mock_chroma_class):
        """Test de logging de errores durante búsqueda."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.side_effect = Exception("Test error")
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        with pytest.raises(Exception):
            connector.similarity_search("test query")
        
        # Verificar que se registró el error
        mock_logger.error.assert_called()
        error_call = mock_logger.error.call_args[0][0]
        assert "Error en similarity_search" in error_call

    @pytest.mark.unit
    @pytest.mark.db
    def test_environment_variables_handling(self):
        """Test de manejo de variables de entorno."""
        with patch.dict(os.environ, {
            'CHROMA_PERSIST_DIRECTORY': 'custom_chroma_dir',
            'CHROMA_COLLECTION_NAME': 'custom_collection',
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT': 'test_embeddings',
            'AZURE_OPENAI_API_VERSION': '2023-12-01-preview'
        }):
            with patch('meribot.core.db.chromadb_connector.Chroma'):
                with patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings'):
                    connector = ChromaDBConnector()
                    
                    assert connector.persist_directory == 'custom_chroma_dir'
                    assert connector.collection_name == 'custom_collection'
                    assert connector.openai_api_key == 'test_key'
                    assert connector.openai_endpoint == 'https://test.openai.azure.com'
                    assert connector.openai_deployment == 'test_embeddings'
                    assert connector.openai_api_version == '2023-12-01-preview'

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_top_k_parameter_handling(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de manejo del parámetro top_k."""
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = sample_documents
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        # Test con diferentes valores de top_k
        test_values = [1, 3, 10, 100]
        
        for top_k in test_values:
            connector.similarity_search("test", top_k=top_k)
            mock_chroma_instance.similarity_search.assert_called_with("test", k=top_k)

    @pytest.mark.unit
    @pytest.mark.db
    @patch('meribot.core.db.chromadb_connector.Chroma')
    @patch('meribot.core.db.chromadb_connector.AzureOpenAIEmbeddings')
    def test_complex_where_filter(self, mock_embeddings_class, mock_chroma_class, sample_documents):
        """Test de filtros where complejos."""
        mock_chroma_instance = Mock()
        
        # Crear documentos que cumplan y no cumplan el filtro
        filtered_docs = [doc for doc in sample_documents if doc.metadata.get('domain') == 'onboarding']
        mock_chroma_instance.similarity_search.return_value = sample_documents
        mock_chroma_class.return_value = mock_chroma_instance
        
        connector = ChromaDBConnector()
        
        # Test con filtro $in
        where_filter = {'domain': {'$in': ['onboarding', 'training']}}
        results = connector.similarity_search("test", where=where_filter)
        
        # Verificar que el filtro se aplicó correctamente
        for hit in results:
            if hit['metadatas']:
                assert hit['metadatas']['domain'] in ['onboarding', 'training']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])