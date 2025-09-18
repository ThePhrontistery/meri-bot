"""
Tests unitarios para el módulo document_loader.py del crawler.
Valida funciones de parsing de documentos, chunking de texto, y generación de embeddings.
"""

import pytest
import numpy as np
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from typing import List, Dict, Any

from meribot.crawler.document_loader import (
    parse_html,
    parse_docx,
    parse_xlsx,
    parse_pdf,
    parse_document,
    chunk_text_with_langchain,
    semantic_chunk_text,
    split_text,
    normalize_text,
    get_azure_openai_embeddings,
    process_and_classify_chunks
)


class TestParseHtml:
    """Tests para la función parse_html."""
    
    def test_parse_html_basic_content(self):
        """Test parsing básico de HTML con contenido simple."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <main>
                <h1>Main Title</h1>
                <p>This is the main content of the page.</p>
                <p>Another paragraph with important information.</p>
            </main>
        </body>
        </html>
        """
        
        result = parse_html(html_content, url="https://example.com")
        
        assert "error" not in result
        assert result["text"] is not None
        assert "Main Title" in result["text"]
        assert "main content" in result["text"]
        assert result["metadata"]["title"] == "Test Page"
        assert result["metadata"]["type"] == "html"
        assert result["metadata"]["url"] == "https://example.com"
    
    def test_parse_html_main_priority(self):
        """Test que parse_html prioriza contenido en tag <main>."""
        html_content = """
        <html>
        <body>
            <div>Some random content</div>
            <main>Main content should be extracted</main>
            <div>More random content</div>
        </body>
        </html>
        """
        
        result = parse_html(html_content)
        
        assert "Main content should be extracted" in result["text"]
        assert "random content" not in result["text"]
    
    def test_parse_html_article_fallback(self):
        """Test fallback a tag <article> cuando no hay <main>."""
        html_content = """
        <html>
        <body>
            <div>Some random content</div>
            <article>Article content should be extracted</article>
            <div>More random content</div>
        </body>
        </html>
        """
        
        result = parse_html(html_content)
        
        assert "Article content should be extracted" in result["text"]
    
    def test_parse_html_section_fallback(self):
        """Test fallback a tag <section> cuando no hay <main> ni <article>."""
        html_content = """
        <html>
        <body>
            <div>Some random content</div>
            <section>Section content should be extracted</section>
            <div>More random content</div>
        </body>
        </html>
        """
        
        result = parse_html(html_content)
        
        assert "Section content should be extracted" in result["text"]
    
    def test_parse_html_body_fallback(self):
        """Test fallback a <body> cuando no hay tags semánticos."""
        html_content = """
        <html>
        <body>
            <div>Body content should be extracted</div>
            <p>More body content</p>
        </body>
        </html>
        """
        
        result = parse_html(html_content)
        
        assert "Body content should be extracted" in result["text"]
        assert "More body content" in result["text"]
    
    def test_parse_html_no_title(self):
        """Test manejo de HTML sin título."""
        html_content = """
        <html>
        <body>
            <main>Content without title</main>
        </body>
        </html>
        """
        
        result = parse_html(html_content)
        
        assert result["metadata"]["title"] is None
        assert result["text"] == "Content without title"
    
    def test_parse_html_empty_content(self):
        """Test manejo de HTML vacío o sin contenido."""
        html_content = "<html><body></body></html>"
        
        result = parse_html(html_content)
        
        assert result["text"] == ""
        assert result["metadata"]["type"] == "html"
    
    def test_parse_html_invalid_html(self):
        """Test manejo de HTML malformado."""
        invalid_html = "This is not valid HTML content"
        
        result = parse_html(invalid_html)
        
        # BeautifulSoup debería manejar HTML malformado gracefully
        assert "error" not in result
        assert result["text"] is not None


