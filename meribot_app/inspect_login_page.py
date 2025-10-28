#!/usr/bin/env python3
"""
Script para inspeccionar los campos de login de la página web.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def inspect_login_page():
    """Inspecciona la página de login para encontrar los selectores correctos."""
    
    print("🔍 Inspeccionando página de login...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Inicializar driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navegar a la página de login
        login_url = "https://cca.capgemini.com/web/home"
        print(f"Navegando a: {login_url}")
        driver.get(login_url)
        
        # Esperar a que la página se cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("Página cargada. Esperando 5 segundos para contenido dinámico...")
        time.sleep(5)
        
        # Buscar todos los campos de input
        print("\n📝 Campos de input encontrados:")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, input_elem in enumerate(inputs):
            try:
                input_type = input_elem.get_attribute("type") or "text"
                input_name = input_elem.get_attribute("name") or "sin_nombre"
                input_id = input_elem.get_attribute("id") or "sin_id"
                input_class = input_elem.get_attribute("class") or "sin_class"
                placeholder = input_elem.get_attribute("placeholder") or "sin_placeholder"
                
                print(f"  Input {i+1}:")
                print(f"    - Tipo: {input_type}")
                print(f"    - Name: {input_name}")
                print(f"    - ID: {input_id}")
                print(f"    - Class: {input_class}")
                print(f"    - Placeholder: {placeholder}")
                print(f"    - Visible: {input_elem.is_displayed()}")
                print()
            except Exception as e:
                print(f"    - Error obteniendo información: {e}")
        
        # Buscar botones
        print("\n🔘 Botones encontrados:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, button in enumerate(buttons):
            try:
                button_type = button.get_attribute("type") or "button"
                button_text = button.text or "sin_texto"
                button_class = button.get_attribute("class") or "sin_class"
                button_id = button.get_attribute("id") or "sin_id"
                
                print(f"  Botón {i+1}:")
                print(f"    - Tipo: {button_type}")
                print(f"    - Texto: {button_text}")
                print(f"    - Class: {button_class}")
                print(f"    - ID: {button_id}")
                print(f"    - Visible: {button.is_displayed()}")
                print()
            except Exception as e:
                print(f"    - Error obteniendo información: {e}")
        
        # Buscar formularios
        print("\n📋 Formularios encontrados:")
        forms = driver.find_elements(By.TAG_NAME, "form")
        for i, form in enumerate(forms):
            try:
                form_action = form.get_attribute("action") or "sin_action"
                form_method = form.get_attribute("method") or "sin_method"
                form_class = form.get_attribute("class") or "sin_class"
                form_id = form.get_attribute("id") or "sin_id"
                
                print(f"  Formulario {i+1}:")
                print(f"    - Action: {form_action}")
                print(f"    - Method: {form_method}")
                print(f"    - Class: {form_class}")
                print(f"    - ID: {form_id}")
                print()
            except Exception as e:
                print(f"    - Error obteniendo información: {e}")
        
        # Obtener el HTML de la página para análisis
        print("\n📄 Guardando HTML para análisis...")
        html_content = driver.page_source
        with open("login_page_source.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("HTML guardado en: login_page_source.html")
        
        # Buscar texto relevante
        print("\n🔍 Buscando texto relevante de login...")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        login_keywords = ["usuario", "contraseña", "password", "email", "acceder", "login", "entrar"]
        
        for keyword in login_keywords:
            if keyword.lower() in body_text.lower():
                print(f"  ✅ Encontrado: '{keyword}'")
            else:
                print(f"  ❌ No encontrado: '{keyword}'")
        
        print(f"\n📊 Resumen:")
        print(f"  - Total inputs: {len(inputs)}")
        print(f"  - Total botones: {len(buttons)}")
        print(f"  - Total formularios: {len(forms)}")
        
    except Exception as e:
        print(f"❌ Error durante inspección: {e}")
    
    finally:
        print("\n🔄 Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    inspect_login_page()