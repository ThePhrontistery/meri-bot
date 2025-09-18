"""
Configuración de fixtures y utilidades compartidas para tests unitarios del crawler.
Proporciona configuraciones mock, datos de prueba y utilidades comunes.
"""

import pytest
import os
import tempfile
import yaml
import json
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List
from pathlib import Path


# ==================== FIXTURES DE CONFIGURACIÓN ====================

@pytest.fixture
def valid_crawler_config():
    """Fixture con configuración válida básica del crawler."""
    return {
        "seeds": ["https://example.com", "https://test.com"],
        "allowed_domains": ["example.com", "test.com", "subdomain.example.com"],
        "user_agent": "MeriBot-Crawler/1.0 (Test Suite)",
        "delay": 1.0,
        "output_dir": "./test_data/scraped",
        "log_level": "INFO",
        "chroma_path": "./test_data/chroma",
        "embedding_model": "text-embedding-ada-002",
        "max_depth": 3,
        "file_types": ["html", "pdf", "docx", "xlsx"]
    }


@pytest.fixture
def minimal_crawler_config():
    """Fixture con configuración mínima válida del crawler."""
    return {
        "seeds": ["https://example.com"],
        "allowed_domains": ["example.com"],
        "user_agent": "TestBot/1.0",
        "delay": 1.0,
        "output_dir": "./data",
        "log_level": "INFO",
        "chroma_path": "./chroma",
        "embedding_model": "text-embedding-ada-002"
    }


@pytest.fixture
def invalid_crawler_config():
    """Fixture con configuración inválida para tests de validación."""
    return {
        "seeds": "not_a_list",  # Debería ser lista
        "allowed_domains": ["example.com"],
        "user_agent": 123,  # Debería ser string
        "delay": "not_a_number",  # Debería ser float
        # Faltan campos requeridos
    }


@pytest.fixture
def temp_config_file(valid_crawler_config):
    """Fixture que crea un archivo YAML temporal con configuración válida."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(valid_crawler_config, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_invalid_config_file():
    """Fixture que crea un archivo YAML inválido."""
    invalid_yaml = """
    seeds:
      - https://example.com
    invalid_yaml: [unclosed_bracket
    user_agent: "TestBot/1.0
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(invalid_yaml)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# ==================== FIXTURES DE DIRECTORIO Y ARCHIVOS ====================

@pytest.fixture
def temp_output_dir():
    """Fixture que crea un directorio temporal para output del crawler."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def temp_log_dir():
    """Fixture que crea un directorio temporal para logs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        yield log_dir


@pytest.fixture
def sample_html_file():
    """Fixture que crea un archivo HTML temporal de ejemplo."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
        <meta charset="utf-8">
    </head>
    <body>
        <main>
            <h1>Main Title</h1>
            <p>This is a test document with multiple paragraphs.</p>
            <p>It contains sample content for testing document parsing.</p>
            <section>
                <h2>Section Title</h2>
                <p>Section content with more detailed information.</p>
            </section>
        </main>
    </body>
    </html>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_text_file():
    """Fixture que crea un archivo de texto temporal de ejemplo."""
    text_content = """
    This is a sample text document for testing purposes.
    
    It contains multiple paragraphs with different types of content.
    Some paragraphs are longer and contain more detailed information
    that can be used to test text processing and chunking functionality.
    
    The document also includes special characters: ñáéíóú, and symbols: @#$%
    
    This allows testing of text normalization and encoding handling.
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# ==================== FIXTURES DE MOCKS Y DATOS DE PRUEBA ====================

@pytest.fixture
def mock_logger():
    """Fixture que proporciona un logger mock."""
    logger = MagicMock()
    logger.name = "test_logger"
    logger.level = 20  # INFO level
    return logger


@pytest.fixture
def mock_requests_response():
    """Fixture que proporciona un response mock para requests."""
    response = MagicMock()
    response.status_code = 200
    response.headers = {"Content-Type": "text/html; charset=utf-8"}
    response.text = """
    <html>
    <body>
        <main>
            <h1>Test Page</h1>
            <p>Test content</p>
            <a href="page2.html">Link to page 2</a>
            <a href="document.pdf">PDF Document</a>
        </main>
    </body>
    </html>
    """
    response.content = b"binary content for file downloads"
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def sample_document_metadata():
    """Fixture con metadata de ejemplo para documentos."""
    return {
        "title": "Test Document",
        "author": "Test Author",
        "date": "2023-01-01",
        "version": "1.0",
        "type": "html",
        "url": "https://example.com/test-document.html",
        "domain": "example.com"
    }


@pytest.fixture
def sample_chunks():
    """Fixture con chunks de texto de ejemplo."""
    return [
        "This is the first chunk of text content that contains important information about the topic.",
        "This is the second chunk with different content that continues the discussion from the previous chunk.",
        "The third chunk provides additional details and examples to support the main points discussed earlier.",
        "Finally, this fourth chunk summarizes the key concepts and provides conclusions for the document."
    ]


@pytest.fixture
def sample_chunks_metadata():
    """Fixture con metadata para chunks de ejemplo."""
    return [
        {"id": "doc1_chunk_0", "source": "document1.pdf", "chunk_idx": 0, "page": 1},
        {"id": "doc1_chunk_1", "source": "document1.pdf", "chunk_idx": 1, "page": 1},
        {"id": "doc1_chunk_2", "source": "document1.pdf", "chunk_idx": 2, "page": 2},
        {"id": "doc1_chunk_3", "source": "document1.pdf", "chunk_idx": 3, "page": 2}
    ]


@pytest.fixture
def mock_embeddings():
    """Fixture que proporciona embeddings mock."""
    import numpy as np
    
    # Generar embeddings mock de 1536 dimensiones (tamaño típico de OpenAI)
    embeddings = []
    for i in range(4):
        # Crear embeddings con valores diferentes pero consistentes
        embedding = np.random.rand(1536).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)  # Normalizar
        embeddings.append(embedding.tolist())
    
    return embeddings


