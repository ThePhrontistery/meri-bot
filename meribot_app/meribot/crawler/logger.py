"""
Módulo de logging estructurado para el Crawler de Meri-bot.
Permite logs a consola y archivo, configurable por nivel y formato.
Compatible con Rich si está instalado.
"""
import os
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from typing import Optional

try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'crawler.log')

DEFAULT_LEVEL = os.environ.get("CRAWLER_LOG_LEVEL", "INFO").upper()

LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: Optional[str] = None) -> Logger:
    ensure_log_dir()
    logger = logging.getLogger(name or "crawler")
    if logger.hasHandlers():
        return logger  # Evita duplicar handlers
    level = LEVELS.get(DEFAULT_LEVEL, logging.INFO)
    logger.setLevel(level)

    # Formato estructurado
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = logging.Formatter(fmt)

    # Handler para archivo
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    if RICH_AVAILABLE:
        console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.propagate = False
    return logger

if __name__ == "__main__":
    logger = get_logger("test")
    logger.debug("Mensaje DEBUG de prueba")
    logger.info("Mensaje INFO de prueba")
    logger.warning("Mensaje WARNING de prueba")
    logger.error("Mensaje ERROR de prueba")
    logger.critical("Mensaje CRITICAL de prueba")
    print("\nVerifica la salida en consola y en logs/crawler.log\n")
