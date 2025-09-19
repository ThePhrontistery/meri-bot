"""
conftest.py
Configuración central de pytest para los tests del módulo core de MeriBot.
Incluye fixtures compartidas, configuración de tests y utilidades de mocking.
"""

import os
import pytest
import tempfile
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Configurar variables de entorno para tests
os.environ.update({
    'MERIBOT_LOG_FILE': 'test_meribot.log',
    'CHROMA_PERSIST_DIRECTORY': 'meribot/core/test/test_chroma_data',
    'CHROMA_COLLECTION_NAME': 'test_collection',
    'AZURE_OPENAI_API_KEY': 'test_api_key',
    'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
    'AZURE_OPENAI_DEPLOYMENT_NAME': 'test_deployment',
    'AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT': 'test_embeddings',
    'AZURE_OPENAI_API_VERSION': '2023-12-01-preview',
    'LLM_MODEL': 'gpt-4',
    'TEMPERATURE': '0.7',
    'MAX_TOKENS': '512',
    'CRAWLER_CONFIG_PATH': 'test_crawler_config.yaml'
})

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_logger():
    """Mock logger para evitar logs durante tests."""
    logger_mock = Mock()
    logger_mock.info = Mock()
    logger_mock.warning = Mock()
    logger_mock.error = Mock()
    logger_mock.debug = Mock()
    return logger_mock

@pytest.fixture
def sample_conversation_id():
    """Fixture que proporciona un ID de conversación de prueba."""
    return "test_conversation_123"

@pytest.fixture
def sample_message():
    """Fixture que proporciona un mensaje de prueba."""
    return "¿Cuáles son las políticas de onboarding de la empresa?"

@pytest.fixture
def sample_domains():
    """Fixture que proporciona dominios de prueba."""
    return ["onboarding", "training"]

@pytest.fixture
def sample_conversation_history():
    """Fixture que proporciona un historial de conversación de prueba."""
    return [
        {
            "role": "user",
            "content": "Hola, necesito información sobre políticas",
            "timestamp": datetime.utcnow()
        },
        {
            "role": "assistant", 
            "content": "¡Hola! Te puedo ayudar con información sobre políticas de la empresa.",
            "timestamp": datetime.utcnow()
        }
    ]

@pytest.fixture
def sample_vector_search_results():
    """Fixture que proporciona resultados simulados de búsqueda vectorial."""
    return [
        {
            'id': 'doc_1',
            'document': 'Las políticas de onboarding incluyen...',
            'score': 0.95,
            'metadatas': {
                'title': 'Políticas de Onboarding',
                'url': 'https://intranet.cca.com/onboarding',
                'domain': 'onboarding'
            }
        },
        {
            'id': 'doc_2', 
            'document': 'El proceso de formación consta de...',
            'score': 0.87,
            'metadatas': {
                'title': 'Proceso de Formación',
                'url': 'https://intranet.cca.com/training',
                'domain': 'training'
            }
        }
    ]

@pytest.fixture
def sample_citations():
    """Fixture que proporciona citaciones de prueba."""
    return [
        {"title": "Políticas de Onboarding", "url": "https://intranet.cca.com/onboarding"},
        {"title": "Proceso de Formación", "url": "https://intranet.cca.com/training"}
    ]

@pytest.fixture
def mock_chromadb_connector():
    """Mock del ChromaDBConnector."""
    mock = Mock()
    mock.similarity_search = Mock(return_value=[])
    mock.persist_directory = "test_chroma_data"
    mock.collection_name = "test_collection"
    return mock

@pytest.fixture
def mock_llm_provider():
    """Mock del LLMProvider."""
    mock = Mock()
    mock.generate = AsyncMock(return_value="Esta es una respuesta de prueba del LLM.")
    mock.stream = AsyncMock()
    
    async def mock_stream_generator(prompt):
        tokens = ["Esta", "es", "una", "respuesta", "streaming"]
        for token in tokens:
            yield f"{token} "
    
    mock.stream.return_value = mock_stream_generator("test prompt")
    return mock

