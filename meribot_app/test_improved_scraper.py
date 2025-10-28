"""
Script de prueba simple para el scraper mejorado con SPA
"""
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent))

from meribot.crawler.config import load_yaml_config, validate_config
from meribot.crawler.scraper import create_scraper
from meribot.utils.logging import get_logger

def test_improved_scraper():
    """
    Prueba el scraper mejorado con soporte SPA
    """
    print("=== Test Scraper Mejorado con SPA ===\n")
    
    # Cargar configuración
    config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
    config = load_yaml_config(config_path)
    validate_config(config)
    
    print(f"Configuración cargada:")
    print(f"  - SPA Support: {config.get('spa_support', False)}")
    print(f"  - Seeds: {config.get('seeds', [])}")
    print(f"  - Dominios permitidos: {config.get('allowed_domains', [])}")
    print()
    
    # Crear logger
    logger = get_logger("TestImprovedScraper")
    
    # Crear scraper usando factory function (automáticamente elige SPA si está habilitado)
    scraper = create_scraper(config, logger=logger)
    
    print(f"Scraper creado: {type(scraper).__name__}")
    print()
    
    try:
        # Procesar todas las URLs seeds
        seeds = config.get("seeds", [])
        for url in seeds:
            print(f"Procesando: {url}")
            scraper.crawl_url(url, depth=0)
            
        print(f"\nProcesamiento completado.")
        print(f"URLs visitadas: {len(scraper.visited)}")
        
        for url in scraper.visited:
            print(f"  ✓ {url}")
            
        # Verificar archivos guardados
        output_dir = config.get("output_dir", "./data/scraped")
        if os.path.exists(output_dir):
            print(f"\nArchivos guardados en: {output_dir}")
            file_count = 0
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, output_dir)
                    size = os.path.getsize(file_path)
                    print(f"  📄 {rel_path} ({size} bytes)")
                    file_count += 1
            print(f"\nTotal: {file_count} archivos guardados")
        
    except Exception as e:
        print(f"Error durante el crawling: {e}")
        logger.error(f"Error durante el crawling: {e}")
        
    finally:
        # Cerrar recursos si es necesario
        if hasattr(scraper, '_close_selenium_driver'):
            scraper._close_selenium_driver()
            print("\nDriver Selenium cerrado correctamente")
    
    print("\n=== Test Completado ===")

if __name__ == "__main__":
    test_improved_scraper()