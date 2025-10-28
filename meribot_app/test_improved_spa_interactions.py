"""
Test del scraper mejorado con interacciones para detectar el PDF
"""
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent))

from meribot.crawler.config import load_yaml_config, validate_config
from meribot.crawler.spa_scraper import SPAWebScraper
from meribot.utils.logging import get_logger
from bs4 import BeautifulSoup

def test_improved_spa_interactions():
    """
    Prueba el scraper mejorado con interacciones
    """
    print("=== Test Scraper SPA Mejorado con Interacciones ===\n")
    
    url = "https://cca.capgemini.com/web/onboarding"
    
    # Cargar configuración
    config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
    config = load_yaml_config(config_path)
    validate_config(config)
    
    # Configurar para SPA con más tiempo
    config["allowed_domains"] = ["cca.capgemini.com"]
    config["spa_support"] = True
    config["headless"] = True  # Cambiar a False si quieres ver el navegador
    config["selenium_timeout"] = 25  # Más tiempo
    config["selenium_delay"] = 5     # Más delay inicial
    
    # Crear scraper SPA
    logger = get_logger("TestImprovedSPAInteractions")
    scraper = SPAWebScraper(config, logger=logger)
    
    try:
        print(f"Probando URL: {url}")
        print("Configuración:")
        print(f"  - Headless: {config['headless']}")
        print(f"  - Timeout: {config['selenium_timeout']}s")
        print(f"  - Delay inicial: {config['selenium_delay']}s")
        print()
        
        # Obtener contenido con interacciones
        print("Obteniendo contenido con interacciones mejoradas...")
        rendered_html = scraper._get_page_content_with_selenium(url)
        
        if rendered_html:
            soup = BeautifulSoup(rendered_html, "html.parser")
            
            print(f"HTML renderizado: {len(rendered_html)} caracteres")
            
            # Buscar todos los enlaces
            all_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href and not href.startswith("#"):
                    all_links.append(href)
            
            print(f"Enlaces únicos encontrados: {len(set(all_links))}")
            
            # Mostrar todos los enlaces únicos
            unique_links = sorted(set(all_links))
            for i, link in enumerate(unique_links):
                print(f"  {i+1}. {link}")
            
            print()
            
            # Buscar específicamente PDFs
            pdf_links = []
            for link in unique_links:
                if ".pdf" in link.lower():
                    pdf_links.append(link)
            
            print(f"Enlaces PDF encontrados: {len(pdf_links)}")
            for pdf in pdf_links:
                print(f"  📄 {pdf}")
            
            # Buscar texto relacionado con PDF o documentos
            text_content = soup.get_text().lower()
            pdf_related_words = ["pdf", "document", "download", "archivo", "descargar", "onboarding"]
            
            print()
            print("Búsqueda de palabras relacionadas con documentos:")
            for word in pdf_related_words:
                if word in text_content:
                    print(f"  ✅ '{word}' encontrado en el contenido")
                    # Mostrar contexto
                    import re
                    contexts = re.findall(f'.{{0,50}}{word}.{{0,50}}', text_content, re.IGNORECASE)
                    for ctx in contexts[:2]:  # Primeros 2 contextos
                        print(f"     Contexto: ...{ctx}...")
                else:
                    print(f"  ❌ '{word}' NO encontrado")
            
            # Buscar el PDF específico esperado
            print()
            expected_pdf = "Onboarding_CCA_HRBP.pdf"
            if expected_pdf.lower() in text_content:
                print(f"✅ PDF específico '{expected_pdf}' encontrado en el contenido!")
            else:
                print(f"❌ PDF específico '{expected_pdf}' NO encontrado")
            
            # Verificar si hay elementos que podrían contener enlaces dinámicos
            dynamic_elements = soup.find_all(["div", "span"], {"data-": True}) + \
                             soup.find_all(class_=lambda x: x and "load" in str(x).lower())
            
            print()
            print(f"Elementos potencialmente dinámicos: {len(dynamic_elements)}")
            for i, elem in enumerate(dynamic_elements[:5]):
                attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-') or 'class' in k}
                print(f"  {i+1}. {elem.name}: {attrs}")
        
        else:
            print("❌ No se pudo obtener contenido con Selenium")
            
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        logger.error(f"Error durante la prueba: {e}")
        
    finally:
        # Cerrar driver
        scraper._close_selenium_driver()
    
    print("\n=== Test Completado ===")

if __name__ == "__main__":
    test_improved_spa_interactions()