@pytest.fixture
def mock_llm_engine():
    """Mock del LLMEngine."""
    mock = Mock()
    mock.generate_response = AsyncMock(return_value="Respuesta del motor LLM.")
    mock.stream_response = AsyncMock()
    
    async def mock_stream_response(*args, **kwargs):
        tokens = ["Respuesta", "streaming", "del", "motor", "LLM"]
        for token in tokens:
            yield f"{token} "
    
    mock.stream_response.return_value = mock_stream_response()
    return mock

@pytest.fixture
def mock_conversation_manager():
    """Mock del ConversationManager."""
    from meribot.core.conversation.conversation_context import ConversationContext
    
    mock = Mock()
    mock.sessions = {}
    
    # Mock para get_or_create_session
    def mock_get_or_create_session(conversation_id):
        if conversation_id not in mock.sessions:
            context = ConversationContext(conversation_id=conversation_id)
            mock.sessions[conversation_id] = context
        return mock.sessions[conversation_id]
    
    mock.get_or_create_session = Mock(side_effect=mock_get_or_create_session)
    mock.close_session = Mock(return_value=True)
    return mock

@pytest.fixture
def mock_plugin_manager():
    """Mock del PluginManager."""
    mock = Mock()
    mock.run_pre_llm_plugins = AsyncMock(return_value=None)
    mock.run_post_llm_plugins = AsyncMock()
    mock.process_with_active_plugins = Mock(return_value={})
    mock._plugins = {}
    mock._active_plugins = set()
    return mock

@pytest.fixture
def mock_chat_engine_dependencies():
    """Fixture que proporciona todos los mocks necesarios para ChatEngine."""
    return {
        'plugin_manager': mock_plugin_manager(),
        'chromadb_connector': mock_chromadb_connector(),
        'llm_engine': mock_llm_engine(),
        'conversation_manager': mock_conversation_manager()
    }

@pytest.fixture
def temp_config_file():
    """Crea un archivo de configuración temporal para tests."""
    config_content = """
allowed_domains:
  - onboarding
  - training
  - cca
  - sdo

max_message_length: 4000
max_conversation_id_length: 100
max_domains_count: 5

dangerous_patterns:
  - "<script"
  - "javascript:"
  - "eval("
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        
        # Actualizar la variable de entorno para que apunte al archivo temporal
        old_path = os.environ.get('CRAWLER_CONFIG_PATH')
        os.environ['CRAWLER_CONFIG_PATH'] = f.name
        
        yield f.name
        
        # Restaurar la variable de entorno original
        if old_path:
            os.environ['CRAWLER_CONFIG_PATH'] = old_path
        else:
            os.environ.pop('CRAWLER_CONFIG_PATH', None)
            
        # Limpiar el archivo temporal
        try:
            os.unlink(f.name)
        except OSError:
            pass

@pytest.fixture
def mock_fastapi_dependencies():
    """Mock de dependencias de FastAPI para tests de API."""
    with patch('meribot.core.api.app.ChatEngine') as mock_chat_engine_class:
        mock_chat_engine = Mock()
        mock_chat_engine.process_message = AsyncMock(return_value={
            "type": "llm",
            "response": "Respuesta de prueba del chatbot",
            "citations": [],
            "source": "llm",
            "conversation_id": "test_123"
        })
        mock_chat_engine_class.return_value = mock_chat_engine
        yield mock_chat_engine

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configuración automática del entorno de test."""
    # Asegurar que estamos en modo test
    os.environ['TESTING'] = 'true'
    
    # Crear directorios temporales si no existen (dentro del directorio test)
    test_dirs = ['meribot/core/test/test_chroma_data', 'meribot/core/test/test_logs']
    for dir_name in test_dirs:
        os.makedirs(dir_name, exist_ok=True)
    
    yield
    
    # Limpiar después de los tests
    import shutil
    for dir_name in test_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
            except OSError:
                pass

class AsyncContextManager:
    """Helper para tests que necesitan context managers asíncronos."""
    def __init__(self, async_func):
        self.async_func = async_func

    async def __aenter__(self):
        return await self.async_func()

    async def __aenter__(self):
        pass

