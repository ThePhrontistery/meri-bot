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
    def _get_local_path(self, url, ext):
        """
        Construye la ruta local para guardar el archivo basado en output_dir, dominio y path.
        """
        from pathlib import Path
        output_dir = self.config.get("output_dir", "./data/scraped")
        parsed = urlparse(url)
        domain = parsed.netloc.replace(":", "_")
        path = parsed.path.lstrip("/").replace("/", os.sep)
        if not path or path.endswith("/"):
            path += "index.{}".format(ext)
        local_path = os.path.join(output_dir, domain, path)
        Path(os.path.dirname(local_path)).mkdir(parents=True, exist_ok=True)
        return local_path

    def save_html(self, url, html):
        """
        Guarda el HTML de la página en la ruta local correspondiente.
        """
        local_path = self._get_local_path(url, "html")
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(html)
            self.logger.info(f"[GUARDADO HTML] {local_path}")
        except Exception as e:
            self.logger.error(f"Error guardando HTML {local_path}: {e}")

    def download_file(self, url):
        """
        Descarga un archivo adjunto y lo guarda en la ruta local correspondiente.
        """
        local_path = self._get_local_path(url, url.split(".")[-1].lower())
        try:
            resp = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=20, verify=False)
            resp.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(resp.content)
            self.logger.info(f"[DESCARGADO] {local_path}")
        except Exception as e:
            self.logger.error(f"Error descargando archivo {url}: {e}")
    """
    WebScraper realiza crawling web real a partir de seeds, respetando dominios y profundidad.
    Detecta enlaces a HTML, PDF, DOCX, XLSX y registra hallazgos en logs estructurados.
    """
    def __init__(self, config, logger=None):
        """
        Inicializa el WebScraper con la configuración y el logger proporcionados.
        Args:
            config (dict): Configuración del crawler (dominios, profundidad, tipos de archivo, etc.)
            logger (Logger, opcional): Logger estructurado. Si no se proporciona, se crea uno por defecto.
        """
        self.config = config
        self.logger = logger or get_logger("WebScraper")
        self.allowed_domains = set(self.config["allowed_domains"])
        self.max_depth = self.config.get("max_depth", 2)
        self.file_types = set(self.config.get("file_types", ["html", "pdf", "docx", "xlsx"]))
        self.visited = set()
        self.delay = float(self.config.get("delay", 1.0))
        self.user_agent = self.config.get("user_agent", "MeriBot/1.0")

    def crawl_url(self, url, depth=0):
        """
        Realiza el crawling recursivo sobre una URL, respetando la profundidad máxima y dominios permitidos.
        Detecta y procesa enlaces a documentos soportados y HTML.
        Args:
            url (str): URL a visitar.
            depth (int): Profundidad actual del crawling.
        """
        if depth > self.max_depth:
            self.logger.info(f"Profundidad máxima alcanzada: {depth} en {url}")
            print
            return
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain not in self.allowed_domains:
            print("Dominio no permitido:", domain, "(", url, ")")
            self.logger.info(f"Dominio no permitido: {domain} ({url})")
            return
        if url in self.visited:
            return
        self.visited.add(url)
        self.logger.info(f"Visitando: {url} (profundidad {depth})")
        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "").lower()
            if "html" in content_type:
                print("Procesando HTML:", url)
                self.save_html(url, resp.text)
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
                        self.download_file(abs_url)
            else:
                # Documento soportado
                print("Procesando documento:", url)
                ext = url.split(".")[-1].lower()
                if ext in self.file_types:
                    self.logger.info(f"Documento detectado: {url} (tipo: {ext})")
                    self.download_file(url)
        except Exception as e:
            self.logger.error(f"Error procesando {url}: {e}")

    def _parse_links(self, soup, base_url):
        """
        Extrae y clasifica los enlaces de un documento HTML.
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup del HTML.
            base_url (str): URL base para resolver rutas relativas.
        Returns:
            list: Lista de tuplas (href, ext) con enlaces y su tipo de archivo.
        """
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

    # Iniciar crawling sobre las URLs definidas en seeds
    seeds = config.get("seeds", [])
    if not seeds:
        logger.error("No se encontraron URLs en 'seeds' para iniciar el crawling.")
        exit(1)
    scraper = WebScraper(config, logger=logger)
    for url in seeds:
        scraper.crawl_url(url, depth=0)
    logger.info("Crawling web finalizado. Verifica los logs para el resultado del descubrimiento de enlaces y documentos.")
