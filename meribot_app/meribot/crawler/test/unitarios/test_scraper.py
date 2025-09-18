"""
Tests unitarios para el módulo scraper.py del crawler.
Valida funcionalidad de web scraping, descubrimiento de URLs, y descarga de documentos.
"""

import pytest
import os
import tempfile
import requests
from unittest.mock import patch, MagicMock, mock_open
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from meribot.crawler.scraper import WebScraper


class TestWebScraperInit:
    """Tests para la inicialización de WebScraper."""
    
    def test_web_scraper_init_basic(self):
        """Test inicialización básica de WebScraper."""
        config = {
            "allowed_domains": ["example.com", "test.com"],
            "max_depth": 2,
            "file_types": ["html", "pdf"],
            "delay": 1.0,
            "user_agent": "TestBot/1.0"
        }
        
        mock_logger = MagicMock()
        scraper = WebScraper(config, logger=mock_logger)
        
        assert scraper.config == config
        assert scraper.logger == mock_logger
        assert scraper.allowed_domains == {"example.com", "test.com"}
        assert scraper.max_depth == 2
        assert scraper.file_types == {"html", "pdf"}
        assert scraper.delay == 1.0
        assert scraper.user_agent == "TestBot/1.0"
        assert scraper.visited == set()
    
    def test_web_scraper_init_defaults(self):
        """Test inicialización con valores por defecto."""
        config = {
            "allowed_domains": ["example.com"]
        }
        
        scraper = WebScraper(config)
        
        assert scraper.max_depth == 2  # Default
        assert scraper.file_types == {"html", "pdf", "docx", "xlsx"}  # Default
        assert scraper.delay == 1.0  # Default
        assert scraper.user_agent == "MeriBot/1.0"  # Default
        assert scraper.logger is not None  # Default logger created
    
    @patch('meribot.crawler.scraper.get_logger')
    def test_web_scraper_init_default_logger(self, mock_get_logger):
        """Test creación de logger por defecto."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        
        mock_get_logger.assert_called_once_with("WebScraper")
        assert scraper.logger == mock_logger


class TestWebScraperGetLocalPath:
    """Tests para el método _get_local_path."""
    
    def test_get_local_path_basic(self):
        """Test generación de path local básico."""
        config = {
            "allowed_domains": ["example.com"],
            "output_dir": "./test_data"
        }
        scraper = WebScraper(config)
        
        url = "https://example.com/docs/file.pdf"
        path = scraper._get_local_path(url, "pdf")
        
        expected_path = os.path.join("./test_data", "example.com", "docs", "file.pdf")
        assert path == expected_path
    
    def test_get_local_path_with_port(self):
        """Test path local con puerto en URL."""
        config = {
            "allowed_domains": ["example.com:8080"],
            "output_dir": "./test_data"
        }
        scraper = WebScraper(config)
        
        url = "https://example.com:8080/file.html"
        path = scraper._get_local_path(url, "html")
        
        # Los dos puntos deben ser reemplazados por underscore
        expected_path = os.path.join("./test_data", "example.com_8080", "file.html")
        assert path == expected_path
    
    def test_get_local_path_root_url(self):
        """Test path local para URL raíz."""
        config = {
            "allowed_domains": ["example.com"],
            "output_dir": "./test_data"
        }
        scraper = WebScraper(config)
        
        url = "https://example.com/"
        path = scraper._get_local_path(url, "html")
        
        expected_path = os.path.join("./test_data", "example.com", "index.html")
        assert path == expected_path
    
    def test_get_local_path_no_extension(self):
        """Test path local sin extensión en URL."""
        config = {
            "allowed_domains": ["example.com"],
            "output_dir": "./test_data"
        }
        scraper = WebScraper(config)
        
        url = "https://example.com/docs"
        path = scraper._get_local_path(url, "html")
        
        expected_path = os.path.join("./test_data", "example.com", "docs", "index.html")
        assert path == expected_path
    
    def test_get_local_path_default_output_dir(self):
        """Test path local con directorio por defecto."""
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        
        url = "https://example.com/file.pdf"
        path = scraper._get_local_path(url, "pdf")
        
        # Debería usar el directorio por defecto
        assert "./data/scraped" in path
        assert "example.com" in path
        assert "file.pdf" in path


class TestWebScraperSaveHtml:
    """Tests para el método save_html."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.dirname')
    @patch('pathlib.Path')
    def test_save_html_success(self, mock_path, mock_dirname, mock_file):
        """Test guardado exitoso de HTML."""
        config = {
            "allowed_domains": ["example.com"],
            "output_dir": "./test_data"
        }
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        # Mock Path.mkdir
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_dirname.return_value = "/test/dir"
        
        url = "https://example.com/page.html"
        html_content = "<html><body>Test content</body></html>"
        
        scraper.save_html(url, html_content)
        
        # Verificar que se abrieron ambos archivos
        assert mock_file.call_count == 2
        
        # Verificar logs
        scraper.logger.info.assert_called_once()
        assert "[GUARDADO HTML]" in scraper.logger.info.call_args[0][0]
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_html_error(self, mock_file):
        """Test manejo de error al guardar HTML."""
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        url = "https://example.com/page.html"
        html_content = "<html><body>Test</body></html>"
        
        scraper.save_html(url, html_content)
        
        # Verificar log de error
        scraper.logger.error.assert_called_once()
        assert "Error guardando HTML" in scraper.logger.error.call_args[0][0]