@pytest.fixture
def mock_azure_openai_response():
    """Fixture con response mock para Azure OpenAI API."""
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 307 + [0.1, 0.2]  # 1536 dims
            },
            {
                "object": "embedding", 
                "index": 1,
                "embedding": [0.2, 0.3, 0.4, 0.5, 0.6] * 307 + [0.2, 0.3]  # 1536 dims
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 10,
            "total_tokens": 10
        }
    }


# ==================== FIXTURES DE BASE DE DATOS Y SERVICIOS ====================

@pytest.fixture
def mock_chroma_collection():
    """Fixture que proporciona una colección ChromaDB mock."""
    collection = MagicMock()
    collection.name = "test_collection"
    collection.count.return_value = 100
    collection.get.return_value = {
        "ids": ["doc1", "doc2", "doc3"],
        "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
        "metadatas": [
            {"source": "doc1.pdf", "page": 1},
            {"source": "doc2.pdf", "page": 1}, 
            {"source": "doc3.pdf", "page": 2}
        ],
        "documents": ["Document 1 content", "Document 2 content", "Document 3 content"]
    }
    return collection


@pytest.fixture
def mock_chroma_db(mock_chroma_collection):
    """Fixture que proporciona una base de datos ChromaDB mock."""
    db = MagicMock()
    db._collection = mock_chroma_collection
    
    # Mock similarity search
    from langchain.schema import Document
    db.similarity_search_with_score.return_value = [
        (Document(page_content="Similar document 1", metadata={"id": "doc1"}), 0.85),
        (Document(page_content="Similar document 2", metadata={"id": "doc2"}), 0.90)
    ]
    
    return db


@pytest.fixture
def mock_hash_db():
    """Fixture que proporciona una base de datos de hashes mock."""
    return {
        "doc1_chunk_0": "hash1234567890abcdef",
        "doc1_chunk_1": "hash2345678901bcdefg", 
        "doc2_chunk_0": "hash3456789012cdefgh",
        "existing_doc": "existing_hash_value"
    }


# ==================== FIXTURES DE VARIABLES DE ENTORNO ====================

@pytest.fixture
def mock_env_variables():
    """Fixture que configura variables de entorno mock para tests."""
    env_vars = {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "test_api_key_12345",
        "AZURE_OPENAI_API_VERSION": "2023-05-15",
        "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT": "test-embeddings-deployment",
        "CRAWLER_LOG_LEVEL": "DEBUG",
        "CRAWLER_LOG_FORMAT": "STANDARD",
        "TESTING": "true"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture  
def mock_env_azure_missing():
    """Fixture que simula variables de entorno de Azure faltantes."""
    # Limpiar variables de Azure
    env_vars_to_clear = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"
    ]
    
    with patch.dict(os.environ, {}, clear=False):
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
        yield


# ==================== FIXTURES DE URL Y WEB SCRAPING ====================

@pytest.fixture
def sample_urls():
    """Fixture con URLs de ejemplo para tests de scraping."""
    return {
        "valid_html": "https://example.com/page.html",
        "valid_pdf": "https://example.com/document.pdf", 
        "valid_docx": "https://example.com/report.docx",
        "invalid_domain": "https://notallowed.com/page.html",
        "relative_url": "/relative/page.html",
        "with_params": "https://example.com/page.html?param=value&other=123",
        "with_fragment": "https://example.com/page.html#section1"
    }


@pytest.fixture
def sample_html_with_links():
    """Fixture con HTML que contiene varios tipos de enlaces."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Links Test Page</title></head>
    <body>
        <h1>Test Page with Links</h1>
        <nav>
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="/contact">Contact</a>
        </nav>
        <main>
            <section>
                <h2>Documents</h2>
                <ul>
                    <li><a href="manual.pdf">User Manual (PDF)</a></li>
                    <li><a href="report.docx">Annual Report (Word)</a></li>
                    <li><a href="data.xlsx">Data Sheet (Excel)</a></li>
                    <li><a href="presentation.pptx">Presentation (PowerPoint - unsupported)</a></li>
                </ul>
            </section>
            <section>
                <h2>External Links</h2>
                <a href="https://external.com/page.html">External Site</a>
                <a href="mailto:test@example.com">Email Link</a>
            </section>
            <section>
                <h2>Special Cases</h2>
                <a href="page.html?param=value&other=123">Link with parameters</a>
                <a href="document.pdf#page=5">PDF with fragment</a>
                <a name="anchor">Anchor without href</a>
                <a>Link without href attribute</a>
            </section>
        </main>
    </body>
    </html>
    """


