"""
Test directo del PDF para verificar que el scraper puede manejarlo
"""
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent))

from meribot.crawler.config import load_yaml_config, validate_config
from meribot.crawler.spa_scraper import SPAWebScraper
from meribot.utils.logging import get_logger

def test_direct_pdf_download():
    """
    Prueba directa del PDF que mencionaste
    """
    print("=== Test Descarga Directa del PDF ===\n")
    
    pdf_url = "https://cca.capgemini.com/media/assets/Onboarding_CCA_HRBP.pdf"
    
    # Cargar configuración
    config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
    config = load_yaml_config(config_path)
    validate_config(config)
    
    # Configurar para SPA
    config["allowed_domains"] = ["cca.capgemini.com"]
    config["spa_support"] = True
    config["output_dir"] = "./data/scraped"
    
    # Crear scraper SPA
    logger = get_logger("TestDirectPDFDownload")
    scraper = SPAWebScraper(config, logger=logger)
    
    try:
        print(f"Probando descarga directa del PDF: {pdf_url}")
        
        # Intentar descargar el PDF directamente
        scraper.download_file(pdf_url)
        
        # Verificar si se descargó
        local_path = scraper._get_local_path(pdf_url, "pdf")
        url_path = local_path + ".url"
        
        print(f"Archivo local esperado: {local_path}")
        
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            print(f"✅ PDF descargado exitosamente: {size} bytes")
        else:
            print(f"❌ PDF NO se descargó en la ruta esperada")
        
        if os.path.exists(url_path):
            with open(url_path, 'r') as f:
                url_content = f.read().strip()
            print(f"✅ Archivo .url creado: {url_content}")
        else:
            print(f"❌ Archivo .url NO creado")
            
    except Exception as e:
        print(f"Error durante la descarga: {e}")
        logger.error(f"Error durante la descarga: {e}")
        
    finally:
        # Cerrar driver si se inicializó
        if hasattr(scraper, '_close_selenium_driver'):
            scraper._close_selenium_driver()
    
    print("\n=== Test Completado ===")

if __name__ == "__main__":
    test_direct_pdf_download()