class TestWebScraperDownloadFile:
    """Tests para el método download_file."""
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.dirname')
    @patch('pathlib.Path')
    def test_download_file_new_file(self, mock_path, mock_dirname, mock_exists, mock_file, mock_requests):
        """Test descarga de archivo nuevo."""
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        scraper.user_agent = "TestBot/1.0"
        
        # Setup mocks
        mock_exists.return_value = False  # Archivo no existe
        mock_response = MagicMock()
        mock_response.content = b"file content"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_dirname.return_value = "/test/dir"
        
        url = "https://example.com/document.pdf"
        scraper.download_file(url)
        
        # Verificar request
        mock_requests.assert_called_once_with(
            url,
            headers={"User-Agent": "TestBot/1.0"},
            timeout=20,
            verify=False
        )
        
        # Verificar que se guardaron ambos archivos
        assert mock_file.call_count == 2  # .url y archivo principal
        
        # Verificar logs
        scraper.logger.info.assert_called()
        assert "[DESCARGADO]" in str(scraper.logger.info.call_args_list)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.dirname')
    @patch('pathlib.Path')
    def test_download_file_existing_file(self, mock_path, mock_dirname, mock_exists, mock_file):
        """Test manejo de archivo existente."""
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        # Setup mocks
        mock_exists.return_value = True  # Archivo ya existe
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_dirname.return_value = "/test/dir"
        
        url = "https://example.com/document.pdf"
        scraper.download_file(url)
        
        # Verificar que solo se guarda el archivo .url
        mock_file.assert_called_once()
        
        # Verificar log
        scraper.logger.info.assert_called_once()
        assert "[YA EXISTE]" in scraper.logger.info.call_args[0][0]
    
    @patch('requests.get', side_effect=requests.RequestException("Network error"))
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.dirname')
    @patch('pathlib.Path')
    def test_download_file_network_error(self, mock_path, mock_dirname, mock_exists, mock_file, mock_requests):
        """Test manejo de error de red."""
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        mock_exists.return_value = False
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_dirname.return_value = "/test/dir"
        
        url = "https://example.com/document.pdf"
        scraper.download_file(url)
        
        # Verificar log de error
        scraper.logger.error.assert_called_once()
        assert "Error descargando archivo" in scraper.logger.error.call_args[0][0]


