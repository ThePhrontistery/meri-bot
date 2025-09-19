# meri-cli - Guía Rápida# meri-cli - Guía Rápida



## Ubicación## Ubicación

Este es el directorio oficial de meri-cli: `/meribot/meri-cli/`Este es el directorio oficial de meri-cli: `/meribot/meri-cli/`



## Instalación## Instalación



### Opción 1: Uso directo desde el directorio meri-cli### Opción 1: Uso directo desde el directorio meri-cli

```powershell```powershell

cd meribot/meri-clicd meribot/meri-cli

.\meri-cli.bat crawl --url "https://example.com" --dominio "example".\meri-cli.bat crawl --url "https://example.com" --dominio "example"

``````



### Opción 2: Instalación global### Opción 2: Instalación global

```powershell```powershell

cd meribot/meri-clicd meribot/meri-cli

.\install-meri-cli.ps1 -Install.\install-meri-cli.ps1 -Install

# Reiniciar terminal# Reiniciar terminal

# Desde cualquier directorio:# Desde cualquier directorio:

meri-cli crawl --url "https://example.com" --dominio "example"meri-cli crawl --url "https://example.com" --dominio "example"

``````



## Comandos principales## Comandos principales



### 🕷️ Crawling### Crawling básico

```bash```bash

# Básicomeri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"```



# Con opciones avanzadas### Crawling con opciones avanzadas

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \```bash

  --max-depth 3 \meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \

  --formats "html,pdf" \  --max-depth 3 \

  --exclude ".*logout.*" \  --formats "html,pdf" \

  --dry-run  --exclude ".*logout.*" \

```  --dry-run

```

### 🗄️ Base de Datos

```bash### Gestión de base de datos

# Listar documentos```bash

meri-cli db listmeri-cli db --reset

meri-cli db list --filter dominio:cca --show-chunks```



# Ver documento específico## Archivos en este directorio

meri-cli db show --id "doc_12345"

- `main.py` - Implementación principal del CLI con Click

# Contar documentos y fragmentos- `meri-cli.py` - Script ejecutable Python

meri-cli db count- `meri-cli.bat` - Script batch para Windows

- `meri-cli.ps1` - Script PowerShell

# Eliminar documentos- `install-meri-cli.ps1` - Instalador para uso global

meri-cli db delete --id "doc_12345"- `README.md` - Documentación del módulo

meri-cli db delete --url "https://cca.capgemini.com/page"- `GUIA-RAPIDA.md` - Esta guía

meri-cli db delete --source-path "/path/to/file.html"

```## Parámetros obligatorios

- `--url`: URL inicial para el crawling

### 📋 Flujo típico completo- `--dominio`: Dominio al que pertenece la información

```bash

# 1. Verificar estado## Requisitos

meri-cli db count- Python 3.10+

- Servidor FastAPI ejecutándose en http://localhost:8000 (configurable con --api-host)

# 2. Crawlear nuevos documentos- Dominio debe estar en la lista de dominios permitidos en `crawler_config.yaml`

meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"

## Estructura de ejecución

# 3. Verificar que se agregaron```

meri-cli db list --filter dominio:cca --show-chunksmeri-cli.bat → meri-cli.py → main.py (cli function)

```

# 4. Ver detalles de un documento
meri-cli db show --id "doc_12345"
```

## Archivos en este directorio

- `main.py` - Implementación principal del CLI con Click
- `db_commands.py` - Comandos de gestión de base de datos
- `meri-cli.py` - Script ejecutable Python
- `meri-cli.bat` - Script batch para Windows
- `meri-cli.ps1` - Script PowerShell
- `install-meri-cli.ps1` - Instalador para uso global
- `README.md` - Documentación completa del módulo
- `GUIA-RAPIDA.md` - Esta guía de referencia rápida
- `tasks-db.md` - Documentación de tareas de DB

## Parámetros importantes

### Para crawl (obligatorios)
- `--url`: URL inicial para el crawling
- `--dominio`: Dominio al que pertenece la información

### Para db show (obligatorio)
- `--id`: ID del documento a mostrar

### Para db delete (uno obligatorio)
- `--id`: ID del documento
- `--url`: URL del documento
- `--source-path`: Ruta del archivo fuente

## Requisitos
- Python 3.10+
- Dependencias: Click, requests, PyYAML, urllib3, python-dotenv, tabulate
- Servidor FastAPI ejecutándose en http://localhost:8000 (configurable con --api-host)
- Dominio debe estar en la lista de dominios permitidos en `crawler_config.yaml`
- Variables de entorno configuradas en `.env`

## Endpoints API utilizados
- `/crawl-and-process` - Para comandos crawl
- `/list-documents` - Para db list
- `/show-document` - Para db show
- `/delete-document` - Para db delete --id
- `/delete-document-by-url` - Para db delete --url
- `/delete-document-by-source-path` - Para db delete --source-path
- `/count-documents` - Para db count

## Estructura de ejecución
```
meri-cli.bat → meri-cli.py → main.py (cli function) → db_commands.py (for db operations)
```