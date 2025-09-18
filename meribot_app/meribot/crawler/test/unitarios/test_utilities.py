"""
Tests unitarios para las utilidades del crawler.
Valida check_embeddings.py y chroma_explorer.py.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, call
from argparse import Namespace

# Tests para check_embeddings.py
class TestSemanticSearchCLI:
    """Tests para la clase SemanticSearchCLI de check_embeddings.py."""
    
    def test_create_parser(self):
        """Test creación del parser de argumentos."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        parser = cli._create_parser()
        
        # Verificar argumentos requeridos
        assert parser
        
        # Test parsing con argumentos mínimos
        args = parser.parse_args(['--persist', '/test/path'])
        assert args.persist == '/test/path'
        assert args.collection == 'default'
        assert args.k == 5
        assert args.q is None
    
    def test_create_parser_all_args(self):
        """Test parser con todos los argumentos."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        parser = cli._create_parser()
        
        args = parser.parse_args([
            '--persist', '/test/path',
            '--collection', 'test_collection',
            '--k', '10',
            '--q', 'test query',
            '--azure-deployment', 'test-deployment'
        ])
        
        assert args.persist == '/test/path'
        assert args.collection == 'test_collection'
        assert args.k == 10
        assert args.q == 'test query'
        assert args.azure_deployment == 'test-deployment'
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15',
        'AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT': 'test-deployment'
    })
    @patch('os.path.exists')
    def test_validate_environment_success(self, mock_exists):
        """Test validación exitosa del entorno."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        mock_exists.return_value = True
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(
            persist='/test/path',
            azure_deployment='test-deployment'
        )
        
        result = cli._validate_environment()
        assert result is True
    
    def test_validate_environment_missing_vars(self):
        """Test validación con variables de entorno faltantes."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        with patch.dict(os.environ, {}, clear=True):
            cli = SemanticSearchCLI()
            cli.args = Namespace(
                persist='/test/path',
                azure_deployment='test-deployment'
            )
            
            result = cli._validate_environment()
            assert result is False
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15'
    })
    @patch('os.path.exists')
    def test_validate_environment_missing_deployment(self, mock_exists):
        """Test validación sin deployment especificado."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        mock_exists.return_value = True
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(
            persist='/test/path',
            azure_deployment=None
        )
        
        result = cli._validate_environment()
        assert result is False
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15'
    })
    @patch('os.path.exists')
    def test_validate_environment_missing_persist_dir(self, mock_exists):
        """Test validación con directorio de persistencia faltante."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        mock_exists.return_value = False
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(
            persist='/nonexistent/path',
            azure_deployment='test-deployment'
        )
        
        result = cli._validate_environment()
        assert result is False
    
    @patch('meribot.crawler.check_embeddings.AzureOpenAIEmbeddings')
    def test_initialize_embeddings_success(self, mock_embeddings):
        """Test inicialización exitosa de embeddings."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(azure_deployment='test-deployment')
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_VERSION': '2023-05-15'
        }):
            result = cli._initialize_embeddings()
        
        assert result is True
        assert cli.embeddings == mock_embeddings_instance
        
        mock_embeddings.assert_called_once_with(
            azure_deployment='test-deployment',
            openai_api_type='azure',
            openai_api_key='test-key',
            azure_endpoint='https://test.openai.azure.com',
            openai_api_version='2023-05-15'
        )
    
    @patch('meribot.crawler.check_embeddings.AzureOpenAIEmbeddings')
    def test_initialize_embeddings_failure(self, mock_embeddings):
        """Test fallo en inicialización de embeddings."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        mock_embeddings.side_effect = Exception("API Error")
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(azure_deployment='test-deployment')
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_VERSION': '2023-05-15'
        }):
            result = cli._initialize_embeddings()
        
        assert result is False
    
    @patch('meribot.crawler.check_embeddings.Chroma')
    def test_initialize_vectorstore_success(self, mock_chroma):
        """Test inicialización exitosa del vector store."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        mock_vectorstore = MagicMock()
        mock_chroma.return_value = mock_vectorstore
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(persist='/test/path', collection='test_collection')
        cli.embeddings = MagicMock()
        
        result = cli._initialize_vectorstore()
        
        assert result is True
        assert cli.vectorstore == mock_vectorstore
        
        mock_chroma.assert_called_once_with(
            persist_directory='/test/path',
            collection_name='test_collection',
            embedding_function=cli.embeddings
        )
    
    @patch('meribot.crawler.check_embeddings.Chroma')
    def test_initialize_vectorstore_failure(self, mock_chroma):
        """Test fallo en inicialización del vector store."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        mock_chroma.side_effect = Exception("Chroma Error")
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(persist='/test/path', collection='test_collection')
        cli.embeddings = MagicMock()
        
        result = cli._initialize_vectorstore()
        
        assert result is False
    
    def test_format_result(self):
        """Test formateo de resultados de búsqueda."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        from langchain.schema import Document
        
        cli = SemanticSearchCLI()
        
        # Test con texto corto
        doc = Document(
            page_content="Short text content",
            metadata={"id": "doc1", "source": "test.pdf"}
        )
        
        result = cli._format_result(doc, 0.85, 1)
        
        assert "[1]" in result
        assert "dist=0.8500" in result
        assert "id=doc1" in result
        assert "Short text content" in result
    
    def test_format_result_long_text(self):
        """Test formateo con texto largo que necesita truncamiento."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        from langchain.schema import Document
        
        cli = SemanticSearchCLI()
        
        long_text = "This is a very long text content that exceeds the 140 character limit and should be truncated with ellipsis at the end."
        doc = Document(
            page_content=long_text,
            metadata={"source": "long_doc.pdf"}
        )
        
        result = cli._format_result(doc, 0.75, 2)
        
        assert "[2]" in result
        assert "dist=0.7500" in result
        assert "..." in result
        assert len(result.split("texto: ")[1]) <= 143  # 140 + "..."
    
    def test_format_result_no_id(self):
        """Test formateo sin ID en metadata."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        from langchain.schema import Document
        
        cli = SemanticSearchCLI()
        
        doc = Document(
            page_content="Content without ID",
            metadata={}
        )
        
        result = cli._format_result(doc, 0.90, 1)
        
        assert "id=(sin id)" in result
    
    def test_search_success(self):
        """Test búsqueda exitosa."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        from langchain.schema import Document
        
        cli = SemanticSearchCLI()
        
        # Mock vectorstore
        mock_vectorstore = MagicMock()
        mock_results = [
            (Document(page_content="Result 1", metadata={"id": "1"}), 0.85),
            (Document(page_content="Result 2", metadata={"id": "2"}), 0.90)
        ]
        mock_vectorstore.similarity_search_with_score.return_value = mock_results
        cli.vectorstore = mock_vectorstore
        
        results = cli.search("test query", k=2)
        
        assert len(results) == 2
        assert results == mock_results
        
        mock_vectorstore.similarity_search_with_score.assert_called_once_with("test query", k=2)
    
    def test_search_empty_query(self):
        """Test búsqueda con query vacía."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        cli.vectorstore = MagicMock()
        
        results = cli.search("   ", k=5)
        
        assert results == []
        cli.vectorstore.similarity_search_with_score.assert_not_called()
    
    def test_search_exception(self):
        """Test manejo de excepción en búsqueda."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        
        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search_with_score.side_effect = Exception("Search error")
        cli.vectorstore = mock_vectorstore
        
        results = cli.search("test query", k=5)
        
        assert results == []
    
    @patch('builtins.print')
    def test_print_results_with_results(self, mock_print):
        """Test impresión de resultados exitosos."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        from langchain.schema import Document
        
        cli = SemanticSearchCLI()
        
        results = [
            (Document(page_content="Result 1", metadata={"id": "1"}), 0.85),
            (Document(page_content="Result 2", metadata={"id": "2"}), 0.90)
        ]
        
        cli.print_results(results)
        
        # Verificar que se imprimió cada resultado
        assert mock_print.call_count == 2
    
    @patch('builtins.print')
    def test_print_results_empty(self, mock_print):
        """Test impresión sin resultados."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        cli.print_results([])
        
        mock_print.assert_called_once_with("Sin resultados.")
    
    @patch('builtins.input', side_effect=['test query', 'salir'])
    @patch.object(sys.stdout, 'write')
    def test_run_repl_exit(self, mock_write, mock_input):
        """Test REPL con comando de salida."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(k=5)
        cli.search = MagicMock(return_value=[])
        cli.print_results = MagicMock()
        
        with patch('builtins.print'):
            cli.run_repl()
        
        # Verificar que se ejecutó búsqueda antes de salir
        cli.search.assert_called_with('test query', 5)
    
    @patch('builtins.input', side_effect=['', 'exit'])
    @patch.object(sys.stdout, 'write')
    def test_run_repl_empty_query(self, mock_write, mock_input):
        """Test REPL con query vacía."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        cli.args = Namespace(k=5)
        cli.search = MagicMock()
        
        with patch('builtins.print'):
            cli.run_repl()
        
        # No debería ejecutar búsqueda para query vacía
        cli.search.assert_not_called()
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch.object(sys.stdout, 'write')
    def test_run_repl_keyboard_interrupt(self, mock_write, mock_input):
        """Test REPL con interrupción de teclado."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        
        with patch('builtins.print'):
            cli.run_repl()
        
        # Debería salir gracefully