# Utilidades adicionales para tests
def assert_valid_response_format(response: Dict[str, Any]):
    """Valida que una respuesta tenga el formato esperado."""
    required_fields = ["response", "conversation_id", "intent", "confidence"]
    for field in required_fields:
        assert field in response, f"Campo requerido '{field}' no encontrado en la respuesta"
    
    assert isinstance(response["confidence"], (int, float)), "confidence debe ser numérico"
    assert 0.0 <= response["confidence"] <= 1.0, "confidence debe estar entre 0.0 y 1.0"

def create_mock_langchain_document(content: str, metadata: Dict[str, Any]):
    """Crea un mock de documento de LangChain para tests."""
    mock_doc = Mock()
    mock_doc.page_content = content
    mock_doc.metadata = metadata
    return mock_doc


# ==================== INTEGRATION TEST FIXTURES ====================

@pytest.fixture
def integration_config():
    """Configuración base para tests de integración."""
    return {
        'allowed_domains': ['onboarding', 'training', 'cca', 'sdo'],
        'max_message_length': 4000,
        'max_conversation_id_length': 100,
        'max_domains_count': 5,
        'dangerous_patterns': ['<script>', 'javascript:', 'eval('],
        'chroma_settings': {
            'persist_directory': './integration_test_chroma_data',
            'collection_name': 'meribot_integration_test'
        },
        'llm_settings': {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000
        }
    }

@pytest.fixture
def mock_crawler_service():
    """Mock del servicio de crawler para tests de integración."""
    mock_service = Mock()
    mock_service.start_crawling = AsyncMock(return_value={
        'status': 'started',
        'job_id': 'test_crawl_job',
        'estimated_time': '2 minutes'
    })
    mock_service.get_status = AsyncMock(return_value={
        'status': 'completed',
        'documents_processed': 10,
        'success': True
    })
    return mock_service

@pytest.fixture
def mock_web_client():
    """Mock cliente web para tests de integración."""
    from fastapi.testclient import TestClient
    from meribot.core.api.app import app
    return TestClient(app)

@pytest.fixture
def integration_test_documents():
    """Documentos de ejemplo para tests de integración."""
    return [
        {
            'id': 'integration_doc_1',
            'content': 'Procedimientos de onboarding para nuevos empleados de C&CA.',
            'metadata': {
                'title': 'Onboarding Procedures',
                'url': 'https://intranet.test.com/onboarding',
                'domain': 'onboarding',
                'source': 'integration_test'
            }
        },
        {
            'id': 'integration_doc_2',
            'content': 'Políticas de seguridad y cumplimiento normativo.',
            'metadata': {
                'title': 'Security Policies',
                'url': 'https://intranet.test.com/security',
                'domain': 'cca',
                'source': 'integration_test'
            }
        }
    ]

@pytest.fixture
def mock_services_integration():
    """Mock de todos los servicios para integración."""
    mock_services = Mock()
    
    # ChromaDB Integration Service
    mock_services.chroma_integration = Mock()
    mock_services.chroma_integration.query_chromadb = AsyncMock(return_value=[])
    mock_services.chroma_integration.upsert_chunks_to_chroma = AsyncMock(return_value={
        'success': True, 'chunks_processed': 5
    })
    
    # Crawler Service
    mock_services.crawler = Mock()
    mock_services.crawler.start_crawling = AsyncMock(return_value={'status': 'started'})
    mock_services.crawler.get_status = AsyncMock(return_value={'status': 'completed'})
    
    # Process Docs Service
    mock_services.process_docs = Mock()
    mock_services.process_docs.process_documents = AsyncMock(return_value={
        'status': 'success', 'documents_processed': 3
    })
    
    return mock_services

@pytest.fixture
def integration_chat_engine(integration_config):
    """ChatEngine configurado para tests de integración."""
    from meribot.core.chatengine import ChatEngine
    with patch('meribot.utils.utils.load_config_from_yaml') as mock_config:
        mock_config.side_effect = lambda key: integration_config.get(key)
        return ChatEngine()

# ==================== END INTEGRATION FIXTURES ====================