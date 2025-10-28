"""
Script de prueba para verificar el funcionamiento del SPAWebScraper
con la página de Capgemini que sabemos que es una SPA.
"""
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar meribot
sys.path.append(str(Path(__file__).parent))

from meribot.crawler.config import load_yaml_config, validate_config
from meribot.crawler.spa_scraper import SPAWebScraper
from meribot.utils.logging import get_logger

def test_spa_scraper():
    """
    Prueba el SPAWebScraper con la URL de Capgemini
    """
    print("=== Test SPAWebScraper ===")
    
    # Cargar configuración
    config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
    config = load_yaml_config(config_path)
    validate_config(config)
    
    # Configurar para prueba específica
    config["seeds"] = ["https://cca.capgemini.com/web/home"]
    config["allowed_domains"] = ["cca.capgemini.com"]  # Dominio completo
    config["max_depth"] = 1  # Solo un nivel para prueba
    config["spa_support"] = True
    config["headless"] = True  # Sin interfaz gráfica
    config["selenium_timeout"] = 15
    config["selenium_delay"] = 3
    
    # Crear logger
    logger = get_logger("TestSPAWebScraper")
    
    # Crear scraper SPA
    scraper = SPAWebScraper(config, logger=logger)
    
    try:
        print(f"Probando crawling de: {config['seeds'][0]}")
        scraper.crawl_url(config["seeds"][0], depth=0)
        
        print("\n=== Resultados ===")
        print(f"URLs visitadas: {len(scraper.visited)}")
        for url in scraper.visited:
            print(f"  - {url}")
            
        # Verificar archivos guardados
        output_dir = config.get("output_dir", "./data/scraped")
        print(f"\nArchivos guardados en: {output_dir}")
        
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, output_dir)
                    size = os.path.getsize(file_path)
                    print(f"  - {rel_path} ({size} bytes)")
                    
        print("\n=== Test Completado ===")
        
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        logger.error(f"Error durante la prueba: {e}")
        
    finally:
        # Cerrar driver
        scraper._close_selenium_driver()

if __name__ == "__main__":
    test_spa_scraper()