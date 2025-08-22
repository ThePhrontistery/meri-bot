"""
Módulo base de descubrimiento de URLs y documentos para el Crawler de Meri-bot.
Utiliza configuración y logging estructurado.
"""
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from .config import get_config
from .logger import get_logger

class WebScraper:
    def __init__(self, base_path: str):
        self.config = get_config()
        self.logger = get_logger("WebScraper")
        self.base_path = base_path
        self.allowed_domains = set(self.config["allowed_domains"])
        self.max_depth = self.config.get("max_depth", 2)
        self.file_types = set(self.config.get("file_types", ["html", "pdf", "docx", "xlsx"]))
        self.visited = set()
        self.delay = float(self.config.get("delay", 1.0))

    def scrape(self, start_file: str = None, depth: int = 0):
        if depth > self.max_depth:
            self.logger.info(f"Profundidad máxima alcanzada: {depth}")
            return
        file_path = start_file or self.base_path
        if file_path in self.visited:
            return
        self.visited.add(file_path)
        self.logger.info(f"Procesando archivo: {file_path} (profundidad {depth})")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html = f.read()
            soup = BeautifulSoup(html, "html.parser")
            links = self._parse_links(soup, file_path)
            self.logger.info(f"Enlaces encontrados: {len(links)}")
            for link, ext in links:
                if ext == "html":
                    next_path = os.path.normpath(os.path.join(os.path.dirname(file_path), link))
                    if os.path.exists(next_path):
                        time.sleep(self.delay)
                        self.scrape(next_path, depth + 1)
                else:
                    self.logger.info(f"Documento detectado: {link} (tipo: {ext})")
        except Exception as e:
            self.logger.error(f"Error procesando {file_path}: {e}")

    def _parse_links(self, soup, current_file):
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?")[0].split("#")[0]
            ext = href.split(".")[-1].lower()
            if ext in self.file_types:
                links.append((href, ext))
        return links

if __name__ == "__main__":
    # Prueba local con el archivo HTML proporcionado (ruta corregida)
    base_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "Local_C&CA_host_web", "Cloud & Custom Applications.html"
        )
    )
    if not os.path.exists(base_file):
        print(f"[ERROR] No se encontró el archivo: {base_file}")
    else:
        scraper = WebScraper(base_file)
        scraper.scrape()
        print("\nVerifica los logs para el resultado del descubrimiento de enlaces y documentos.\n")
