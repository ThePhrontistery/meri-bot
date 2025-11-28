# meri-cli - Herramienta de línea de comandos para MeriBot# meri-cli - Herramienta de línea de comandos para MeriBot



## Descripción## Descripción

Este módulo proporciona la herramienta de línea de comandos oficial `meri-cli` para la gestión y administración del sistema MeriBot. Permite realizar operaciones de crawling, procesamiento de documentos y gestión de la base de datos vectorial de manera programática y controlada.Este módulo proporciona la herramienta de línea de comandos oficial `meri-cli` para la gestión y administración del sistema MeriBot. Permite realizar operaciones de crawling, procesamiento de documentos y gestión de la base de datos vectorial de manera programática y controlada.



## Características Principales## Características Principales

- Interfaz de línea de comandos intuitiva con Click- Interfaz de línea de comandos intuitiva con Click

- Comunicación directa con endpoints de la API MeriBot- Comunicación directa con el endpoint de crawling `/crawl-and-process`

- Validación de dominios y URLs- Validación de dominios y URLs

- Modo dry-run para simulación segura- Modo dry-run para simulación segura

- Gestión de múltiples formatos de archivo (HTML, PDF, DOCX, XLSX)- Gestión de múltiples formatos de archivo (HTML, PDF, DOCX, XLSX)

- Administración completa de la base de datos vectorial- Instalación opcional para uso global en el sistema

- Instalación opcional para uso global en el sistema

## Instalación y Uso

## Instalación y Uso

### Opción 1: Uso directo desde el directorio meri-cli

### Opción 1: Uso directo desde el directorio meri-cli```powershell

```powershellcd meribot/meri-cli

cd meribot/meri-cli.\meri-cli.bat crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"

.\meri-cli.bat crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"```

```

### Opción 2: Instalación global (recomendado)

### Opción 2: Instalación global (recomendado)```powershell

```powershellcd meribot/meri-cli

cd meribot/meri-cli.\install-meri-cli.ps1 -Install

.\install-meri-cli.ps1 -Install# Reiniciar terminal

# Reiniciar terminalmeri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"```

```



## Comandos Disponibles## Comandos Principales



### 🕷️ Comando `crawl` - Crawling y Procesamiento### Comando crawl (principal)

Ejecuta el proceso completo de crawling y procesamiento de documentos.Ejecuta el proceso completo de crawling y procesamiento de documentos.



**Parámetros obligatorios:****Parámetros obligatorios:**

- `--url`: URL inicial para el crawling- `--url`: URL inicial para el crawling

- `--dominio`: Dominio al que pertenece la información- `--dominio`: Dominio al que pertenece la información



**Parámetros opcionales:****Parámetros opcionales:**

- `--max-depth INTEGER`: Profundidad máxima de navegación (default: 4)- `--max-depth INTEGER`: Profundidad máxima de navegación (default: 2)

- `--max-pages INTEGER`: Número máximo de páginas a explorar- `--max-pages INTEGER`: Número máximo de páginas a explorar

- `--include TEXT`: Patrón regex para incluir URLs- `--include TEXT`: Patrón regex para incluir URLs

- `--exclude TEXT`: Patrón regex para excluir URLs- `--exclude TEXT`: Patrón regex para excluir URLs

- `--formats TEXT`: Formatos de archivo a recolectar (default: html,pdf,docx,xlsx)- `--formats TEXT`: Formatos de archivo a recolectar (default: html,pdf,docx,xlsx)

- `--output TEXT`: Directorio destino para documentos- `--output TEXT`: Directorio destino para documentos

- `--update-only`: Solo actualizar documentos nuevos o modificados- `--update-only`: Solo actualizar documentos nuevos o modificados

- `--dry-run`: Simular crawling sin descargar- `--dry-run`: Simular crawling sin descargar

- `--manual TEXT`: Lista de URLs separadas por comas para procesar manualmente- `--manual TEXT`: Lista de URLs separadas por comas para procesar manualmente

- `--api-host TEXT`: Host del API de MeriBot (default: http://localhost:8000)- `--api-host TEXT`: Host del API de MeriBot (default: http://localhost:8000)



**Ejemplos:**### Ejemplos de uso

```bash```bash

# Crawling básico# Crawling básico

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"



# Con opciones avanzadas# Con opciones avanzadas

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \

  --max-depth 3 \  --max-depth 3 \

  --formats "html,pdf" \  --formats "html,pdf" \

  --exclude ".*logout.*"  --exclude ".*logout.*"



# Modo simulación# Modo simulación

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --dry-runmeri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --dry-run



# Procesamiento manual de URLs específicas# Procesamiento manual de URLs específicas

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \

  --manual "https://cca.capgemini.com/page1,https://cca.capgemini.com/page2"  --manual "https://cca.capgemini.com/page1,https://cca.capgemini.com/page2"

``````



### 🗄️ Comando `db` - Gestión de Base de Datos Vectorial### Comando db

Administra documentos y fragmentos almacenados en la base de datos vectorial (ChromaDB).Gestiona la base de datos vectorial.

```bash

