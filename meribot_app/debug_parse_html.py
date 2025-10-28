"""
Script de debug para verificar qué pasa con parse_html
"""
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar meribot
sys.path.append(str(Path(__file__).parent))

from meribot.crawler.document_loader import parse_html
import requests

def debug_parse_html():
    """
    Debug del problema con parse_html
    """
    url = "https://cca.capgemini.com/web/home"
    
    print("=== Debug parse_html ===\n")
    
    try:
        # Obtener HTML
        resp = requests.get(url, headers={"User-Agent": "MeriBot/1.0"}, timeout=10, verify=False)
        resp.raise_for_status()
        
        html_content = resp.text
        print(f"HTML obtenido: {len(html_content)} caracteres")
        print(f"Primeros 500 caracteres del HTML:")
        print(html_content[:500])
        print()
        
        # Parsear HTML
        parsed_text = parse_html(html_content)
        print(f"Texto parseado: {len(parsed_text)} caracteres")
        print(f"Texto parseado completo: '{parsed_text}'")
        print()
        
        # Verificar si hay contenido en tags específicos
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar elementos comunes
        title = soup.find('title')
        body = soup.find('body')
        main = soup.find('main')
        divs = soup.find_all('div')
        
        print(f"Title encontrado: {title.get_text() if title else 'No'}")
        print(f"Body encontrado: {'Sí' if body else 'No'}")
        print(f"Main encontrado: {'Sí' if main else 'No'}")
        print(f"Divs encontrados: {len(divs)}")
        
        if body:
            body_text = body.get_text().strip()
            print(f"Texto en body: {len(body_text)} caracteres")
            print(f"Primeros 200 caracteres del body: '{body_text[:200]}'")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_parse_html()