"""
Configuración de pytest para tests unitarios del core de MeriBot.
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fastapi.testclient import TestClient

# Añadir el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configura el entorno de testing con variables de entorno controladas."""
    test_env = {
        "MERIBOT_LOG_LEVEL": "DEBUG",
        "MERIBOT_LOG_FILE": "meribot/core/test/test_logs/test.log",
        "MERIBOT_LOG_MAX_BYTES": "1048576",
        "MERIBOT_LOG_BACKUP_COUNT": "3",
        "SYSTEM_PROMPT_PATH": "meribot/core/test/test_data/test_system_prompt.txt",
        "CRAWLER_CONFIG_PATH": "meribot/core/test/test_data/test_config.yaml",
        "AZURE_OPENAI_API_KEY": "test_key_123",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test-gpt-4",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "CHROMA_PERSIST_DIRECTORY": "meribot/core/test/test_chroma_data",
        "CHROMA_COLLECTION_NAME": "test_collection",
        "HOST": "127.0.0.1",
        "PORT": "8001",
        "ENV": "testing"
    }
    
    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture
def temp_directory():
    """Fixture que proporciona un directorio temporal para tests."""
    import tempfile
    import shutil
    import atexit
    import logging
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    
    # Función de limpieza que se ejecutará al final
    def cleanup():
        try:
            # Cerrar todos los handlers de logging que puedan estar usando archivos
            for handler in logging.root.handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
                    logging.root.removeHandler(handler)
            
            # Forzar limpieza de archivos temporales
            if os.path.exists(temp_dir):
                # En Windows, usar rmtree con ignore_errors
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            # Si falla la limpieza, no interrumpir los tests
            pass
    
    # Registrar limpieza para cuando termine el proceso
    atexit.register(cleanup)
    
    yield temp_dir
    
    # Limpieza inmediata
    cleanup()


@pytest.fixture
def mock_logger():
    """Fixture que proporciona un logger mock para tests."""
    mock_logger = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    mock_logger.critical = MagicMock()
    mock_logger.debug = MagicMock()
    return mock_logger


@pytest.fixture
def sample_config_yaml():
    """Fixture que proporciona contenido YAML de configuración para tests."""
    return """
allowed_domains:
  - "onboarding"
  - "training"
  - "cca"
  - "sdo"
max_message_length: 4000
max_conversation_id_length: 100
max_domains_count: 5
dangerous_patterns:
  - "delete"
  - "drop table"
  - "rm -rf"
  - "<script>"
sensitive_keys:
  - "password"
  - "api_key"
  - "secret"
  - "token"
"""


@pytest.fixture
def sample_system_prompt():
    """Fixture que proporciona un system prompt de ejemplo para tests."""
    return """Eres MeriBot, un asistente conversacional para C&CA.
Tu función es ayudar a empleados con información sobre:
- Políticas de la empresa
- Procedimientos de RR.HH.
- Documentación técnica
- Preguntas frecuentes

Mantén un tono profesional y amigable.
Si no tienes información suficiente, indícalo claramente."""


@pytest.fixture
def create_test_files(temp_directory, sample_config_yaml, sample_system_prompt):
    """Fixture que crea archivos de test en directorio temporal."""
    config_path = os.path.join(temp_directory, "test_config.yaml")
    prompt_path = os.path.join(temp_directory, "test_system_prompt.txt")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(sample_config_yaml)
    
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(sample_system_prompt)
    
    return {
        "config_path": config_path,
        "prompt_path": prompt_path,
        "temp_dir": temp_directory
    }


@pytest.fixture
def mock_environ_config(create_test_files):
    """Fixture que mockea variables de entorno con archivos de test."""
    test_env = {
        "CRAWLER_CONFIG_PATH": create_test_files["config_path"],
        "SYSTEM_PROMPT_PATH": create_test_files["prompt_path"]
    }
    
    with patch.dict(os.environ, test_env):
        yield create_test_files