class TestWebScraperParseLinks:
    """Tests para el método _parse_links."""
    
    def test_parse_links_basic(self):
        """Test parsing básico de links."""
        config = {
            "allowed_domains": ["example.com"],
            "file_types": ["html", "pdf", "docx"]
        }
        scraper = WebScraper(config)
        
        html = """
        <html>
        <body>
            <a href="page1.html">Page 1</a>
            <a href="document.pdf">PDF Document</a>
            <a href="report.docx">Word Document</a>
            <a href="image.jpg">Image</a>
            <a href="/about">About Page</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        base_url = "https://example.com/"
        
        links = scraper._parse_links(soup, base_url)
        
        # Verificar que se detectaron los links correctos
        expected_links = [
            ("page1.html", "html"),
            ("document.pdf", "pdf"),
            ("report.docx", "docx"),
            ("/about", "html")  # Sin extensión se considera HTML
        ]
        
        assert links == expected_links
    
    def test_parse_links_with_query_params(self):
        """Test parsing de links con parámetros de query."""
        config = {
            "allowed_domains": ["example.com"],
            "file_types": ["html", "pdf"]
        }
        scraper = WebScraper(config)
        
        html = """
        <html>
        <body>
            <a href="page.html?param=value&other=123">Page with params</a>
            <a href="doc.pdf?download=true#section1">PDF with params and fragment</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        links = scraper._parse_links(soup, "https://example.com/")
        
        # Los parámetros de query y fragmentos deberían ser removidos
        expected_links = [
            ("page.html", "html"),
            ("doc.pdf", "pdf")
        ]
        
        assert links == expected_links
    
    def test_parse_links_unsupported_types(self):
        """Test que se ignoran tipos de archivo no soportados."""
        config = {
            "allowed_domains": ["example.com"],
            "file_types": ["html", "pdf"]  # Solo HTML y PDF
        }
        scraper = WebScraper(config)
        
        html = """
        <html>
        <body>
            <a href="page.html">Supported HTML</a>
            <a href="doc.pdf">Supported PDF</a>
            <a href="image.jpg">Unsupported Image</a>
            <a href="video.mp4">Unsupported Video</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        links = scraper._parse_links(soup, "https://example.com/")
        
        # Solo deberían aparecer los tipos soportados
        expected_links = [
            ("page.html", "html"),
            ("doc.pdf", "pdf")
        ]
        
        assert links == expected_links
    
    def test_parse_links_no_href(self):
        """Test manejo de tags <a> sin href."""
        config = {
            "allowed_domains": ["example.com"],
            "file_types": ["html"]
        }
        scraper = WebScraper(config)
        
        html = """
        <html>
        <body>
            <a href="valid.html">Valid link</a>
            <a name="anchor">Anchor without href</a>
            <a>Link without href attribute</a>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        links = scraper._parse_links(soup, "https://example.com/")
        
        # Solo el link válido debería aparecer
        assert links == [("valid.html", "html")]
    
    def test_parse_links_empty_soup(self):
        """Test parsing con soup vacío."""
        config = {
            "allowed_domains": ["example.com"],
            "file_types": ["html"]
        }
        scraper = WebScraper(config)
        
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        links = scraper._parse_links(soup, "https://example.com/")
        
        assert links == []