class TestParseDocx:
    """Tests para la función parse_docx."""
    
    def test_parse_docx_not_available(self):
        """Test cuando python-docx no está disponible."""
        with patch('meribot.crawler.document_loader.DOCX_AVAILABLE', False):
            result = parse_docx("test.docx")
            
            assert "error" in result
            assert "python-docx no está instalado" in result["error"]
            assert result["text"] is None
            assert result["metadata"] is None
    
    @patch('meribot.crawler.document_loader.DOCX_AVAILABLE', True)
    @patch('meribot.crawler.document_loader.docx')
    def test_parse_docx_successful(self, mock_docx):
        """Test parsing exitoso de archivo DOCX."""
        # Mock document object
        mock_doc = MagicMock()
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "First paragraph"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Second paragraph"
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        
        # Mock core properties
        mock_props = MagicMock()
        mock_props.title = "Test Document"
        mock_props.author = "Test Author"
        mock_props.created = "2023-01-01"
        mock_doc.core_properties = mock_props
        
        mock_docx.Document.return_value = mock_doc
        
        result = parse_docx("test.docx", url="https://example.com/doc.docx")
        
        assert "error" not in result
        assert result["text"] == "First paragraph\nSecond paragraph"
        assert result["metadata"]["title"] == "Test Document"
        assert result["metadata"]["author"] == "Test Author"
        assert result["metadata"]["type"] == "docx"
        assert result["metadata"]["url"] == "https://example.com/doc.docx"
    
    @patch('meribot.crawler.document_loader.DOCX_AVAILABLE', True)
    @patch('meribot.crawler.document_loader.docx')
    def test_parse_docx_exception(self, mock_docx):
        """Test manejo de excepción en parsing de DOCX."""
        mock_docx.Document.side_effect = Exception("File corrupted")
        
        result = parse_docx("corrupted.docx")
        
        assert "error" in result
        assert "File corrupted" in result["error"]
        assert result["text"] is None


class TestParseXlsx:
    """Tests para la función parse_xlsx."""
    
    def test_parse_xlsx_not_available(self):
        """Test cuando openpyxl no está disponible."""
        with patch('meribot.crawler.document_loader.XLSX_AVAILABLE', False):
            result = parse_xlsx("test.xlsx")
            
            assert "error" in result
            assert "openpyxl no está instalado" in result["error"]
            assert result["text"] is None
            assert result["metadata"] is None
    
    @patch('meribot.crawler.document_loader.XLSX_AVAILABLE', True)
    @patch('meribot.crawler.document_loader.openpyxl')
    def test_parse_xlsx_successful(self, mock_openpyxl):
        """Test parsing exitoso de archivo XLSX."""
        # Mock workbook and worksheet
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        
        # Mock rows data
        mock_ws.iter_rows.return_value = [
            ("Name", "Age", "City"),
            ("John", 30, "New York"),
            ("Jane", 25, "London"),
            (None, 35, "Paris")  # Test None value handling
        ]
        
        mock_wb.worksheets = [mock_ws]
        mock_wb.sheetnames = ["Sheet1"]
        mock_openpyxl.load_workbook.return_value = mock_wb
        
        result = parse_xlsx("test.xlsx", url="https://example.com/data.xlsx")
        
        assert "error" not in result
        assert "Name\tAge\tCity" in result["text"]
        assert "John\t30\tNew York" in result["text"]
        assert "\t35\tParis" in result["text"]  # None becomes empty string
        assert result["metadata"]["type"] == "xlsx"
        assert result["metadata"]["sheets"] == ["Sheet1"]
        assert result["metadata"]["url"] == "https://example.com/data.xlsx"
    
    @patch('meribot.crawler.document_loader.XLSX_AVAILABLE', True)
    @patch('meribot.crawler.document_loader.openpyxl')
    def test_parse_xlsx_exception(self, mock_openpyxl):
        """Test manejo de excepción en parsing de XLSX."""
        mock_openpyxl.load_workbook.side_effect = Exception("File error")
        
        result = parse_xlsx("error.xlsx")
        
        assert "error" in result
        assert "File error" in result["error"]


