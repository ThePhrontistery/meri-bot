"""
Script para debuggear por qué no se está detectando el PDF en la página de onboarding
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
import requests

def debug_onboarding_links():
    """
    Debuggea la detección de enlaces en la página de onboarding
    """
    print("=== Debug de Enlaces en Onboarding ===\n")
    
    url = "https://cca.capgemini.com/web/onboarding"
    
    # Cargar configuración
    config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
    config = load_yaml_config(config_path)
    validate_config(config)
    
    # Configurar para SPA
    config["allowed_domains"] = ["cca.capgemini.com"]
    config["spa_support"] = True
    config["headless"] = False  # Mostrar navegador para debug
    config["selenium_timeout"] = 20  # Más tiempo
    config["selenium_delay"] = 5     # Más delay
    
    # Crear scraper SPA
    logger = get_logger("DebugOnboardingLinks")
    scraper = SPAWebScraper(config, logger=logger)
    
    try:
        print("1. Método tradicional (requests + BeautifulSoup):")
        # Primero probar método tradicional
        resp = requests.get(url, headers={"User-Agent": "MeriBot/1.0"}, timeout=10, verify=False)
        resp.raise_for_status()
        
        soup_traditional = BeautifulSoup(resp.text, "html.parser")
        traditional_links = scraper._parse_links(soup_traditional, url)
        
        print(f"   - HTML estático: {len(resp.text)} caracteres")
        print(f"   - Enlaces encontrados: {len(traditional_links)}")
        for i, (link, ext) in enumerate(traditional_links[:10]):  # Primeros 10
            print(f"     {i+1}. {link} ({ext})")
        
        # Buscar específicamente el PDF en HTML estático
        pdf_links_static = []
        for a in soup_traditional.find_all("a", href=True):
            href = a["href"]
            if ".pdf" in href.lower():
                pdf_links_static.append(href)
        
        print(f"   - Enlaces PDF en HTML estático: {len(pdf_links_static)}")
        for pdf in pdf_links_static:
            print(f"     PDF: {pdf}")
        
        print()
        
        print("2. Método SPA (Selenium + JavaScript):")
        # Ahora con Selenium
        rendered_html = scraper._get_page_content_with_selenium(url)
        
        if rendered_html:
            soup_spa = BeautifulSoup(rendered_html, "html.parser")
            spa_links = scraper._parse_links(soup_spa, url)
            
            print(f"   - HTML renderizado: {len(rendered_html)} caracteres")
            print(f"   - Enlaces encontrados: {len(spa_links)}")
            for i, (link, ext) in enumerate(spa_links[:10]):  # Primeros 10
                print(f"     {i+1}. {link} ({ext})")
            
            # Buscar específicamente el PDF en HTML renderizado
            pdf_links_spa = []
            for a in soup_spa.find_all("a", href=True):
                href = a["href"]
                if ".pdf" in href.lower():
                    pdf_links_spa.append(href)
            
            print(f"   - Enlaces PDF en HTML renderizado: {len(pdf_links_spa)}")
            for pdf in pdf_links_spa:
                print(f"     PDF: {pdf}")
            
            # Buscar texto que contenga "pdf" (case insensitive)
            text_content = soup_spa.get_text().lower()
            if "pdf" in text_content:
                print(f"   - La palabra 'PDF' aparece en el contenido")
                # Buscar contexto alrededor de PDF
                import re
                pdf_contexts = re.findall(r'.{0,50}pdf.{0,50}', text_content, re.IGNORECASE)
                for i, context in enumerate(pdf_contexts[:5]):  # Primeros 5 contextos
                    print(f"     Contexto {i+1}: ...{context}...")
            else:
                print(f"   - La palabra 'PDF' NO aparece en el contenido")
            
            # Buscar todos los enlaces únicos
            all_links = set()
            for a in soup_spa.find_all("a", href=True):
                href = a["href"].strip()
                if href and not href.startswith("#"):
                    all_links.add(href)
            
            print(f"   - Total enlaces únicos encontrados: {len(all_links)}")
            for i, link in enumerate(sorted(all_links)[:20]):  # Primeros 20
                print(f"     {i+1}. {link}")
        
        print()
        
        print("3. Análisis de diferencias:")
        if rendered_html:
            diff_chars = len(rendered_html) - len(resp.text)
            print(f"   - Diferencia en tamaño: +{diff_chars} caracteres")
            print(f"   - Diferencia en enlaces: {len(spa_links) - len(traditional_links)} enlaces adicionales")
        
        print("\n4. Búsqueda específica del PDF esperado:")
        expected_pdf = "https://cca.capgemini.com/media/assets/Onboarding_CCA_HRBP.pdf"
        
        # Buscar en HTML estático
        if expected_pdf in resp.text:
            print(f"   ✅ PDF encontrado en HTML estático")
        else:
            print(f"   ❌ PDF NO encontrado en HTML estático")
        
        # Buscar en HTML renderizado
        if rendered_html and expected_pdf in rendered_html:
            print(f"   ✅ PDF encontrado en HTML renderizado")
        else:
            print(f"   ❌ PDF NO encontrado en HTML renderizado")
        
        # Buscar partes del PDF
        pdf_parts = ["Onboarding_CCA_HRBP", "media/assets", ".pdf"]
        for part in pdf_parts:
            static_found = part in resp.text
            spa_found = rendered_html and part in rendered_html
            print(f"   - '{part}': Estático={static_found}, SPA={spa_found}")
            
    except Exception as e:
        print(f"Error durante el debug: {e}")
        logger.error(f"Error durante el debug: {e}")
        
    finally:
        # Cerrar driver
        scraper._close_selenium_driver()
    
    print("\n=== Debug Completado ===")

if __name__ == "__main__":
    debug_onboarding_links()