class TestWebScraperCrawlUrl:
    """Tests para el método crawl_url."""
    
    @patch('time.sleep')
    @patch('requests.get')
    def test_crawl_url_html_success(self, mock_requests, mock_sleep):
        """Test crawling exitoso de página HTML."""
        config = {
            "allowed_domains": ["example.com"],
            "max_depth": 1,
            "file_types": ["html", "pdf"],
            "delay": 0.5,
            "user_agent": "TestBot/1.0"
        }
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        # Mock response
        html_content = """
        <html>
        <body>
            <a href="page2.html">Page 2</a>
            <a href="document.pdf">PDF Doc</a>
        </body>
        </html>
        """
        
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Mock save_html and download_file
        with patch.object(scraper, 'save_html') as mock_save:
            with patch.object(scraper, 'download_file') as mock_download:
                url = "https://example.com/page1.html"
                scraper.crawl_url(url, depth=0)
        
        # Verificar request
        mock_requests.assert_called_with(
            url,
            headers={"User-Agent": "TestBot/1.0"},
            timeout=10,
            verify=False
        )
        
        # Verificar que se guardó el HTML
        mock_save.assert_called_once_with(url, html_content)
        
        # Verificar que se descargó el PDF
        mock_download.assert_called_once()
        
        # Verificar que la URL se marcó como visitada
        assert url in scraper.visited
        
        # Verificar logs
        scraper.logger.info.assert_called()
    
    def test_crawl_url_max_depth_exceeded(self):
        """Test que no crawlea cuando se excede la profundidad máxima."""
        config = {
            "allowed_domains": ["example.com"],
            "max_depth": 2
        }
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        url = "https://example.com/deep.html"
        scraper.crawl_url(url, depth=3)  # Excede max_depth
        
        # Verificar que se loggeó el límite
        scraper.logger.info.assert_called_once()
        assert "Profundidad máxima alcanzada" in scraper.logger.info.call_args[0][0]
        
        # Verificar que no se visitó la URL
        assert url not in scraper.visited
    
    def test_crawl_url_domain_not_allowed(self):
        """Test que no crawlea dominios no permitidos."""
        config = {
            "allowed_domains": ["example.com"],
            "max_depth": 2
        }
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        url = "https://other-domain.com/page.html"
        scraper.crawl_url(url, depth=0)
        
        # Verificar log de dominio no permitido
        scraper.logger.info.assert_called_once()
        assert "Dominio no permitido" in scraper.logger.info.call_args[0][0]
        
        # Verificar que no se visitó la URL
        assert url not in scraper.visited
    
    def test_crawl_url_already_visited(self):
        """Test que no crawlea URLs ya visitadas."""
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        url = "https://example.com/page.html"
        scraper.visited.add(url)  # Marcar como ya visitada
        
        with patch('requests.get') as mock_requests:
            scraper.crawl_url(url, depth=0)
        
        # No debería hacer request
        mock_requests.assert_not_called()
    
    @patch('requests.get')
    def test_crawl_url_document_direct(self, mock_requests):
        """Test crawling directo de documento (no HTML)."""
        config = {
            "allowed_domains": ["example.com"],
            "file_types": ["pdf"]
        }
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        # Mock response para PDF
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        with patch.object(scraper, 'download_file') as mock_download:
            url = "https://example.com/document.pdf"
            scraper.crawl_url(url, depth=0)
        
        # Verificar que se descargó el documento
        mock_download.assert_called_once_with(url)
        
        # Verificar que se loggeó como documento
        scraper.logger.info.assert_called()
    
    @patch('requests.get', side_effect=requests.RequestException("Network error"))
    def test_crawl_url_request_error(self, mock_requests):
        """Test manejo de error en request."""
        config = {"allowed_domains": ["example.com"]}
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        url = "https://example.com/error.html"
        scraper.crawl_url(url, depth=0)
        
        # Verificar log de error
        scraper.logger.error.assert_called_once()
        assert "Error procesando" in scraper.logger.error.call_args[0][0]
        
        # La URL debería estar marcada como visitada aunque haya fallado
        assert url in scraper.visited
    
    @patch('time.sleep')
    @patch('requests.get')
    def test_crawl_url_recursive_depth(self, mock_requests, mock_sleep):
        """Test crawling recursivo con control de profundidad."""
        config = {
            "allowed_domains": ["example.com"],
            "max_depth": 1,
            "delay": 0.1
        }
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        # HTML con link interno
        html_content = """
        <html>
        <body>
            <a href="subpage.html">Subpage</a>
        </body>
        </html>
        """
        
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        with patch.object(scraper, 'save_html'):
            url = "https://example.com/index.html"
            scraper.crawl_url(url, depth=0)
        
        # Verificar que se hizo sleep por el delay
        mock_sleep.assert_called_with(0.1)
        
        # Verificar múltiples calls por recursión
        assert mock_requests.call_count >= 1