class TestParsePdf:
    """Tests para la función parse_pdf."""
    
    def test_parse_pdf_not_available(self):
        """Test cuando PyMuPDF no está disponible."""
        with patch('meribot.crawler.document_loader.PDF_AVAILABLE', False):
            result = parse_pdf("test.pdf")
            
            assert "error" in result
            assert "PyMuPDF (fitz) no está instalado" in result["error"]
            assert result["text"] is None
            assert result["metadata"] is None
    
    @patch('meribot.crawler.document_loader.PDF_AVAILABLE', True)
    @patch('meribot.crawler.document_loader.fitz')
    def test_parse_pdf_successful(self, mock_fitz):
        """Test parsing exitoso de archivo PDF."""
        # Mock PDF document
        mock_doc = MagicMock()
        
        # Mock pages
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "First page content"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Second page content"
        
        mock_doc.__iter__ = lambda x: iter([mock_page1, mock_page2])
        mock_doc.metadata = {
            "title": "Test PDF",
            "author": "PDF Author",
            "creationDate": "2023-01-01"
        }
        
        mock_fitz.open.return_value = mock_doc
        
        result = parse_pdf("test.pdf", url="https://example.com/doc.pdf")
        
        assert "error" not in result
        assert result["text"] == "First page content\nSecond page content"
        assert result["metadata"]["title"] == "Test PDF"
        assert result["metadata"]["author"] == "PDF Author"
        assert result["metadata"]["type"] == "pdf"
        assert result["metadata"]["url"] == "https://example.com/doc.pdf"
    
    @patch('meribot.crawler.document_loader.PDF_AVAILABLE', True)
    @patch('meribot.crawler.document_loader.fitz')
    def test_parse_pdf_exception(self, mock_fitz):
        """Test manejo de excepción en parsing de PDF."""
        mock_fitz.open.side_effect = Exception("PDF error")
        
        result = parse_pdf("error.pdf")
        
        assert "error" in result
        assert "PDF error" in result["error"]


class TestParseDocument:
    """Tests para la función parse_document."""
    
    @patch('meribot.crawler.document_loader.parse_html')
    @patch("builtins.open", mock_open(read_data="<html><body>Test</body></html>"))
    def test_parse_document_html_by_extension(self, mock_parse_html):
        """Test parsing de documento HTML por extensión."""
        mock_parse_html.return_value = {"text": "Test content", "metadata": {}}
        
        result = parse_document("test.html", url="https://example.com")
        
        mock_parse_html.assert_called_once()
        assert result == {"text": "Test content", "metadata": {}}
    
    @patch('meribot.crawler.document_loader.parse_html')
    @patch("builtins.open", mock_open(read_data="<!DOCTYPE html><html><body>Test</body></html>"))
    def test_parse_document_html_by_content(self, mock_parse_html):
        """Test detección de HTML por contenido cuando no hay extensión."""
        mock_parse_html.return_value = {"text": "Test content", "metadata": {}}
        
        result = parse_document("test", url="https://example.com")
        
        mock_parse_html.assert_called_once()
    
    @patch('meribot.crawler.document_loader.parse_docx')
    def test_parse_document_docx(self, mock_parse_docx):
        """Test parsing de documento DOCX."""
        mock_parse_docx.return_value = {"text": "DOCX content", "metadata": {}}
        
        result = parse_document("test.docx", url="https://example.com")
        
        mock_parse_docx.assert_called_once_with("test.docx", url="NO_URL_ORIGINAL: https://example.com")
    
    @patch('meribot.crawler.document_loader.parse_xlsx')
    def test_parse_document_xlsx(self, mock_parse_xlsx):
        """Test parsing de documento XLSX."""
        mock_parse_xlsx.return_value = {"text": "XLSX content", "metadata": {}}
        
        result = parse_document("test.xlsx")
        
        mock_parse_xlsx.assert_called_once_with("test.xlsx", url=None)
    
    @patch('meribot.crawler.document_loader.parse_pdf')
    def test_parse_document_pdf(self, mock_parse_pdf):
        """Test parsing de documento PDF."""
        mock_parse_pdf.return_value = {"text": "PDF content", "metadata": {}}
        
        result = parse_document("test.pdf", url="https://example.com/doc.pdf")
        
        mock_parse_pdf.assert_called_once_with("test.pdf", url="https://example.com/doc.pdf")
    
    def test_parse_document_unsupported_format(self):
        """Test manejo de formato no soportado."""
        result = parse_document("test.txt")
        
        assert "error" in result
        assert "Formato no soportado" in result["error"]
        assert ".txt" in result["error"]
    
    def test_parse_document_full_url_detection(self):
        """Test detección correcta de URLs completas."""
        with patch('meribot.crawler.document_loader.parse_pdf') as mock_parse_pdf:
            mock_parse_pdf.return_value = {"text": "content", "metadata": {}}
            
            # URL completa
            parse_document("test.pdf", url="https://example.com/doc.pdf")
            mock_parse_pdf.assert_called_with("test.pdf", url="https://example.com/doc.pdf")
            
            # URL incompleta
            mock_parse_pdf.reset_mock()
            parse_document("test.pdf", url="relative/path")
            mock_parse_pdf.assert_called_with("test.pdf", url="NO_URL_ORIGINAL: relative/path")


