# Mejora del Scraper para SPAs (Single Page Applications)

## Resumen de las Mejoras

Se ha implementado un nuevo `SPAWebScraper` que utiliza Selenium WebDriver para manejar páginas web que dependen de JavaScript para mostrar contenido dinámico. Esta mejora es especialmente importante para sitios web modernos construidos con frameworks como Angular, React, o Vue.js.

## Problema Solucionado

El scraper tradicional (`WebScraper`) utiliza únicamente `requests` y `BeautifulSoup`, lo que solo puede extraer el HTML estático inicial. Para las SPAs (Single Page Applications), esto resulta en:

- **0 caracteres** de texto útil extraído
- **0 palabras** de contenido
- **Pérdida completa** del contenido dinámico generado por JavaScript

## Solución Implementada

El nuevo `SPAWebScraper` incluye:

### 1. Detección Automática de SPAs
- Identifica automáticamente páginas que son SPAs basándose en indicadores como:
  - Frameworks detectados: `ng-app`, `angular`, `react`, `vue`
  - Contenido mínimo con muchos scripts
  - Indicadores de carga dinámica: `loading`, `spinner`

### 2. Renderizado con Selenium
- Utiliza Chrome WebDriver para cargar páginas completamente
- Espera a que JavaScript termine de ejecutarse
- Extrae el HTML completamente renderizado

### 3. Configuración Flexible
```yaml
# Configuración SPA en crawler_config.yaml
spa_support: true          # Habilitar detección automática de SPAs
selenium_timeout: 15       # Timeout en segundos para cargar páginas
headless: true            # Ejecutar navegador sin interfaz gráfica
selenium_delay: 3         # Tiempo adicional para contenido dinámico
```

## Resultados de la Mejora

### Comparación: Scraper Tradicional vs SPA

**Página de prueba**: `https://cca.capgemini.com/web/home` (Angular SPA)

| Método | HTML | Texto Extraído | Palabras | Mejora |
|--------|------|----------------|----------|---------|
| **Tradicional** | 22,059 chars | **0 chars** | **0 palabras** | - |
| **SPA** | 27,952 chars | **413 chars** | **61 palabras** | **∞x** |

### Contenido Extraído
Con el SPAWebScraper se obtiene contenido real como:
```
Web C&CA Accede con tus credenciales corporativos (inicio de sesión en tu portatil) 
Usuario o email Contraseña Acceder ¿Has olvidado tu usuario o contraseña? 
¡No te preocupes! Puedes restablecerlos fácilmente...
```

## Archivos Implementados

### 1. `spa_scraper.py`
- **SPAWebScraper**: Clase principal con soporte SPA
- **Detección automática**: Identifica SPAs sin configuración manual
- **Manejo de recursos**: Gestión automática del WebDriver

### 2. `scraper.py` (actualizado)
- **create_scraper()**: Factory function que elige automáticamente el scraper apropiado
- **Compatibilidad hacia atrás**: Mantiene funcionalidad del WebScraper original
- **Fallback inteligente**: Usa WebScraper tradicional si Selenium no está disponible

### 3. `config.py` (actualizado)
- **Nuevos campos de configuración** para SPA support
- **Validación extendida** con Pydantic
- **Configuración flexible** por YAML

### 4. `crawler_config.yaml` (actualizado)
- **Configuración SPA** añadida con valores por defecto sensatos
- **Documentación inline** de cada parámetro

## Instalación de Dependencias

```bash
pip install selenium webdriver-manager
```

## Uso

### Automático (Recomendado)
```python
from meribot.crawler.scraper import create_scraper
from meribot.crawler.config import load_yaml_config

config = load_yaml_config("crawler_config.yaml")
scraper = create_scraper(config)  # Selecciona automáticamente el scraper apropiado
scraper.crawl_url("https://example.com")
```

### Manual
```python
from meribot.crawler.spa_scraper import SPAWebScraper

scraper = SPAWebScraper(config)
scraper.crawl_url("https://spa-example.com")
```

## Scripts de Prueba

### `test_spa_scraper.py`
Prueba completa del SPAWebScraper con la página de Capgemini.

### `compare_scrapers.py`  
Comparación lado a lado entre el scraper tradicional y el SPA scraper.

### `debug_parse_html.py`
Script de debugging para analizar problemas de extracción de texto.

## Beneficios

1. **Cobertura completa**: Maneja tanto sitios estáticos como SPAs
2. **Detección automática**: No requiere configuración manual por sitio
3. **Compatibilidad**: Funciona con el código existente
4. **Rendimiento**: Usa Selenium solo cuando es necesario
5. **Configurabilidad**: Timeouts y delays ajustables por sitio

## Casos de Uso Ideales

- **Sitios corporativos modernos** (Angular, React, Vue)
- **Portales de empleados** con autenticación dinámica  
- **Dashboards** con contenido generado por JavaScript
- **Aplicaciones web** con navegación client-side
- **Sitios híbridos** que mezclan contenido estático y dinámico

## Limitaciones

- **Rendimiento**: ~2-6 segundos adicionales por página SPA
- **Recursos**: Requiere Chrome/Chromium instalado
- **Memoria**: Mayor uso de memoria con WebDriver activo
- **Complejidad**: Dependencia adicional de Selenium

## Monitoreo y Logging

El scraper SPA incluye logging detallado:
```
{"timestamp": "2025-10-28T13:01:34.265364Z", "level": "INFO", 
 "message": "SPA detectada en https://example.com - Indicador: ng-app"}
 
{"timestamp": "2025-10-28T13:01:50.814086Z", "level": "INFO", 
 "message": "Contenido SPA obtenido: 27952 caracteres"}
```

## Próximos Pasos

1. **Optimización de rendimiento**: Cache de WebDriver por sesión
2. **Soporte multi-navegador**: Firefox, Edge además de Chrome  
3. **Detección avanzada**: Análisis más sofisticado de SPAs
4. **Configuración por dominio**: Timeouts específicos por sitio
5. **Manejo de autenticación**: Login automático para sitios protegidos