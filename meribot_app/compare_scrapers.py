"""
Script de comparación entre WebScraper tradicional y SPAWebScraper
para demostrar la mejora en el manejo de SPAs.
"""
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar meribot
sys.path.append(str(Path(__file__).parent))

from meribot.crawler.config import load_yaml_config, validate_config
from meribot.crawler.scraper import WebScraper
from meribot.crawler.spa_scraper import SPAWebScraper
from meribot.crawler.document_loader import parse_html
from meribot.utils.logging import get_logger
import requests

def compare_scrapers():
    """
    Compara el contenido obtenido por WebScraper tradicional vs SPAWebScraper
    """
    print("=== Comparación WebScraper vs SPAWebScraper ===\n")
    
    url = "https://cca.capgemini.com/web/home"
    
    # 1. Método tradicional (requests + BeautifulSoup)
    print("1. Método tradicional (requests + BeautifulSoup):")
    try:
        resp = requests.get(url, headers={"User-Agent": "MeriBot/1.0"}, timeout=10, verify=False)
        resp.raise_for_status()
        
        traditional_html = resp.text
        traditional_result = parse_html(traditional_html)
        traditional_parsed = traditional_result.get('text', '') if isinstance(traditional_result, dict) else str(traditional_result)
        
        print(f"   - HTML crudo: {len(traditional_html)} caracteres")
        print(f"   - Texto extraído: {len(traditional_parsed)} caracteres") 
        print(f"   - Contenido: '{traditional_parsed[:100]}...'")
        
    except Exception as e:
        print(f"   Error: {e}")
        traditional_html = ""
        traditional_parsed = ""
    
    print()
    
    # 2. Método SPA (Selenium + rendering JavaScript)
    print("2. Método SPA (Selenium + rendering JavaScript):")
    
    # Cargar configuración
    config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
    config = load_yaml_config(config_path)
    validate_config(config)
    
    # Configurar para SPA
    config["allowed_domains"] = ["cca.capgemini.com"]
    config["spa_support"] = True
    config["headless"] = True
    config["selenium_timeout"] = 15
    config["selenium_delay"] = 3
    
    # Crear scraper SPA
    logger = get_logger("CompareScraper")
    scraper = SPAWebScraper(config, logger=logger)
    
    try:
        spa_html = scraper._get_page_content_with_selenium(url)
        if spa_html:
            spa_result = parse_html(spa_html)
            spa_parsed = spa_result.get('text', '') if isinstance(spa_result, dict) else str(spa_result)
            
            print(f"   - HTML renderizado: {len(spa_html)} caracteres")
            print(f"   - Texto extraído: {len(spa_parsed)} caracteres")
            print(f"   - Contenido: '{spa_parsed[:100]}...'")
        else:
            print("   Error: No se pudo obtener contenido con Selenium")
            spa_html = ""
            spa_parsed = ""
            
    except Exception as e:
        print(f"   Error: {e}")
        spa_html = ""
        spa_parsed = ""
    finally:
        scraper._close_selenium_driver()
    
    print()
    
    # 3. Comparación de resultados
    print("3. Comparación de resultados:")
    traditional_len = len(traditional_parsed) if traditional_parsed else 0
    spa_len = len(spa_parsed) if spa_parsed else 0
    
    if spa_len > 0:
        if traditional_len > 0:
            improvement_ratio = spa_len / traditional_len
            print(f"   - Mejora en texto extraído: {improvement_ratio:.1f}x más contenido")
        else:
            print(f"   - Mejora en texto extraído: ∞ (de 0 a {spa_len} caracteres)")
        
        print(f"   - Diferencia en caracteres: +{spa_len - traditional_len}")
        
        # Análisis del contenido
        traditional_words = len(traditional_parsed.split()) if traditional_parsed else 0
        spa_words = len(spa_parsed.split()) if spa_parsed else 0
        print(f"   - Palabras (tradicional): {traditional_words}")
        print(f"   - Palabras (SPA): {spa_words}")
        
        if traditional_words > 0:
            print(f"   - Mejora en palabras: {spa_words / traditional_words:.1f}x")
        else:
            print(f"   - Mejora en palabras: ∞ (de 0 a {spa_words} palabras)")
        
        # Mostrar ejemplos del contenido extraído con SPA
        print(f"\n4. Contenido extraído con SPA:")
        content_sample = spa_parsed[:300] if len(spa_parsed) > 300 else spa_parsed
        print(f"   '{content_sample}{'...' if len(spa_parsed) > 300 else ''}'")
    else:
        print("   No se pudo extraer contenido con ningún método")
    
    print("\n=== Fin de la comparación ===")

if __name__ == "__main__":
    compare_scrapers()