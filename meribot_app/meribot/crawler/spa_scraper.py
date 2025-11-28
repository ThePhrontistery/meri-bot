"""
Módulo de WebScraper avanzado con soporte para SPAs (Single Page Applications).
Utiliza Selenium WebDriver para renderizar JavaScript y extraer contenido dinámico.
"""
import os
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from .config import get_config, load_yaml_config, validate_config, ConfigError
from meribot.utils.logging import get_logger


class SPAWebScraper:
    """
    WebScraper avanzado que puede manejar SPAs usando Selenium WebDriver.
    Detecta automáticamente si una página requiere JavaScript rendering.
    """
    
    def __init__(self, config, logger=None):
        """
        Inicializa el SPAWebScraper con la configuración y el logger proporcionados.
        Args:
            config (dict): Configuración del crawler (dominios, profundidad, tipos de archivo, etc.)
            logger (Logger, opcional): Logger estructurado. Si no se proporciona, se crea uno por defecto.
        """
        self.config = config
        self.logger = logger or get_logger("SPAWebScraper")
        self.allowed_domains = set(self.config["allowed_domains"])
        self.max_depth = self.config.get("max_depth", 4)
        
        # Validación robusta para file_types
        file_types_raw = self.config.get("file_types", ["html", "pdf", "docx", "xlsx"])
        if isinstance(file_types_raw, (list, tuple)):
            self.file_types = set(file_types_raw)
        elif isinstance(file_types_raw, str):
            # Si es string, separar por comas
            self.file_types = set([ft.strip() for ft in file_types_raw.split(",")])
        else:
            # Fallback a tipos por defecto
            self.logger.warning(f"file_types inválido ({type(file_types_raw)}), usando valores por defecto")
            self.file_types = set(["html", "pdf", "docx", "xlsx"])
        
        self.logger.info(f"file_types configurado: {self.file_types} (tipo: {type(self.file_types)})")
        
        self.visited = set()
        self.delay = float(self.config.get("delay", 1.0))
        self.user_agent = self.config.get("user_agent", "MeriBot/1.0")
        
        # Configuración específica para SPA
        self.use_selenium = self.config.get("spa_support", True)
        self.selenium_timeout = self.config.get("selenium_timeout", 10)
        self.headless = self.config.get("headless", True)
        self.selenium_delay = self.config.get("selenium_delay", 3)
        
        # Driver de Selenium (se inicializa cuando sea necesario)
        self.driver = None
        
    def _get_local_path(self, url, ext):
        """
        Construye la ruta local para guardar el archivo basado en output_dir, dominio y path.
        """
        from pathlib import Path
        output_dir = self.config.get("output_dir", "./data/scraped")
        parsed = urlparse(url)
        domain = parsed.netloc.replace(":", "_")
        path = parsed.path.lstrip("/").replace("/", os.sep)
        if not path or path.endswith("/"):
            path += "index.{}".format(ext)
        local_path = os.path.join(output_dir, domain, path)
        Path(os.path.dirname(local_path)).mkdir(parents=True, exist_ok=True)
        return local_path

    def _init_selenium_driver(self):
        """
        Inicializa el driver de Selenium WebDriver de forma lazy.
        """
        if self.driver is None:
            try:
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-logging")
                chrome_options.add_argument("--disable-default-apps")
                chrome_options.add_argument(f"--user-agent={self.user_agent}")
                
                # Configurar el servicio con ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_page_load_timeout(self.selenium_timeout)
                self.logger.info("Driver de Selenium inicializado correctamente")
                
            except Exception as e:
                self.logger.error(f"Error inicializando driver de Selenium: {e}")
                self.driver = None
                
    def _close_selenium_driver(self):
        """
        Cierra el driver de Selenium si está activo.
        """
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info("Driver de Selenium cerrado")
            except Exception as e:
                self.logger.error(f"Error cerrando driver de Selenium: {e}")

    def _try_page_interactions(self):
        """
        Intenta interacciones comunes para activar contenido dinámico.
        """
        try:
            if not self.driver:
                return
                
            self.logger.info("Intentando interacciones para activar contenido dinámico")
            
            # Hacer scroll hacia abajo para activar lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Scroll hacia arriba
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Scroll paso a paso por la página
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_step = max(500, page_height // 5)  # Dividir en 5 pasos
            
            for i in range(0, page_height, scroll_step):
                self.driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(0.5)  # Esperar brevemente en cada paso
            
            # Intentar hacer hover sobre elementos interactivos
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.common.by import By
                
                # Buscar botones, enlaces o elementos que puedan tener hover effects
                interactive_elements = self.driver.find_elements(By.CSS_SELECTOR, "button, a, .btn, [role='button']")
                actions = ActionChains(self.driver)
                
                for element in interactive_elements[:5]:  # Solo los primeros 5
                    try:
                        actions.move_to_element(element).perform()
                        time.sleep(0.3)
                    except Exception:
                        continue  # Ignorar elementos que no se pueden hacer hover
                        
            except Exception as e:
                self.logger.debug(f"No se pudieron realizar hovers: {e}")
            
            # Intentar clicks en elementos seguros que no naveguen
            try:
                # Buscar elementos expandibles (dropdowns, accordions, etc.)
                expandable_selectors = [
                    "[data-toggle]", "[data-target]", ".dropdown-toggle", 
                    ".accordion-toggle", ".collapse-toggle", "[aria-expanded='false']"
                ]
                
                for selector in expandable_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements[:3]:  # Solo los primeros 3 de cada tipo
                        try:
                            if element.is_displayed() and element.is_enabled():
                                element.click()
                                time.sleep(1)
                                break  # Solo un click por selector
                        except Exception:
                            continue
                            
            except Exception as e:
                self.logger.debug(f"No se pudieron realizar clicks expandibles: {e}")
            
            # Volver al top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            self.logger.info("Interacciones completadas")
            
        except Exception as e:
            self.logger.warning(f"Error durante interacciones de página: {e}")

    def _is_spa_page(self, html_content, url):
        """
        Determina si una página es una SPA basándose en indicadores comunes.
        Args:
            html_content (str): Contenido HTML de la página
            url (str): URL de la página
        Returns:
            bool: True si la página parece ser una SPA
        """
        spa_indicators = [
            # Frameworks JS comunes
            'ng-app', 'ng-version', 'angular',  # Angular
            'react', 'reactDOM',                 # React
            'vue', 'v-app',                      # Vue.js
            # Indicadores de contenido dinámico
            'loading', 'spinner'
        ]
        
        # Verificación separada para contenido mínimo típico de SPAs
        is_minimal_with_scripts = len(html_content.strip()) < 5000 and 'script' in html_content.lower()
        
        html_lower = html_content.lower()
        
        # Verificar indicadores de cadena
        for indicator in spa_indicators:
            if indicator in html_lower:
                self.logger.info(f"SPA detectada en {url} - Indicador: {indicator}")
                return True
        
        # Verificar si es una página mínima con scripts (típico de SPAs)
        if is_minimal_with_scripts:
            self.logger.info(f"SPA detectada en {url} - Indicador: contenido mínimo con scripts")
            return True
                
        return False

    def _get_page_content_with_selenium(self, url):
        """
        Obtiene el contenido de una página usando Selenium para renderizar JavaScript.
        Args:
            url (str): URL a cargar
        Returns:
            str: HTML renderizado o None si hay error
        """
        try:
            if not self.driver:
                self._init_selenium_driver()
                
            if not self.driver:
                return None
            
            # Manejar autenticación si es necesaria (solo una vez por sesión)
            if not hasattr(self, '_authentication_handled'):
                auth_success = self._handle_authentication(self.driver)
                self._authentication_handled = True
                if not auth_success:
                    self.logger.warning("Autenticación falló, continuando sin autenticación")
                
            self.logger.info(f"Cargando página con Selenium: {url}")
            self.driver.get(url)
            
            # Esperar a que la página cargue completamente
            time.sleep(self.selenium_delay)
            
            # Intentar esperar por elementos que indiquen que el contenido está listo
            try:
                # Esperar por elementos comunes que indican contenido cargado
                WebDriverWait(self.driver, self.selenium_timeout).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # Esperar un poco más para contenido dinámico inicial
                time.sleep(3)
                
                # Intentar interacciones para activar contenido dinámico
                self._try_page_interactions()
                
                # Esperar después de las interacciones
                time.sleep(2)
                
            except TimeoutException:
                self.logger.warning(f"Timeout esperando carga completa de {url}")
                
            # Obtener el HTML renderizado
            rendered_html = self.driver.page_source
            self.logger.info(f"Contenido obtenido con Selenium: {len(rendered_html)} caracteres")
            return rendered_html
            
        except WebDriverException as e:
            self.logger.error(f"Error de WebDriver obteniendo {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo {url} con Selenium: {e}")
            return None

    def save_html(self, url, html):
        """
        Guarda el HTML de la página en la ruta local correspondiente y la URL de origen en un archivo .url.
        """
        local_path = self._get_local_path(url, "html")
        url_path = local_path + ".url"
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(html)
            # Guardar la URL de origen en un archivo .url junto al HTML
            with open(url_path, "w", encoding="utf-8") as f_url:
                f_url.write(url)
            self.logger.info(f"[GUARDADO HTML] {local_path} y {url_path}")
        except Exception as e:
            self.logger.error(f"Error guardando HTML {local_path} o .url: {e}")

    def download_file(self, url):
        """
        Descarga un archivo adjunto y lo guarda en la ruta local correspondiente.
        Además, guarda la URL de origen en un archivo .url junto al documento.
        """
        local_path = self._get_local_path(url, url.split(".")[-1].lower())
        url_path = local_path + ".url"
        try:
            # Guardar la URL de origen en un archivo .url junto al documento SIEMPRE
            with open(url_path, "w", encoding="utf-8") as f_url:
                f_url.write(url)
            # Descargar el archivo solo si no existe
            if not os.path.exists(local_path):
                resp = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=20, verify=False)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                self.logger.info(f"[DESCARGADO] {local_path} (origen: {url})")
            else:
                self.logger.info(f"[YA EXISTE] {local_path} (origen: {url}) - Solo se actualizó el .url")
        except Exception as e:
            self.logger.error(f"Error descargando archivo {url}: {e}")

    def crawl_url(self, url, depth=4):
        """
        Realiza el crawling recursivo sobre una URL, con soporte automático para SPAs.
        Args:
            url (str): URL a visitar.
            depth (int): Profundidad actual del crawling.
        """
        if depth > self.max_depth:
            self.logger.info(f"Profundidad máxima alcanzada: {depth} en {url}")
            return
            
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain not in self.allowed_domains:
            self.logger.info(f"Dominio no permitido: {domain} ({url})")
            return
            
        if url in self.visited:
            return
            
        self.visited.add(url)
        self.logger.info(f"Visitando: {url} (profundidad {depth})")
        
        headers = {"User-Agent": self.user_agent}
        html_content = None
        is_spa = False
        
        try:
            # Primero intentar con requests tradicional
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            
            # Asegurar que content_type es una cadena
            if not isinstance(content_type, str):
                self.logger.warning(f"content_type no es string: {type(content_type)} = {content_type}")
                content_type = str(content_type) if content_type else ""
            
            content_type = content_type.lower()
            
            if "html" in content_type:
                initial_html = resp.text
                
                # Verificar si es una SPA
                if self.use_selenium and self._is_spa_page(initial_html, url):
                    is_spa = True
                    self.logger.info(f"SPA detectada: {url} - Usando Selenium")
                    
                    # Obtener contenido renderizado con Selenium
                    rendered_html = self._get_page_content_with_selenium(url)
                    if rendered_html:
                        html_content = rendered_html
                        self.logger.info(f"Contenido SPA obtenido: {len(html_content)} caracteres")
                    else:
                        self.logger.warning(f"Fallback a HTML estático para {url}")
                        html_content = initial_html
                else:
                    html_content = initial_html
                    
                # Guardar HTML (renderizado o estático)
                self.save_html(url, html_content)
                
                # Procesar enlaces
                soup = BeautifulSoup(html_content, "html.parser")
                links = self._parse_links(soup, url)
                self.logger.info(f"Enlaces encontrados: {len(links)} en {url} {'(SPA)' if is_spa else '(estático)'}")
                
                for link, ext in links:
                    abs_url = urljoin(url, link)
                    if ext == "html":
                        time.sleep(self.delay)
                        self.crawl_url(abs_url, depth + 1)
                    elif ext and isinstance(self.file_types, set) and ext in self.file_types:
                        self.logger.info(f"Documento detectado: {abs_url} (tipo: {ext})")
                        self.download_file(abs_url)
            else:
                # Documento soportado
                ext = url.split(".")[-1].lower() if "." in url else ""
                if ext and isinstance(self.file_types, set) and ext in self.file_types:
                    self.logger.info(f"Documento detectado: {url} (tipo: {ext})")
                    self.download_file(url)
                    
        except Exception as e:
            self.logger.error(f"Error procesando {url}: {e}")

    def _parse_links(self, soup, base_url):
        """
        Extrae y clasifica los enlaces de un documento HTML.
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup del HTML.
            base_url (str): URL base para resolver rutas relativas.
        Returns:
            list: Lista de tuplas (href, ext) con enlaces y su tipo de archivo.
        """
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?")[0].split("#")[0]
            
            # Filtrar enlaces vacíos o de navegación interna
            if not href or href.startswith("#") or href == "/":
                continue
                
            ext = href.split(".")[-1].lower() if "." in href.split("/")[-1] else ""
            
            if ext and isinstance(self.file_types, set) and ext in self.file_types:
                links.append((href, ext))
            elif ext == "html" or not ext:
                links.append((href, "html"))
                
        return links

    def _handle_authentication(self, driver) -> bool:
        """Maneja la autenticación automática si está configurada"""
        try:
            auto_login = self.config.get('auto_login', {})
            if not auto_login or not auto_login.get('enabled', False):
                return True  # No hay autenticación configurada, continuamos
            
            login_url = auto_login.get('login_url')
            if not login_url:
                self.logger.warning("URL de login no configurada")
                return True
            
            # Navegar a la página de login
            self.logger.info(f"Navegando a página de login: {login_url}")
            driver.get(login_url)
            
            # Esperar a que la página se cargue
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Obtener credenciales de la configuración
            username = auto_login.get('username')
            password = auto_login.get('password')
            
            if not username or not password:
                self.logger.error("Credenciales no encontradas en la configuración")
                return False
            
            # Rellenar formulario de login
            username_selector = auto_login.get('username_field', '#username')
            password_selector = auto_login.get('password_field', '#password')
            submit_selector = auto_login.get('submit_button', 'input[type="submit"]')
            
            # Encontrar y rellenar campo de usuario
            username_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, username_selector))
            )
            username_element.clear()
            username_element.send_keys(username)
            
            # Encontrar y rellenar campo de contraseña
            password_element = driver.find_element(By.CSS_SELECTOR, password_selector)
            password_element.clear()
            password_element.send_keys(password)
            
            # Enviar formulario
            submit_element = driver.find_element(By.CSS_SELECTOR, submit_selector)
            submit_element.click()
            
            # Esperar a que el login se complete
            success_indicators = auto_login.get('success_indicators', [])
            max_wait = auto_login.get('login_timeout', 30)
            
            if success_indicators:
                # Esperar a que aparezca algún indicador de éxito
                for indicator in success_indicators:
                    try:
                        WebDriverWait(driver, max_wait).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        self.logger.info("Login exitoso detectado")
                        return True
                    except:
                        continue
                
                self.logger.warning("No se detectaron indicadores de login exitoso")
                return False
            else:
                # Esperar un tiempo fijo si no hay indicadores específicos
                time.sleep(5)
                self.logger.info("Login completado (sin verificación específica)")
                return True
        
        except Exception as e:
            self.logger.error(f"Error durante autenticación: {str(e)}")
            return False

    def _handle_authentication(self, driver) -> bool:
        """Maneja la autenticación automática si está configurada"""
        try:
            auto_login = self.config.get('auto_login', {})
            if not auto_login or not auto_login.get('enabled', False):
                return True  # No hay autenticación configurada, continuamos
            
            login_url = auto_login.get('login_url')
            if not login_url:
                self.logger.warning("URL de login no configurada")
                return True
            
            # Navegar a la página de login
            self.logger.info(f"Navegando a página de login: {login_url}")
            driver.get(login_url)
            
            # Esperar a que la página se cargue
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Obtener credenciales de la configuración (ya las pasamos desde el API)
            username = auto_login.get('username')
            password = auto_login.get('password')
            
            if not username or not password:
                self.logger.error("Credenciales no encontradas en configuración")
                return False
            
            # Rellenar formulario de login con selectores más genéricos
            username_selectors = [
                'input[name="username"]',
                'input[name="user"]', 
                'input[name="email"]',
                'input[type="text"]',
                '#username',
                '#user',
                '#email'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Acceder")',
                'button:contains("Login")',
                'button:contains("Entrar")',
                '.btn-primary',
                '.login-button'
            ]
            
            # Intentar encontrar campo de usuario
            username_element = None
            for selector in username_selectors:
                try:
                    username_element = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"Campo de usuario encontrado con selector: {selector}")
                    break
                except:
                    continue
            
            if not username_element:
                self.logger.error("No se pudo encontrar el campo de usuario")
                return False
            
            # Intentar encontrar campo de contraseña
            password_element = None
            for selector in password_selectors:
                try:
                    password_element = driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Campo de contraseña encontrado con selector: {selector}")
                    break
                except:
                    continue
            
            if not password_element:
                self.logger.error("No se pudo encontrar el campo de contraseña")
                return False
            
            # Rellenar formulario
            username_element.clear()
            username_element.send_keys(username)
            self.logger.info("Campo de usuario rellenado")
            
            password_element.clear()
            password_element.send_keys(password)
            self.logger.info("Campo de contraseña rellenado")
            
            # Intentar enviar formulario
            submit_element = None
            for selector in submit_selectors:
                try:
                    submit_element = driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Botón de envío encontrado con selector: {selector}")
                    break
                except:
                    continue
            
            if submit_element:
                submit_element.click()
                self.logger.info("Formulario enviado")
            else:
                # Intentar enviar con Enter en el campo de contraseña
                password_element.send_keys(Keys.RETURN)
                self.logger.info("Formulario enviado con Enter")
            
            # Esperar a que el login se complete
            success_indicators = auto_login.get('success_indicators', [])
            max_wait = auto_login.get('login_timeout', 30)
            
            if success_indicators:
                # Esperar a que aparezca algún indicador de éxito
                for indicator in success_indicators:
                    try:
                        WebDriverWait(driver, max_wait).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        self.logger.info("Login exitoso detectado")
                        return True
                    except:
                        continue
                
                self.logger.warning("No se detectaron indicadores de login exitoso")
                # Continuar de todas formas para ver si el login funcionó
            
            # Esperar un tiempo fijo si no hay indicadores específicos
            time.sleep(5)
            
            # Verificar si hay errores de login visibles
            error_indicators = [
                '.error',
                '.alert-danger',
                '.login-error',
                '[class*="error"]'
            ]
            
            for error_selector in error_indicators:
                try:
                    error_element = driver.find_element(By.CSS_SELECTOR, error_selector)
                    if error_element.is_displayed():
                        self.logger.warning(f"Posible error de login detectado: {error_element.text}")
                        return False
                except:
                    continue
            
            self.logger.info("Login completado (sin verificación específica)")
            return True
        
        except Exception as e:
            self.logger.error(f"Error durante autenticación: {str(e)}")
            return False

    def __del__(self):
        """
        Destructor para asegurar que el driver de Selenium se cierre.
        """
        self._close_selenium_driver()


if __name__ == "__main__":
    # Validación de configuración al inicio
    try:
        config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "..", "crawler_config.yaml")
        config = load_yaml_config(config_path)
        validate_config(config)
    except ConfigError as e:
        print(f"[ERROR] Configuración inválida: {e}")
        exit(1)
    except Exception as ex:
        print(f"[ERROR] Error inesperado al validar configuración: {ex}")
        exit(1)

    # Inicializar logger estructurado con el nivel de la configuración YAML
    log_level = config.get("log_level", "INFO")
    logger = get_logger("SPAWebScraper", level=log_level)
    logger.info("[OK] Configuración válida y logger inicializado.")

    # Iniciar crawling sobre las URLs definidas en seeds
    seeds = config.get("seeds", [])
    if not seeds:
        logger.error("No se encontraron URLs en 'seeds' para iniciar el crawling.")
        exit(1)
        
    scraper = SPAWebScraper(config, logger=logger)
    try:
        for url in seeds:
            scraper.crawl_url(url, depth=4)
    finally:
        # Asegurar que el driver se cierre al finalizar
        scraper._close_selenium_driver()
        
    logger.info("Crawling web con soporte SPA finalizado.")