from .document_loader import parse_html, parse_docx, parse_xlsx, parse_pdf
"""
Módulo base de descubrimiento de URLs y documentos para el Crawler de Meri-bot.
Utiliza configuración y logging estructurado.
"""
import os
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from .config import get_config, load_yaml_config, validate_config, ConfigError
from .logger import get_logger


class WebScraper:
    """
    WebScraper realiza crawling web real a partir de seeds, respetando dominios y profundidad.
    Detecta enlaces a HTML, PDF, DOCX, XLSX y registra hallazgos en logs estructurados.
    """
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or get_logger("WebScraper")
        self.allowed_domains = set(self.config["allowed_domains"])
        self.max_depth = self.config.get("max_depth", 2)
        self.file_types = set(self.config.get("file_types", ["html", "pdf", "docx", "xlsx"]))
        self.visited = set()
        self.delay = float(self.config.get("delay", 1.0))
        self.user_agent = self.config.get("user_agent", "MeriBot/1.0")

    def crawl_url(self, url, depth=0):
        if depth > self.max_depth:
            self.logger.info(f"Profundidad máxima alcanzada: {depth} en {url}")
            return
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain not in self.allowed_domains:
            self.logger.info(f"Dominio no permitido: {domain} ({url})")
            return
        if url in self.visited:
            return
        self.visited.add(url)
        self.logger.info(f"Visitando: {url} (profundidad {depth})")
        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "").lower()
            if "html" in content_type:
                soup = BeautifulSoup(resp.text, "html.parser")
                links = self._parse_links(soup, url)
                self.logger.info(f"Enlaces encontrados: {len(links)} en {url}")
                for link, ext in links:
                    abs_url = urljoin(url, link)
                    if ext == "html":
                        time.sleep(self.delay)
                        self.crawl_url(abs_url, depth + 1)
                    elif ext in self.file_types:
                        self.logger.info(f"Documento detectado: {abs_url} (tipo: {ext})")
            else:
                # Documento soportado
                ext = url.split(".")[-1].lower()
                if ext in self.file_types:
                    self.logger.info(f"Documento detectado: {url} (tipo: {ext})")
        except Exception as e:
            self.logger.error(f"Error procesando {url}: {e}")

    def _parse_links(self, soup, base_url):
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?")[0].split("#")[0]
            ext = href.split(".")[-1].lower()
            if ext in self.file_types:
                links.append((href, ext))
            elif ext == "html" or not ext:
                links.append((href, "html"))
        return links





if __name__ == "__main__":
    # Validación de configuración al inicio
    try:
        config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "..", "crawler_config.yaml")
        config = load_yaml_config(config_path)
        validate_config(config)
    except ConfigError as e:
        print(f"[ERROR] Configuración inválida: {e}")
        exit(1)
    except Exception as ex:
        print(f"[ERROR] Error inesperado al validar configuración: {ex}")
        exit(1)

    # Inicializar logger estructurado con el nivel de la configuración YAML
    log_level = config.get("log_level", "INFO")
    logger = get_logger("WebScraper", level=log_level)
    logger.info("[OK] Configuración válida y logger inicializado.")

    # Iniciar crawling sobre archivo HTML local proporcionado
    local_html = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Local_C&CA_host_web", "Cloud & Custom Applications.html"))
    if not os.path.exists(local_html):
        logger.error(f"No se encontró el archivo local: {local_html}")
    else:
        # Usar el método scrape local para archivos
        class LocalFileScraper(WebScraper):
            def crawl_url(self, file_path, depth=0):
                if depth > self.max_depth:
                    self.logger.info(f"Profundidad máxima alcanzada: {depth} en {file_path}")
                    return
                if file_path in self.visited:
                    return
                self.visited.add(file_path)
                self.logger.info(f"Procesando archivo local: {file_path} (profundidad {depth})")
                try:
                    ext = file_path.split(".")[-1].lower()
                    if ext == "html":
                        with open(file_path, "r", encoding="utf-8") as f:
                            html = f.read()
                        # Parsear HTML y loguear resumen
                        try:
                            result = parse_html(html)
                            resumen = result["text"][:120].replace("\n", " ") + ("..." if len(result["text"]) > 120 else "")
                            self.logger.info(f"[PARSE HTML] {file_path} | Título: {result['metadata'].get('title')} | Resumen: {resumen}")
                        except Exception as e:
                            self.logger.error(f"Error parseando HTML {file_path}: {e}")
                        soup = BeautifulSoup(html, "html.parser")
                        links = self._parse_links(soup, file_path)
                        self.logger.info(f"Enlaces encontrados: {len(links)} en {file_path}")
                        for link, ext2 in links:
                            next_path = os.path.normpath(os.path.join(os.path.dirname(file_path), link))
                            if ext2 == "html" and os.path.exists(next_path):
                                time.sleep(self.delay)
                                self.crawl_url(next_path, depth + 1)
                            elif ext2 in self.file_types:
                                self._parse_and_log_doc(next_path, ext2)
                    elif ext in self.file_types:
                        self._parse_and_log_doc(file_path, ext)
                except Exception as e:
                    self.logger.error(f"Error procesando {file_path}: {e}")

            def _parse_and_log_doc(self, path, ext):
                if not os.path.exists(path):
                    self.logger.warning(f"No se puede parsear {ext.upper()} {path}: archivo no encontrado (probablemente es un enlace externo o no descargado)")
                    return
                try:
                    if ext == "pdf":
                        result = parse_pdf(path)
                        resumen = result["text"][:120].replace("\n", " ") + ("..." if len(result["text"]) > 120 else "")
                        self.logger.info(f"[PARSE PDF] {path} | Metadatos: {result['metadata']} | Resumen: {resumen}")
                    elif ext == "docx":
                        result = parse_docx(path)
                        resumen = result["text"][:120].replace("\n", " ") + ("..." if len(result["text"]) > 120 else "")
                        self.logger.info(f"[PARSE DOCX] {path} | Metadatos: {result['metadata']} | Resumen: {resumen}")
                    elif ext == "xlsx":
                        result = parse_xlsx(path)
                        resumen = result["text"][:120].replace("\n", " ") + ("..." if len(result["text"]) > 120 else "")
                        self.logger.info(f"[PARSE XLSX] {path} | Metadatos: {result['metadata']} | Resumen: {resumen}")
                    else:
                        self.logger.info(f"Documento detectado (sin parser): {path} (tipo: {ext})")
                except Exception as e:
                    self.logger.error(f"Error parseando {ext.upper()} {path}: {e}")

        scraper = LocalFileScraper(config, logger=logger)
        scraper.crawl_url(local_html, depth=0)
        logger.info("Crawling local finalizado. Verifica los logs para el resultado del descubrimiento de enlaces y documentos.")