# ==================== FIXTURES DE UTILIDADES Y HELPERS ====================

@pytest.fixture
def capture_logs():
    """Fixture para capturar logs durante tests."""
    import logging
    from io import StringIO
    
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    
    # Formatear logs para tests
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    
    # Configurar logger root para capturar todos los logs
    root_logger = logging.getLogger()
    original_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)
    
    yield log_stream
    
    # Cleanup
    root_logger.removeHandler(handler)
    root_logger.setLevel(original_level)


@pytest.fixture
def clean_test_environment():
    """Fixture que limpia el entorno entre tests."""
    # Setup
    original_cwd = os.getcwd()
    
    yield
    
    # Cleanup
    os.chdir(original_cwd)
    
    # Limpiar loggers de test
    import logging
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        if logger_name.startswith(("test", "crawler")):
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)


# ==================== FUNCIONES HELPER PARA TESTS ====================

def create_test_file(content: str, suffix: str = ".txt", directory: str = None) -> str:
    """
    Helper para crear archivos temporales de test.
    
    Args:
        content: Contenido del archivo
        suffix: Extensión del archivo
        directory: Directorio donde crear el archivo (opcional)
        
    Returns:
        str: Path del archivo creado
    """
    kwargs = {"mode": "w", "suffix": suffix, "delete": False, "encoding": "utf-8"}
    if directory:
        kwargs["dir"] = directory
        
    with tempfile.NamedTemporaryFile(**kwargs) as f:
        f.write(content)
        return f.name


def mock_file_operations():
    """Helper para mockear operaciones de archivo comunes."""
    return {
        "open": patch("builtins.open"),
        "exists": patch("os.path.exists"),
        "makedirs": patch("os.makedirs"),
        "listdir": patch("os.listdir"),
        "unlink": patch("os.unlink")
    }


def assert_valid_config(config: Dict[str, Any]) -> None:
    """
    Helper para validar que una configuración tiene los campos requeridos.
    
    Args:
        config: Configuración a validar
    """
    required_fields = [
        "seeds", "allowed_domains", "user_agent", "delay", 
        "output_dir", "log_level", "chroma_path", "embedding_model"
    ]
    
    for field in required_fields:
        assert field in config, f"Missing required field: {field}"
    
    # Validar tipos básicos
    assert isinstance(config["seeds"], list), "seeds must be a list"
    assert isinstance(config["allowed_domains"], list), "allowed_domains must be a list"
    assert isinstance(config["user_agent"], str), "user_agent must be a string"
    assert isinstance(config["delay"], (int, float)), "delay must be a number"


def assert_valid_document_result(result: Dict[str, Any]) -> None:
    """
    Helper para validar resultado de parsing de documento.
    
    Args:
        result: Resultado del parsing a validar
    """
    if "error" not in result:
        assert "text" in result, "Missing 'text' field in successful parse result"
        assert "metadata" in result, "Missing 'metadata' field in successful parse result"
        assert isinstance(result["metadata"], dict), "metadata must be a dict"
    else:
        assert "text" in result, "Missing 'text' field in error result"
        assert "metadata" in result, "Missing 'metadata' field in error result"


# ==================== MARCADORES DE PYTEST ====================

# Estas funciones ayudan a aplicar marcadores automáticamente
def pytest_configure(config):
    """Configuración automática de pytest."""
    # Registrar marcadores personalizados si no están en pytest.ini
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")


def pytest_collection_modifyitems(config, items):
    """Modificar items de test automáticamente."""
    for item in items:
        # Agregar marcador 'unit' a todos los tests en test/unitarios
        if "test/unitarios" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            
        # Agregar marcadores específicos basados en nombre de archivo
        if "test_config" in str(item.fspath):
            item.add_marker(pytest.mark.config)
        elif "test_document_loader" in str(item.fspath):
            item.add_marker(pytest.mark.document)
        elif "test_scraper" in str(item.fspath):
            item.add_marker(pytest.mark.scraper)
        elif "test_logger" in str(item.fspath):
            item.add_marker(pytest.mark.logger)
        elif "test_utilities" in str(item.fspath):
            item.add_marker(pytest.mark.utilities)
            
        # Agregar marcador 'network' a tests que usan requests o APIs
        if any(keyword in item.name.lower() for keyword in ["request", "api", "network", "download"]):
            item.add_marker(pytest.mark.network)
            
        # Agregar marcador 'azure' a tests de Azure
        if "azure" in item.name.lower():
            item.add_marker(pytest.mark.azure)
            
        # Agregar marcador 'chroma' a tests de ChromaDB
        if "chroma" in item.name.lower():
            item.add_marker(pytest.mark.chroma)