@pytest.fixture
def client():
    """Fixture que proporciona un TestClient de FastAPI para tests de API."""
    from meribot.core.api.app import app
    
    # Mock las dependencias que podrían causar problemas
    with patch('meribot.core.api.app.chat_engine') as mock_chat_engine:
        mock_chat_engine.process_message.return_value = {
            "response": "Respuesta de test",
            "conversation_id": "test-123",
            "type": "llm",
            "citations": []
        }
        
        with patch('meribot.core.api.app.load_config_from_yaml') as mock_load_config:
            mock_load_config.return_value = ["test.domain.com", "example.com"]
            
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def sample_request_data():
    """Fixture que proporciona datos de request de ejemplo."""
    return {
        "question": "¿Cuáles son las políticas de la empresa?",
        "conversation_id": "test-conversation-123",
        "domains": ["onboarding", "training"]
    }


# ======================= FIXTURES ADICIONALES PARA MOCKS =======================

@pytest.fixture
def sample_message():
    """Fixture que proporciona un mensaje de ejemplo."""
    return "¿Cuáles son las políticas de vacaciones?"


@pytest.fixture
def sample_conversation_id():
    """Fixture que proporciona un ID de conversación de ejemplo."""
    return "test-conv-123"


@pytest.fixture
def sample_domains():
    """Fixture que proporciona dominios de ejemplo."""
    return ["onboarding", "policies", "hr"]


@pytest.fixture
def sample_citations():
    """Fixture que proporciona citaciones de ejemplo."""
    return [
        {"text": "Política de vacaciones...", "source": "manual_empleado.pdf", "url": "https://test.com/doc1"},
        {"text": "Procedimiento de solicitud...", "source": "hr_guide.pdf", "url": "https://test.com/doc2"}
    ]


@pytest.fixture
def sample_conversation_history():
    """Fixture que proporciona historial de conversación de ejemplo."""
    return [
        {"role": "user", "content": "¿Qué es C&CA?"},
        {"role": "assistant", "content": "C&CA es una empresa de consultoría..."}
    ]


@pytest.fixture
def sample_vector_search_results():
    """Fixture que proporciona resultados de búsqueda vectorial de ejemplo."""
    return [
        {"content": "Contenido relevante 1", "metadata": {"source": "doc1.pdf"}},
        {"content": "Contenido relevante 2", "metadata": {"source": "doc2.pdf"}}
    ]


@pytest.fixture
def temp_config_file(temp_directory):
    """Fixture que crea un archivo de configuración temporal."""
    config_content = """
allowed_domains:
  - "test.domain.com"
  - "example.com"
max_message_length: 4000
"""
    config_path = os.path.join(temp_directory, "test_config.yaml")
    with open(config_path, 'w') as f:
        f.write(config_content)
    return config_path


# ======================= FIXTURES DE MOCKS PARA COMPONENTES =======================

@pytest.fixture
def mock_chat_engine_dependencies():
    """Mock para las dependencias del ChatEngine."""
    with patch('meribot.core.chatengine.ChromaDBConnector') as mock_chroma, \
         patch('meribot.core.chatengine.ConversationManager') as mock_conv, \
         patch('meribot.core.chatengine.LLMEngine') as mock_llm:
        
        # Configurar mocks
        mock_chroma.return_value.similarity_search.return_value = []
        mock_conv.return_value.get_history.return_value = []
        mock_llm.return_value.generate_response.return_value = "Respuesta generada"
        
        yield {
            'chroma': mock_chroma,
            'conversation': mock_conv,
            'llm': mock_llm
        }


@pytest.fixture
def mock_fastapi_dependencies():
    """Mock para las dependencias de FastAPI."""
    mocks = {}
    
    with patch('meribot.core.api.app.ChatEngine') as mock_chat_engine, \
         patch('meribot.core.api.app.load_config_from_yaml') as mock_load_config:
        
        # Configurar ChatEngine mock
        mock_instance = MagicMock()
        mock_instance.process_message.return_value = {
            "response": "Test response",
            "conversation_id": "test-123",
            "type": "llm",
            "citations": []
        }
        mock_chat_engine.return_value = mock_instance
        
        # Configurar load_config mock
        mock_load_config.return_value = ["test.domain.com", "example.com"]
        
        mocks['chat_engine'] = mock_chat_engine
        mocks['load_config'] = mock_load_config
        
        yield mocks