class TestChunkTextWithLangchain:
    """Tests para la función chunk_text_with_langchain."""
    
    @patch('meribot.crawler.document_loader.RecursiveCharacterTextSplitter')
    def test_chunk_text_with_langchain_basic(self, mock_splitter_class):
        """Test chunking básico con LangChain."""
        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_splitter_class.return_value = mock_splitter
        
        text = "This is a long text that needs to be chunked into smaller pieces."
        result = chunk_text_with_langchain(text, chunk_size=100, chunk_overlap=20)
        
        # Verificar configuración del splitter
        mock_splitter_class.assert_called_once_with(
            chunk_size=100,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False
        )
        
        # Verificar resultado
        mock_splitter.split_text.assert_called_once_with(text)
        assert result == ["chunk1", "chunk2", "chunk3"]
    
    def test_chunk_text_with_langchain_empty_text(self):
        """Test manejo de texto vacío."""
        result = chunk_text_with_langchain("")
        assert result == []
        
        result = chunk_text_with_langchain("   ")
        assert result == []
    
    def test_chunk_text_with_langchain_none_text(self):
        """Test manejo de texto None."""
        result = chunk_text_with_langchain(None)
        assert result == []
    
    @patch('meribot.crawler.document_loader.RecursiveCharacterTextSplitter')
    def test_chunk_text_with_langchain_default_params(self, mock_splitter_class):
        """Test uso de parámetros por defecto."""
        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["chunk"]
        mock_splitter_class.return_value = mock_splitter
        
        chunk_text_with_langchain("test text")
        
        # Verificar parámetros por defecto
        mock_splitter_class.assert_called_once_with(
            chunk_size=2000,  # SPLITTER_CHUNK_SIZE_DOC
            chunk_overlap=50,  # SPLITTER_CHUNK_OVERLAP_DOC
            length_function=len,
            is_separator_regex=False
        )


class TestSemanticChunkText:
    """Tests para la función semantic_chunk_text (deprecated)."""
    
    @patch('meribot.crawler.document_loader.chunk_text_with_langchain')
    def test_semantic_chunk_text_deprecation_redirect(self, mock_chunk_langchain):
        """Test que semantic_chunk_text redirige a chunk_text_with_langchain."""
        mock_chunk_langchain.return_value = ["chunk1", "chunk2"]
        
        result = semantic_chunk_text("test text", max_chunk_size=1000, stride=25)
        
        # Verificar redirección
        mock_chunk_langchain.assert_called_once_with("test text", chunk_size=1000, chunk_overlap=25)
        assert result == ["chunk1", "chunk2"]