#### `db list` - Listar documentos# Resetear la base de datos (requiere confirmación)

Lista todos los documentos almacenados en la base vectorial.meri-cli db --reset

```

**Opciones:**

- `--filter <campo>:<valor>`: Filtra documentos por campo específico### Comando scrape (obsoleto)

- `--show-chunks`: Muestra también el número de fragmentos asociadosMantiene compatibilidad con versiones anteriores.

```bash

**Ejemplos:**meri-cli scrape --url "https://example.com"

```bash```

# Listar todos los documentos

meri-cli db list## Estructura del Módulo

```

# Filtrar por dominiomeri-cli/

meri-cli db list --filter dominio:cca├── __init__.py

├── main.py                   # Implementación principal con Click

# Mostrar con número de chunks├── meri-cli.py              # Script ejecutable Python

meri-cli db list --show-chunks├── meri-cli.bat             # Script batch para Windows

├── meri-cli.ps1             # Script PowerShell

# Combinar filtro y chunks├── install-meri-cli.ps1     # Instalador para uso global

meri-cli db list --filter dominio:cca --show-chunks├── README.md                # Esta documentación

```└── GUIA-RAPIDA.md          # Guía de referencia rápida

```

#### `db show` - Mostrar detalles de documento

Muestra información detallada y metadatos de un documento específico.## Configuración

La herramienta lee la configuración desde `crawler_config.yaml` en el directorio raíz del proyecto:

**Parámetros obligatorios:**

- `--id <DOCUMENT_ID>`: ID del documento a mostrar```yaml

seeds:

**Ejemplo:**  - "https://cca.capgemini.com/web/home"

```bashallowed_domains:

# Mostrar detalles completos de un documento  - "cca"

meri-cli db show --id "doc_12345"  - "onboarding"

```  - "training"

user_agent: "MeriBot/1.0"

#### `db delete` - Eliminar documentosdelay: 1.0

Elimina un documento y todos sus fragmentos asociados.output_dir: "./data/scraped"

max_depth: 4

**Opciones (una requerida):**file_types:

- `--id <DOCUMENT_ID>`: Eliminar por ID de documento  - "html"

- `--url <URL>`: Eliminar por URL fuente  - "pdf"

- `--source-path <PATH>`: Eliminar por ruta fuente  - "docx"

  - "xlsx"

**Ejemplos:**```

```bash

# Eliminar por ID## Validaciones y Seguridad

meri-cli db delete --id "doc_12345"- **Validación de URL**: Verifica que la URL tenga protocolo válido

- **Validación de dominio**: Comprueba que el dominio esté en la lista permitida

# Eliminar por URL- **Timeouts**: Configuración de timeouts para evitar colgues

meri-cli db delete --url "https://cca.capgemini.com/page"- **Dry-run**: Modo simulación para pruebas seguras

- **Confirmación**: Operaciones destructivas requieren confirmación

# Eliminar por source-path

meri-cli db delete --source-path "/data/scraped/cca.capgemini.com/page.html"## Requisitos

```- Python 3.10 o superior

- Dependencias: Click, requests, PyYAML, urllib3

#### `db count` - Contar documentos y fragmentos- Servidor FastAPI ejecutándose (por defecto en http://localhost:8000)

Muestra estadísticas de la base de datos vectorial.- Configuración válida en `crawler_config.yaml`



**Ejemplo:**## Arquitectura de Comunicación

```bash```

# Mostrar conteo totalmeri-cli → FastAPI Endpoint → Crawler Service → ChromaDB

meri-cli db count         ↓

```   /crawl-and-process

```

### 📋 Ejemplos de Uso Completo

El CLI se comunica con el endpoint `/crawl-and-process` que:

#### Flujo típico de trabajo:1. Valida los parámetros de entrada

```bash2. Ejecuta el scraping de documentos

# 1. Verificar estado actual de la base de datos3. Procesa y fragmenta el contenido

meri-cli db count4. Almacena en la base de datos vectorial ChromaDB

5. Retorna el resultado del procesamiento

# 2. Listar documentos existentes

meri-cli db list## Solución de Problemas



# 3. Ejecutar crawling de nuevos documentos### Error "Missing option '--dominio'"

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --max-depth 2Asegúrate de incluir ambos parámetros obligatorios:

```bash

# 4. Verificar que se agregaron correctamentemeri-cli crawl --url "https://example.com" --dominio "example"

meri-cli db list --filter dominio:cca --show-chunks```



# 5. Ver detalles de un documento específico### Error de conexión con FastAPI

