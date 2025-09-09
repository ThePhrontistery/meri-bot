# meri-cli - Herramienta de línea de comandos para MeriBot

## Descripción
Este módulo proporciona la herramienta de línea de comandos oficial `meri-cli` para la gestión y administración del sistema MeriBot. Permite realizar operaciones de crawling, procesamiento de documentos y gestión de la base de datos vectorial de manera programática y controlada.

## Características Principales
- Interfaz de línea de comandos intuitiva con Click
- Comunicación directa con el endpoint de crawling `/crawl-and-process`
- Validación de dominios y URLs
- Modo dry-run para simulación segura
- Gestión de múltiples formatos de archivo (HTML, PDF, DOCX, XLSX)
- Instalación opcional para uso global en el sistema

## Instalación y Uso

### Opción 1: Uso directo desde el directorio meri-cli
```powershell
cd meribot/meri-cli
.\meri-cli.bat crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"
```

### Opción 2: Instalación global (recomendado)
```powershell
cd meribot/meri-cli
.\install-meri-cli.ps1 -Install
# Reiniciar terminal
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"
```

## Comandos Principales

### Comando crawl (principal)
Ejecuta el proceso completo de crawling y procesamiento de documentos.

**Parámetros obligatorios:**
- `--url`: URL inicial para el crawling
- `--dominio`: Dominio al que pertenece la información

**Parámetros opcionales:**
- `--max-depth INTEGER`: Profundidad máxima de navegación (default: 2)
- `--max-pages INTEGER`: Número máximo de páginas a explorar
- `--include TEXT`: Patrón regex para incluir URLs
- `--exclude TEXT`: Patrón regex para excluir URLs
- `--formats TEXT`: Formatos de archivo a recolectar (default: html,pdf,docx,xlsx)
- `--output TEXT`: Directorio destino para documentos
- `--update-only`: Solo actualizar documentos nuevos o modificados
- `--dry-run`: Simular crawling sin descargar
- `--manual TEXT`: Lista de URLs separadas por comas para procesar manualmente
- `--api-host TEXT`: Host del API de MeriBot (default: http://localhost:8000)

### Ejemplos de uso
```bash
# Crawling básico
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"

# Con opciones avanzadas
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --max-depth 3 \
  --formats "html,pdf" \
  --exclude ".*logout.*"

# Modo simulación
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --dry-run

# Procesamiento manual de URLs específicas
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --manual "https://cca.capgemini.com/page1,https://cca.capgemini.com/page2"
```

### Comando db
Gestiona la base de datos vectorial.
```bash
# Resetear la base de datos (requiere confirmación)
meri-cli db --reset
```

### Comando scrape (obsoleto)
Mantiene compatibilidad con versiones anteriores.
```bash
meri-cli scrape --url "https://example.com"
```

## Estructura del Módulo
```
meri-cli/
├── __init__.py
├── main.py                   # Implementación principal con Click
├── meri-cli.py              # Script ejecutable Python
├── meri-cli.bat             # Script batch para Windows
├── meri-cli.ps1             # Script PowerShell
├── install-meri-cli.ps1     # Instalador para uso global
├── README.md                # Esta documentación
└── GUIA-RAPIDA.md          # Guía de referencia rápida
```

## Configuración
La herramienta lee la configuración desde `crawler_config.yaml` en el directorio raíz del proyecto:

```yaml
seeds:
  - "https://cca.capgemini.com/web/home"
allowed_domains:
  - "cca"
  - "onboarding"
  - "training"
user_agent: "MeriBot/1.0"
delay: 1.0
output_dir: "./data/scraped"
max_depth: 4
file_types:
  - "html"
  - "pdf"
  - "docx"
  - "xlsx"
```

## Validaciones y Seguridad
- **Validación de URL**: Verifica que la URL tenga protocolo válido
- **Validación de dominio**: Comprueba que el dominio esté en la lista permitida
- **Timeouts**: Configuración de timeouts para evitar colgues
- **Dry-run**: Modo simulación para pruebas seguras
- **Confirmación**: Operaciones destructivas requieren confirmación

## Requisitos
- Python 3.10 o superior
- Dependencias: Click, requests, PyYAML, urllib3
- Servidor FastAPI ejecutándose (por defecto en http://localhost:8000)
- Configuración válida en `crawler_config.yaml`

## Arquitectura de Comunicación
```
meri-cli → FastAPI Endpoint → Crawler Service → ChromaDB
         ↓
   /crawl-and-process
```

El CLI se comunica con el endpoint `/crawl-and-process` que:
1. Valida los parámetros de entrada
2. Ejecuta el scraping de documentos
3. Procesa y fragmenta el contenido
4. Almacena en la base de datos vectorial ChromaDB
5. Retorna el resultado del procesamiento

## Solución de Problemas

### Error "Missing option '--dominio'"
Asegúrate de incluir ambos parámetros obligatorios:
```bash
meri-cli crawl --url "https://example.com" --dominio "example"
```

### Error de conexión con FastAPI
Verifica que el servidor esté ejecutándose:
```bash
python -m meribot.api.app
```

### Dominio no permitido
Revisa `crawler_config.yaml` y asegúrate de que el dominio esté en `allowed_domains`.

### Instalación global no funciona
Reinicia la terminal después de ejecutar el instalador:
```powershell
.\install-meri-cli.ps1 -Install
# Reiniciar terminal o ejecutar: refreshenv
```

## Notas de Desarrollo
- Implementado con Click para una interfaz robusta
- Soporte completo para PowerShell en Windows
- Manejo de errores con mensajes informativos
- Interfaz amigable con emojis y colores
- Arquitectura modular y extensible