# Tests para chroma_explorer.py
class TestChromaExplorer:
    """Tests para las funciones de chroma_explorer.py."""
    
    @patch('os.system')
    def test_clear_screen_windows(self, mock_system):
        """Test clear_screen en Windows."""
        from meribot.crawler.chroma_explorer import clear_screen
        
        with patch('os.name', 'nt'):
            clear_screen()
            mock_system.assert_called_once_with('cls')
    
    @patch('os.system')
    def test_clear_screen_unix(self, mock_system):
        """Test clear_screen en sistemas Unix."""
        from meribot.crawler.chroma_explorer import clear_screen
        
        with patch('os.name', 'posix'):
            clear_screen()
            mock_system.assert_called_once_with('clear')
    
    @patch('rich.console.Console.print')
    def test_display_header(self, mock_print):
        """Test display_header."""
        from meribot.crawler.chroma_explorer import display_header
        
        display_header("Test Title")
        
        mock_print.assert_called_once()
        # Verificar que se pasó un Panel
        call_args = mock_print.call_args[0][0]
        assert hasattr(call_args, 'title') or 'Test Title' in str(call_args)
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT': 'test-deployment',
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
        'AZURE_OPENAI_API_VERSION': '2023-05-15'
    })
    @patch('meribot.crawler.chroma_explorer.AzureOpenAIEmbeddings')
    @patch('meribot.crawler.chroma_explorer.Chroma')
    def test_initialize_chroma_success(self, mock_chroma, mock_embeddings):
        """Test inicialización exitosa de Chroma."""
        from meribot.crawler.chroma_explorer import initialize_chroma
        
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_db = MagicMock()
        mock_chroma.return_value = mock_db
        
        result = initialize_chroma('/test/persist', 'test_collection')
        
        assert result == mock_db
        
        mock_embeddings.assert_called_once_with(
            azure_deployment='test-deployment',
            openai_api_key='test-key',
            azure_endpoint='https://test.openai.azure.com',
            openai_api_version='2023-05-15'
        )
        
        mock_chroma.assert_called_once_with(
            persist_directory='/test/persist',
            collection_name='test_collection',
            embedding_function=mock_embeddings_instance
        )
    
    def test_initialize_chroma_missing_env_vars(self):
        """Test inicialización con variables de entorno faltantes."""
        from meribot.crawler.chroma_explorer import initialize_chroma
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('rich.console.Console.print'):
                result = initialize_chroma('/test/persist', 'test_collection')
        
        assert result is None
    
    @patch('meribot.crawler.chroma_explorer.AzureOpenAIEmbeddings')
    def test_initialize_chroma_exception(self, mock_embeddings):
        """Test manejo de excepción en inicialización."""
        from meribot.crawler.chroma_explorer import initialize_chroma
        
        mock_embeddings.side_effect = Exception("Init error")
        
        with patch.dict(os.environ, {
            'AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT': 'test-deployment',
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_VERSION': '2023-05-15'
        }):
            with patch('rich.console.Console.print'):
                result = initialize_chroma('/test/persist', 'test_collection')
        
        assert result is None
    
    @patch('rich.console.Console.print')
    def test_show_collection_info_empty(self, mock_print):
        """Test show_collection_info con colección vacía."""
        from meribot.crawler.chroma_explorer import show_collection_info
        
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_db._collection = mock_collection
        
        show_collection_info(mock_db)
        
        mock_print.assert_called()
        # Verificar que se muestra mensaje de colección vacía
        call_args = str(mock_print.call_args_list)
        assert "empty" in call_args.lower() or "vacía" in call_args.lower()
    
    @patch('rich.console.Console.print')
    def test_show_collection_info_with_data(self, mock_print):
        """Test show_collection_info con datos."""
        from meribot.crawler.chroma_explorer import show_collection_info
        
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 100
        mock_collection.get.return_value = {
            'embeddings': [[0.1, 0.2, 0.3]]  # Embedding de ejemplo
        }
        mock_collection.name = 'test_collection'
        mock_db._collection = mock_collection
        
        show_collection_info(mock_db)
        
        mock_print.assert_called()
        mock_collection.count.assert_called_once()
        mock_collection.get.assert_called_once_with(limit=1)
    
    @patch('rich.console.Console.print')
    def test_show_collection_info_exception(self, mock_print):
        """Test manejo de excepción en show_collection_info."""
        from meribot.crawler.chroma_explorer import show_collection_info
        
        mock_db = MagicMock()
        mock_db._collection.count.side_effect = Exception("Collection error")
        
        show_collection_info(mock_db)
        
        mock_print.assert_called()
        # Verificar que se mostró mensaje de error
        error_shown = any("error" in str(call).lower() for call in mock_print.call_args_list)
        assert error_shown
    
    @patch('rich.console.Console.print')
    def test_search_documents_success(self, mock_print):
        """Test búsqueda exitosa de documentos."""
        from meribot.crawler.chroma_explorer import search_documents
        from langchain.schema import Document
        
        mock_db = MagicMock()
        mock_results = [
            (Document(page_content="Result 1", metadata={"id": "1"}), 0.85),
            (Document(page_content="Result 2", metadata={"source": "doc2.pdf"}), 0.90)
        ]
        mock_db.similarity_search_with_score.return_value = mock_results
        
        search_documents(mock_db, "test query", k=2)
        
        mock_db.similarity_search_with_score.assert_called_once_with("test query", k=2)
        
        # Verificar que se imprimieron los resultados
        assert mock_print.call_count >= 2  # Al menos cabecera + resultados
    
    @patch('rich.console.Console.print')
    def test_search_documents_no_results(self, mock_print):
        """Test búsqueda sin resultados."""
        from meribot.crawler.chroma_explorer import search_documents
        
        mock_db = MagicMock()
        mock_db.similarity_search_with_score.return_value = []
        
        search_documents(mock_db, "no results query")
        
        mock_print.assert_called()
        # Verificar mensaje de sin resultados
        no_results_shown = any("no matching" in str(call).lower() or "no results" in str(call).lower() 
                              for call in mock_print.call_args_list)
        assert no_results_shown
    
    @patch('rich.console.Console.print')
    def test_search_documents_exception(self, mock_print):
        """Test manejo de excepción en búsqueda."""
        from meribot.crawler.chroma_explorer import search_documents
        
        mock_db = MagicMock()
        mock_db.similarity_search_with_score.side_effect = Exception("Search error")
        
        search_documents(mock_db, "error query")
        
        mock_print.assert_called()
        # Verificar que se mostró mensaje de error
        error_shown = any("error" in str(call).lower() for call in mock_print.call_args_list)
        assert error_shown