class TestSplitText:
    """Tests para la función split_text."""
    
    def test_split_text_basic(self):
        """Test splitting básico por oraciones."""
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        result = split_text(text, max_length=30)
        
        assert len(result) > 1
        assert all(len(chunk) <= 30 for chunk in result)
        assert "First sentence." in result[0]
    
    def test_split_text_long_sentence(self):
        """Test manejo de oraciones más largas que max_length."""
        text = "This is a very long sentence that exceeds the maximum length limit."
        result = split_text(text, max_length=20)
        
        # Debería incluir la oración completa aunque sea más larga
        assert len(result) == 1
        assert result[0] == text
    
    def test_split_text_invalid_input(self):
        """Test manejo de inputs inválidos."""
        # Input no string
        result = split_text(123)
        assert result == [123]
        
        # max_length inválido
        result = split_text("test text", max_length=0)
        assert result == ["test text"]
        
        result = split_text("test text", max_length=-1)
        assert result == ["test text"]
    
    def test_split_text_empty_string(self):
        """Test manejo de string vacío."""
        result = split_text("")
        assert result == [""]
    
    def test_split_text_no_sentences(self):
        """Test texto sin delimitadores de oraciones."""
        text = "This is text without sentence delimiters"
        result = split_text(text, max_length=100)
        
        assert len(result) == 1
        assert result[0] == text


class TestNormalizeText:
    """Tests para la función normalize_text."""
    
    def test_normalize_text_basic(self):
        """Test normalización básica de texto."""
        text = "  This   is  \n\n\n  text  with   extra   spaces  \n\n  "
        result = normalize_text(text)
        
        assert result == "This is\ntext with extra spaces"
    
    def test_normalize_text_control_characters(self):
        """Test eliminación de caracteres de control."""
        text = "Text\x00with\x01control\x02characters\x1f"
        result = normalize_text(text)
        
        assert result == "Textwithcontrolcharacters"
        assert "\x00" not in result
        assert "\x01" not in result
    
    def test_normalize_text_preserve_tabs_newlines(self):
        """Test preservación de tabs y newlines."""
        text = "Text\twith\ttabs\nand\nnewlines"
        result = normalize_text(text)
        
        assert "\t" in result
        assert "\n" in result
        assert result == "Text\twith\ttabs\nand\nnewlines"
    
    def test_normalize_text_non_string_input(self):
        """Test manejo de input no string."""
        result = normalize_text(123)
        assert result == 123
        
        result = normalize_text(None)
        assert result is None
    
    def test_normalize_text_empty_string(self):
        """Test texto vacío."""
        result = normalize_text("")
        assert result == ""