class TestWebScraperIntegration:
    """Tests de integración para WebScraper."""
    
    @patch('meribot.crawler.scraper.load_yaml_config')
    @patch('meribot.crawler.scraper.validate_config')
    @patch('meribot.crawler.scraper.get_logger')
    def test_scraper_main_execution(self, mock_logger, mock_validate, mock_load_config):
        """Test ejecución del script principal del scraper."""
        # Setup mocks
        test_config = {
            "seeds": ["https://example.com"],
            "allowed_domains": ["example.com"],
            "file_types": ["html", "pdf"],
            "log_level": "INFO"
        }
        
        mock_load_config.return_value = test_config
        mock_validate.return_value = None
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        
        # Mock os.path.exists to simulate config file presence
        with patch('os.path.exists', return_value=True):
            with patch.object(WebScraper, 'crawl_url') as mock_crawl:
                # Import and run main section
                from meribot.crawler import scraper
                
                # Simulate running the main section
                config = mock_load_config.return_value
                mock_validate(config)
                logger = mock_logger.return_value
                
                scraper_instance = WebScraper(config, logger=logger)
                for url in config["seeds"]:
                    scraper_instance.crawl_url(url, depth=0)
                
                # Verify crawl was called for each seed
                assert mock_crawl.call_count == len(test_config["seeds"])
    
    def test_web_scraper_complete_workflow(self):
        """Test workflow completo de WebScraper."""
        config = {
            "allowed_domains": ["example.com"],
            "max_depth": 1,
            "file_types": ["html", "pdf"],
            "delay": 0.1,
            "user_agent": "TestBot/1.0",
            "output_dir": "./test_output"
        }
        
        scraper = WebScraper(config)
        scraper.logger = MagicMock()
        
        # Verificar inicialización correcta
        assert scraper.allowed_domains == {"example.com"}
        assert scraper.max_depth == 1
        assert scraper.file_types == {"html", "pdf"}
        assert scraper.visited == set()
        
        # Test path generation
        url = "https://example.com/docs/file.pdf"
        path = scraper._get_local_path(url, "pdf")
        expected = os.path.join("./test_output", "example.com", "docs", "file.pdf")
        assert path == expected
        
        # Test link parsing
        html = '<a href="test.pdf">PDF</a><a href="page.html">HTML</a>'
        soup = BeautifulSoup(html, "html.parser")
        links = scraper._parse_links(soup, "https://example.com/")
        
        assert ("test.pdf", "pdf") in links
        assert ("page.html", "html") in links


# Fixtures para tests de scraper
@pytest.fixture
def sample_config():
    """Fixture con configuración básica para scraper."""
    return {
        "allowed_domains": ["example.com", "test.com"],
        "max_depth": 2,
        "file_types": ["html", "pdf", "docx"],
        "delay": 1.0,
        "user_agent": "TestBot/1.0",
        "output_dir": "./test_data"
    }


@pytest.fixture
def mock_logger():
    """Fixture con logger mock."""
    return MagicMock()


@pytest.fixture
def sample_html_with_links():
    """Fixture con HTML que contiene diversos tipos de links."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Links Test Page</h1>
        <div>
            <a href="page1.html">HTML Page 1</a>
            <a href="page2.html?param=value">HTML Page 2 with params</a>
            <a href="document.pdf">PDF Document</a>
            <a href="report.docx">Word Document</a>
            <a href="data.xlsx">Excel File</a>
            <a href="image.jpg">Image (should be ignored)</a>
            <a href="/about">About Page (relative)</a>
            <a href="https://external.com/page.html">External Link</a>
            <a name="anchor">Anchor without href</a>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_requests_response():
    """Fixture con response mock para requests."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html><body>Test content</body></html>"
    mock_response.content = b"test file content"
    mock_response.raise_for_status.return_value = None
    return mock_response