class TestUtilitiesIntegration:
    """Tests de integración para las utilidades."""
    
    @patch('sys.argv', ['check_embeddings.py', '--persist', '/test/path', '--q', 'test query'])
    @patch('meribot.crawler.check_embeddings.SemanticSearchCLI.run')
    def test_check_embeddings_main(self, mock_run):
        """Test función main de check_embeddings."""
        from meribot.crawler.check_embeddings import main
        
        mock_run.return_value = 0
        
        result = main()
        
        assert result == 0
        mock_run.assert_called_once()
    
    def test_semantic_search_cli_workflow(self):
        """Test workflow completo de SemanticSearchCLI."""
        from meribot.crawler.check_embeddings import SemanticSearchCLI
        
        cli = SemanticSearchCLI()
        
        # Verificar inicialización
        assert cli.parser is not None
        assert cli.args is None
        assert cli.embeddings is None
        assert cli.vectorstore is None
        
        # Test creación de parser
        parser = cli._create_parser()
        args = parser.parse_args(['--persist', '/test'])
        
        assert args.persist == '/test'
        assert args.collection == 'default'
        assert args.k == 5
    
    @patch('os.path.exists')
    @patch('rich.prompt.Prompt.ask')
    @patch('meribot.crawler.chroma_explorer.initialize_chroma')
    @patch('meribot.crawler.chroma_explorer.clear_screen')
    @patch('meribot.crawler.chroma_explorer.display_header')
    def test_chroma_explorer_main_workflow(self, mock_header, mock_clear, mock_init, mock_prompt, mock_exists):
        """Test workflow básico de chroma_explorer main."""
        mock_exists.return_value = True
        mock_init.return_value = None  # Simular fallo de inicialización
        mock_prompt.return_value = 'n'  # No reintentar
        
        # Importar y test básico de main (sin ejecutar loop completo)
        from meribot.crawler import chroma_explorer
        
        # Verificar que las funciones están disponibles
        assert hasattr(chroma_explorer, 'main')
        assert hasattr(chroma_explorer, 'initialize_chroma')
        assert hasattr(chroma_explorer, 'show_collection_info')
        assert hasattr(chroma_explorer, 'search_documents')


# Fixtures para tests de utilidades
@pytest.fixture
def mock_document():
    """Fixture con documento mock para tests."""
    from langchain.schema import Document
    return Document(
        page_content="This is test document content for search testing.",
        metadata={
            "id": "test_doc_1",
            "source": "test_document.pdf",
            "page": 1
        }
    )


@pytest.fixture
def mock_search_results(mock_document):
    """Fixture con resultados de búsqueda mock."""
    return [
        (mock_document, 0.85),
        (Document(
            page_content="Another test document with different content.",
            metadata={"id": "test_doc_2", "source": "another_doc.pdf"}
        ), 0.92)
    ]


@pytest.fixture
def mock_chroma_db():
    """Fixture con base de datos Chroma mock."""
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 50
    mock_collection.name = 'test_collection'
    mock_db._collection = mock_collection
    return mock_db


@pytest.fixture
def semantic_cli():
    """Fixture con instancia de SemanticSearchCLI."""
    from meribot.crawler.check_embeddings import SemanticSearchCLI
    return SemanticSearchCLI()