class TestGetAzureOpenaiEmbeddings:
    """Tests para la función get_azure_openai_embeddings."""
    
    def test_get_azure_openai_embeddings_missing_env_vars(self):
        """Test error cuando faltan variables de entorno."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError) as exc_info:
                get_azure_openai_embeddings(["test sentence"])
            
            assert "Faltan variables de entorno" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT": "test-deployment"
    })
    @patch('meribot.crawler.document_loader.requests.post')
    def test_get_azure_openai_embeddings_success(self, mock_post):
        """Test obtención exitosa de embeddings."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]}
            ]
        }
        mock_post.return_value = mock_response
        
        sentences = ["First sentence", "Second sentence"]
        result = get_azure_openai_embeddings(sentences)
        
        # Verificar llamada a API
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "embeddings" in call_args[1]["data"]
        
        # Verificar resultado
        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 3)
        assert np.array_equal(result[0], [0.1, 0.2, 0.3])
        assert np.array_equal(result[1], [0.4, 0.5, 0.6])
    
    @patch.dict(os.environ, {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT": "test-deployment"
    })
    @patch('meribot.crawler.document_loader.requests.post')
    def test_get_azure_openai_embeddings_api_error(self, mock_post):
        """Test manejo de error de API."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc_info:
            get_azure_openai_embeddings(["test sentence"])
        
        assert "Error Azure OpenAI: 400" in str(exc_info.value)


class TestProcessAndClassifyChunks:
    """Tests para la función process_and_classify_chunks."""
    
    @patch('meribot.crawler.document_loader.load_hash_db')
    @patch('meribot.crawler.document_loader.save_hash_db')
    @patch('meribot.crawler.document_loader.calculate_sha256')
    def test_process_and_classify_chunks_new_chunks(self, mock_hash, mock_save, mock_load):
        """Test clasificación de chunks nuevos."""
        mock_load.return_value = {}  # Hash DB vacía
        mock_hash.side_effect = ["hash1", "hash2"]
        
        chunks = ["First chunk", "Second chunk"]
        metadata = [{"id": "doc1_chunk1"}, {"id": "doc1_chunk2"}]
        
        result = process_and_classify_chunks(chunks, metadata)
        
        assert len(result) == 2
        assert result[0] == ("First chunk", {"id": "doc1_chunk1"}, "nuevo")
        assert result[1] == ("Second chunk", {"id": "doc1_chunk2"}, "nuevo")
        
        # Verificar que se guarda la hash DB
        mock_save.assert_called_once()
    
    @patch('meribot.crawler.document_loader.load_hash_db')
    @patch('meribot.crawler.document_loader.save_hash_db')
    @patch('meribot.crawler.document_loader.calculate_sha256')
    def test_process_and_classify_chunks_unchanged_chunks(self, mock_hash, mock_save, mock_load):
        """Test clasificación de chunks sin cambios."""
        mock_load.return_value = {"doc1_chunk1": "existing_hash"}
        mock_hash.return_value = "existing_hash"
        
        chunks = ["Unchanged chunk"]
        metadata = [{"id": "doc1_chunk1"}]
        
        result = process_and_classify_chunks(chunks, metadata)
        
        assert len(result) == 1
        assert result[0][2] == "sin cambios"
    
    @patch('meribot.crawler.document_loader.load_hash_db')
    @patch('meribot.crawler.document_loader.save_hash_db')
    @patch('meribot.crawler.document_loader.calculate_sha256')
    def test_process_and_classify_chunks_modified_chunks(self, mock_hash, mock_save, mock_load):
        """Test clasificación de chunks modificados."""
        mock_load.return_value = {"doc1_chunk1": "old_hash"}
        mock_hash.return_value = "new_hash"
        
        chunks = ["Modified chunk"]
        metadata = [{"id": "doc1_chunk1"}]
        
        result = process_and_classify_chunks(chunks, metadata)
        
        assert len(result) == 1
        assert result[0][2] == "modificado"
    
    @patch('meribot.crawler.document_loader.load_hash_db')
    @patch('meribot.crawler.document_loader.save_hash_db')
    @patch('meribot.crawler.document_loader.calculate_sha256')
    def test_process_and_classify_chunks_fallback_id(self, mock_hash, mock_save, mock_load):
        """Test fallback para ID cuando no está disponible en metadata."""
        mock_load.return_value = {}
        mock_hash.return_value = "test_hash"
        
        chunks = ["Test chunk"]
        metadata = [{"url": "https://example.com"}]  # No hay 'id'
        
        result = process_and_classify_chunks(chunks, metadata)
        
        assert len(result) == 1
        # Debería usar 'url' como fallback
        assert result[0][2] == "nuevo"


# Fixtures para tests de document_loader
@pytest.fixture
def sample_html():
    """Fixture con HTML de ejemplo."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Sample Document</title></head>
    <body>
        <main>
            <h1>Main Heading</h1>
            <p>This is the main content of the document.</p>
            <p>It contains multiple paragraphs with useful information.</p>
        </main>
    </body>
    </html>
    """


@pytest.fixture
def sample_text():
    """Fixture con texto de ejemplo para chunking."""
    return """
    This is a sample document with multiple sentences. It contains various types of information
    that need to be processed and chunked appropriately. The document discusses important topics
    related to business operations and customer service. Each paragraph contains valuable insights
    that should be preserved during the chunking process. The text is designed to test various
    scenarios including sentence boundaries and paragraph breaks.
    """


@pytest.fixture
def sample_chunks():
    """Fixture con chunks de ejemplo."""
    return [
        "This is the first chunk of text content.",
        "This is the second chunk with different information.",
        "This is the third chunk completing the set."
    ]


@pytest.fixture
def sample_metadata():
    """Fixture con metadata de ejemplo."""
    return [
        {"id": "doc1_chunk1", "source": "document1.pdf"},
        {"id": "doc1_chunk2", "source": "document1.pdf"},
        {"id": "doc1_chunk3", "source": "document1.pdf"}
    ]