meri-cli db show --id "doc_12345"Verifica que el servidor esté ejecutándose:

```bash

# 6. Si es necesario, eliminar documentos obsoletospython -m meribot.core.api.app

meri-cli db delete --url "https://cca.capgemini.com/old-page"```

```

### Dominio no permitido

## Estructura del MóduloRevisa `crawler_config.yaml` y asegúrate de que el dominio esté en `allowed_domains`.

```

meri-cli/### Instalación global no funciona

├── __init__.pyReinicia la terminal después de ejecutar el instalador:

├── main.py                   # Implementación principal con Click```powershell

├── db_commands.py           # Comandos de gestión de base de datos.\install-meri-cli.ps1 -Install

├── meri-cli.py              # Script ejecutable Python# Reiniciar terminal o ejecutar: refreshenv

├── meri-cli.bat             # Script batch para Windows```

├── meri-cli.ps1             # Script PowerShell

├── install-meri-cli.ps1     # Instalador para uso global## Notas de Desarrollo

├── scheduler_config.yaml    # Configuración del scheduler- Implementado con Click para una interfaz robusta

├── README.md                # Esta documentación- Soporte completo para PowerShell en Windows

├── GUIA-RAPIDA.md          # Guía de referencia rápida- Manejo de errores con mensajes informativos

└── tasks-db.md             # Documentación de tareas de DB- Interfaz amigable con emojis y colores

```- Arquitectura modular y extensible


## Configuración

### Variables de Entorno
La herramienta usa las siguientes variables de entorno (definidas en `.env`):

```env
MERIBOT_CRAWLER_URL=http://localhost:8000
MERIBOT_LOG_LEVEL=INFO
```

### Archivo de Configuración del Crawler
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
- **Validación de parámetros**: Verificación de exclusividad en comandos db delete

## Requisitos
- Python 3.10 o superior
- Dependencias: Click, requests, PyYAML, urllib3, python-dotenv, tabulate
- Servidor FastAPI ejecutándose (por defecto en http://localhost:8000)
- Configuración válida en `crawler_config.yaml`
- Variables de entorno configuradas en `.env`

## Arquitectura de Comunicación

### Para comandos de crawling:
```
meri-cli crawl → FastAPI /crawl-and-process → Crawler Service → ChromaDB
```

### Para comandos de base de datos:
```
meri-cli db → FastAPI Endpoints → ChromaDB
              ├── /list-documents
              ├── /show-document
              ├── /delete-document
              ├── /delete-document-by-url
              ├── /delete-document-by-source-path
              └── /count-documents
```

El CLI se comunica con diferentes endpoints que:
1. Validan los parámetros de entrada
2. Ejecutan las operaciones solicitadas
3. Retornan resultados en formato JSON
4. Proporcionan manejo de errores consistente

## Solución de Problemas

### Error "Missing option '--dominio'"
Asegúrate de incluir ambos parámetros obligatorios en crawl:
```bash
meri-cli crawl --url "https://example.com" --dominio "example"
```

### Error "Missing option '--id'" en comandos db
Para comandos como `db show`, el ID es obligatorio:
```bash
meri-cli db show --id "doc_12345"
```

### Error "No puede usar más de una opción" en db delete
Solo especifica una opción de eliminación a la vez:
```bash
# ✅ Correcto
meri-cli db delete --id "doc_12345"

# ❌ Incorrecto
meri-cli db delete --id "doc_12345" --url "https://example.com"
```

### Error de conexión con FastAPI
Verifica que el servidor esté ejecutándose:
```bash
python start_server_direct.py
```

### Dominio no permitido
Revisa `crawler_config.yaml` y asegúrate de que el dominio esté en `allowed_domains`.

### Instalación global no funciona
Reinicia la terminal después de ejecutar el instalador:
```powershell
.\install-meri-cli.ps1 -Install
# Reiniciar terminal o ejecutar: refreshenv
```

### Error "[ERROR] No se pudo conectar al endpoint del crawler"
Verifica:
1. Que el servidor MeriBot esté ejecutándose
2. Que la URL del endpoint sea correcta (variable `MERIBOT_CRAWLER_URL`)
3. Que no haya firewall bloqueando la conexión

## Formatos de Salida

### Tablas formateadas
Si `tabulate` está instalado, los comandos `db list` y `db show` mostrarán tablas formateadas:
```bash
pip install tabulate
```

### Salida sin formato
Si `tabulate` no está disponible, la salida será en formato texto plano con separadores de tabulación.

## Notas de Desarrollo
- Implementado con Click para una interfaz robusta
- Soporte completo para PowerShell en Windows
- Manejo de errores con mensajes informativos
- Interfaz amigable con emojis y colores
- Arquitectura modular y extensible
- Separación clara entre comandos de crawling y base de datos
- Uso de variables de entorno para configuración flexible