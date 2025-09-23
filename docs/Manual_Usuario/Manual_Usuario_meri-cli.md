# Manual de Usuario - Herramienta CLI MeriBot (meri-cli)

**Versión**: 1.0  
**Fecha**: 23 de Septiembre, 2025  
**Audiencia**: Administradores técnicos, DevOps y desarrolladores  
---
# Índice
- [Que es meri-cli](#que-es-meri-cli)
- [Requisitos previos y configuracion](#requisitos-previos-y-configuracion)
- [Instalacion de meri-cli](#instalacion-de-meri-cli)
- [Comandos disponibles](#comandos-disponibles)
- [Comando crawl - extraccion y procesamiento](#comando-crawl---extraccion-y-procesamiento)
- [Ejemplos practicos de crawling](#ejemplos-practicos-de-crawling)
- [Comando db - gestion de base de datos](#comando-db---gestion-de-base-de-datos)
- [Configuracion avanzada](#configuracion-avanzada)
- [Interpretacion de resultados](#interpretacion-de-resultados)
- [Solucion de problemas comunes](#solucion-de-problemas-comunes)
- [Mejores practicas](#mejores-practicas)
- [Comandos de diagnostico](#comandos-de-diagnostico)
- [Automatizacion y scripting](#automatizacion-y-scripting)
- [Soporte y contacto](#soporte-y-contacto)
- [Proximas funcionalidades roadmap](#proximas-funcionalidades-roadmap)
- [Conclusion](#conclusion)
---
## Que es meri-cli

`meri-cli` es la herramienta oficial de línea de comandos para la administración y gestión del sistema MeriBot. Proporciona una interfaz unificada para realizar operaciones de crawling, procesamiento de documentos, gestión de la base de datos vectorial y monitoreo del sistema.

### ✨ **Capacidades principales:**
- 🕷️ **Crawling automatizado** con configuración avanzada
- 💾 **Gestión de base vectorial** (ChromaDB) completa
- 📊 **Monitoreo y estadísticas** del sistema
- 🔧 **Administración de documentos** con metadatos
- 🛡️ **Validación y seguridad** integradas
- 🎯 **Modo simulación** para pruebas seguras
- 📋 **Reportes detallados** de todas las operaciones

---

## Requisitos previos y configuracion

### Configuración del Sistema
1. **Servidor MeriBot activo**: meri-cli se comunica con la API del sistema
2. **Python 3.12+** instalado y configurado
3. **Dependencias instaladas**: Todas las librerías de `requirements.txt`
4. **Permisos de ejecución**: Para scripts PowerShell (Windows)

### Iniciar el Sistema MeriBot
**IMPORTANTE**: Antes de usar cualquier comando de meri-cli, asegúrate de que el servidor esté corriendo:

```powershell
cd meribot_app
python start_server_direct.py
```

Esto iniciará:
- 🌐 **API Server**: http://localhost:8000
- 🔧 **Crawler API**: http://localhost:8000/crawler/*
- 📊 **Admin Interface**: http://localhost:8000/docs
- 💬 **Widget**: http://localhost:8000/widget

> **💡 Tip**: Mantén una terminal con el servidor corriendo y usa otra para los comandos meri-cli

---

## Instalacion de meri-cli

### Opción 1: Uso Directo (Recomendado para desarrollo)
```powershell
# Navegar al directorio meri-cli
cd meribot_app\meribot\meri-cli

# Ejecutar comandos directamente
python main.py --help
python main.py crawl --url "https://ejemplo.com" --dominio "test"
```

### Opción 2: Usando Scripts de Conveniencia
```powershell
# En Windows (PowerShell)
cd meribot_app\meribot\meri-cli
.\meri-cli.ps1 --help

# En Windows (CMD)
cd meribot_app\meribot\meri-cli
meri-cli.bat --help
```

### Opción 3: Instalación Global (Para uso avanzado)
```powershell
cd meribot_app\meribot\meri-cli
.\install-meri-cli.ps1 -Install

# Reiniciar terminal, luego usar desde cualquier ubicación:
meri-cli --help
```

---

## Comandos disponibles

### Vista General de Comandos
```powershell
# Ver ayuda principal
python main.py --help

# Comandos principales disponibles:
python main.py crawl      # Crawling y procesamiento de documentos
python main.py db         # Gestión de base de datos vectorial
```

---

## Comando crawl - extraccion y procesamiento

### Sintaxis Básica
```powershell
python main.py crawl --url "URL_INICIAL" --dominio "DOMINIO_TEMATICO"
```

### Parámetros Obligatorios
- `--url`: URL inicial para el crawling (debe incluir http/https)
- `--dominio`: Dominio temático al que pertenece la información

### Parámetros Opcionales Completos
- `--max-depth INTEGER`: Profundidad máxima de navegación (default: 4)
- `--max-pages INTEGER`: Número máximo de páginas a explorar
- `--include REGEX`: Patrón regex para incluir URLs específicas
- `--exclude REGEX`: Patrón regex para excluir URLs específicas
- `--formats TEXT`: Formatos a recolectar (default: html,pdf,docx,xlsx)
- `--output DIRECTORY`: Directorio destino para documentos descargados
- `--update-only`: Solo actualizar documentos nuevos o modificados
- `--dry-run`: Simular crawling sin procesar realmente
- `--manual URLS`: Lista de URLs separadas por comas para procesar manualmente
- `--api-host URL`: Host del API de MeriBot (default: http://localhost:8000)

---

## Ejemplos practicos de crawling

### Ejemplo 1: Crawling Básico
```powershell
python main.py crawl \
  --url "https://intranet.capgemini.com/policies" \
  --dominio "RRHH"
```
**Resultado**: Extrae políticas de RRHH con configuración por defecto

### Ejemplo 2: Crawling Controlado
```powershell
python main.py crawl \
  --url "https://cca.capgemini.com/procedures" \
  --dominio "Procesos" \
  --max-depth 2 \
  --max-pages 25
```
**Resultado**: Limita la profundidad y número de páginas para sitios grandes

### Ejemplo 3: Crawling con Filtros Avanzados
```powershell
python main.py crawl \
  --url "https://intranet.capgemini.com" \
  --dominio "IT" \
  --include ".*/(support|help|documentation)/.*" \
  --exclude ".*/temp/.*|.*/draft/.*"
```
**Resultado**: Solo incluye páginas de soporte/ayuda, excluye temporales

### Ejemplo 4: Procesamiento Manual de URLs
```powershell
python main.py crawl \
  --url "https://base.com" \
  --dominio "Calidad" \
  --manual "https://site.com/manual1.pdf,https://site.com/guide.html,https://site.com/process.docx"
```
**Resultado**: Procesa solo las URLs especificadas manualmente

### Ejemplo 5: Simulación Segura (Dry Run)
```powershell
python main.py crawl \
  --url "https://ejemplo.com" \
  --dominio "test" \
  --dry-run
```
**Resultado**: Muestra qué haría sin ejecutar realmente

### Ejemplo 6: Solo PDFs y Word
```powershell
python main.py crawl \
  --url "https://documents.capgemini.com" \
  --dominio "Documentacion" \
  --formats "pdf,docx" \
  --output "./documentos_descargados"
```
**Resultado**: Solo procesa documentos PDF y Word, los guarda localmente

---

## Comando db - gestion de base de datos

### Subcomandos Disponibles
```powershell
python main.py db --help    # Ver ayuda de comandos DB

# Subcomandos principales:
python main.py db list      # Listar documentos
python main.py db delete    # Eliminar documentos  
python main.py db info      # Información detallada
python main.py db stats     # Estadísticas generales
```

### 1. Listar Documentos (`db list`)
```powershell
# Listar todos los documentos
python main.py db list

# Filtrar por dominio
python main.py db list --filter dominio:RRHH

# Mostrar con número de chunks
python main.py db list --show-chunks

# Combinar filtro y chunks
python main.py db list --filter dominio:IT --show-chunks
```

**Salida típica:**
```
| ID       | Nombre                    | Dominio | Fecha ingreso | Chunks |
|----------|---------------------------|---------|---------------|--------|
| doc_001  | política_vacaciones.pdf   | RRHH    | 2025-09-20    | 15     |
| doc_002  | manual_onboarding.html    | RRHH    | 2025-09-21    | 8      |
| doc_003  | guía_desarrollo.docx      | IT      | 2025-09-22    | 23     |
```

### 2. Información Detallada (`db info`)
```powershell
# Ver detalles completos de un documento
python main.py db info --id "doc_001"
```

**Salida típica:**
```
Detalles del documento: doc_001
----------------------------------------
id             : doc_001
title          : política_vacaciones.pdf
domain         : RRHH
url            : https://intranet.capgemini.com/hr/vacation-policy.pdf
created_date   : 2025-09-20 14:30:15
size           : 2.4 MB
chunks         : 15

Chunks asociados:
Chunk 0: id=chunk_001_01
Este documento establece las políticas de vacaciones para todos los empleados de Capgemini...

Chunk 1: id=chunk_001_02
Las solicitudes de vacaciones deben realizarse con al menos 15 días de anticipación...
```

### 3. Eliminar Documentos (`db delete`)
```powershell
# Eliminar por ID
python main.py db delete --id "doc_001"

# Eliminar por URL original
python main.py db delete --url "https://intranet.capgemini.com/policy.pdf"

# Eliminar por ruta fuente
python main.py db delete --source-path "/documents/manual.pdf"
```

**⚠️ Importante**: Este comando elimina el documento y TODOS sus chunks asociados permanentemente.

### 4. Estadísticas Generales (`db stats`)
```powershell
python main.py db stats
```

**Salida típica:**
```
📊 Estadísticas de la Base Vectorial
=====================================
Total documentos: 127
Total chunks: 2,847
Dominios disponibles: RRHH (45), IT (38), Procesos (32), Calidad (12)
Último procesamiento: 2025-09-23 10:15:32
Tamaño base de datos: 245.7 MB
Estado: Saludable ✅
```

---

## Configuracion avanzada

### Archivo de Configuración (`crawler_config.yaml`)
```yaml
# Dominios permitidos para crawling
allowed_domains:
  - "capgemini.com"
  - "cca.capgemini.com" 
  - "intranet.capgemini.com"
  - "training.capgemini.com"

# Configuración de procesamiento
processing:
  chunk_size: 1000
  chunk_overlap: 200
  max_depth: 4
  max_pages: 100
  timeout: 30

# Formatos soportados
supported_formats:
  - "html"
  - "pdf"
  - "docx"
  - "xlsx"
  - "txt"
  - "md"
```

### Variables de Entorno Utilizadas
meri-cli utiliza las siguientes variables desde `.env`:
```env
# API del sistema
MERIBOT_CRAWLER_URL=http://localhost:8000

# Azure OpenAI (para embeddings)
AZURE_OPENAI_API_KEY=***
AZURE_OPENAI_ENDPOINT=***
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small

# Base de datos vectorial
CHROMA_PERSIST_DIRECTORY=chroma_data
CHROMA_COLLECTION_NAME=meri_chunks

# Configuración de logs
MERIBOT_LOG_LEVEL=INFO
MERIBOT_LOG_FILE=logs/meribot_core.log
```

---

## Interpretacion de resultados

### Salida Típica del Comando Crawl
```
Iniciando proceso de crawling...
URL inicial: https://intranet.capgemini.com/policies
Dominio: RRHH
Profundidad máxima: 4

Conectando con el servicio de crawling: http://localhost:8000/crawler/crawl-and-process

Crawling completado exitosamente!

Resultados del procesamiento (18 archivos):
  ✅ política_vacaciones.pdf: Procesado y almacenado correctamente (15 chunks)
  ✅ manual_gastos.html: Procesado y almacenado correctamente (8 chunks)
  ⚠️  formulario_baja.docx: Advertencia: Documento ya existía, actualizado (12 chunks)
  ❌ guía_onboarding.pdf: Error: No se pudo procesar el documento

📈 Resumen Final:
  ✅ Exitosos: 14 documentos (387 chunks generados)
  ❌ Errores: 2 documentos
  ⚠️  Advertencias: 2 documentos
  ⏱️ Tiempo total: 2m 45s
  💾 Datos almacenados: 15.7 MB
```

### Estados de Procesamiento Explicados

#### ✅ **Exitosos**
- Documento descargado sin problemas
- Contenido extraído y parseado correctamente
- Embeddings generados con Azure OpenAI
- Chunks almacenados en ChromaDB
- Metadatos guardados correctamente

#### ⚠️ **Advertencias**
- Documento ya existía en la base (actualizado)
- Formato parcialmente compatible (algunos elementos no procesados)
- Chunks duplicados detectados y omitidos
- Problemas menores de parseo (contenido recuperado parcialmente)

#### ❌ **Errores**
- No se pudo acceder al documento (404, permisos, etc.)
- Formato completamente incompatible
- Error en generación de embeddings (problema API)
- Problema de almacenamiento en ChromaDB
- Timeout de procesamiento

---

## Solucion de problemas comunes

### **Problema**: "Error de conexión con el API"
**Síntomas**: `[ERROR] No se pudo conectar al endpoint del crawler`  
**Causas**: Servidor MeriBot no está corriendo  
**Solución**:
```powershell
# Verificar que el servidor esté corriendo
cd meribot_app
python start_server_direct.py

# En otra terminal, probar conectividad
curl http://localhost:8000/docs
```

### **Problema**: "Dominio no permitido"
**Síntomas**: `Error: Dominio 'ejemplo.com' no está en la lista de dominios permitidos`  
**Causas**: El dominio no está configurado en `crawler_config.yaml`  
**Solución**:
1. Editar `meribot_app/crawler_config.yaml`
2. Añadir el dominio a `allowed_domains`
3. Reiniciar el servidor

### **Problema**: "No se pueden procesar algunos documentos"
**Síntomas**: Múltiples errores de procesamiento  
**Causas**: Formatos no soportados, documentos corruptos, permisos  
**Solución**:
```powershell
# Verificar formatos específicos
python main.py crawl --url "URL" --dominio "DOMINIO" --formats "html,pdf"

# Usar dry-run para verificar acceso
python main.py crawl --url "URL" --dominio "DOMINIO" --dry-run

# Procesar URLs manualmente para diagnóstico
python main.py crawl --url "URL" --dominio "DOMINIO" --manual "URL_ESPECIFICA"
```

### **Problema**: "Timeout en el procesamiento"
**Síntomas**: Proceso se cuelga o falla por tiempo  
**Causas**: Documentos muy grandes, sitios lentos, muchas páginas  
**Solución**:
```powershell
# Reducir alcance
python main.py crawl --url "URL" --dominio "DOMINIO" --max-pages 10 --max-depth 2

# Procesar en lotes
python main.py crawl --url "URL" --dominio "DOMINIO" --manual "URL1,URL2,URL3"
```

### **Problema**: "Embeddings no se generan"
**Síntomas**: Documentos procesados pero sin chunks en la base  
**Causas**: Problemas con Azure OpenAI API  
**Solución**:
1. Verificar variables de entorno `AZURE_OPENAI_*`
2. Comprobar conectividad con Azure
3. Verificar quotas y límites de API
4. Revisar logs: `logs/meribot_core.log`

---

## Mejores practicas

### ✅ **Estrategia de Crawling Eficiente**

1. **Planificación previa**:
   ```powershell
   # Siempre usar dry-run primero
   python main.py crawl --url "URL" --dominio "DOMINIO" --dry-run
   ```

2. **Crawling incremental**:
   ```powershell
   # Primera vez: crawling completo
   python main.py crawl --url "URL" --dominio "DOMINIO" --max-depth 3
   
   # Actualizaciones: solo nuevos
   python main.py crawl --url "URL" --dominio "DOMINIO" --update-only
   ```

3. **Control de recursos**:
   ```powershell
   # Para sitios grandes, limitar alcance
   python main.py crawl --url "URL" --dominio "DOMINIO" --max-pages 50 --max-depth 2
   ```

### ✅ **Gestión de Base de Datos**

1. **Monitoreo regular**:
   ```powershell
   # Revisar estadísticas semanalmente
   python main.py db stats
   
   # Listar documentos recientes
   python main.py db list --show-chunks
   ```

2. **Mantenimiento de contenido**:
   ```powershell
   # Eliminar documentos obsoletos
   python main.py db delete --url "URL_OBSOLETA"
   
   # Verificar detalles antes eliminar
   python main.py db info --id "DOCUMENT_ID"
   ```

### ❌ **Evitar estos errores comunes**

- ❌ Ejecutar crawling sin verificar el servidor
- ❌ No usar dry-run en sitios desconocidos
- ❌ Crawling masivo sin límites de profundidad
- ❌ Ignorar los mensajes de error y advertencia
- ❌ No verificar la configuración de dominios permitidos

---

## Comandos de diagnostico

### Verificar Estado del Sistema
```powershell
# Verificar conectividad con API
curl http://localhost:8000/docs

# Probar endpoint de crawler
curl http://localhost:8000/crawler/health

# Ver logs en tiempo real
Get-Content logs/meribot_core.log -Wait -Tail 10
```

### Scripts de Diagnóstico
```powershell
# Verificar configuración
python -c "import yaml; print(yaml.safe_load(open('crawler_config.yaml')))"

# Verificar variables de entorno
python -c "import os; print('Azure API Key:', bool(os.getenv('AZURE_OPENAI_API_KEY')))"

# Test de conectividad básico
python -c "import requests; print(requests.get('http://localhost:8000/docs').status_code)"
```

---

## Automatizacion y scripting

### Scripts de Mantenimiento Regular

#### Script de Crawling Semanal
```powershell
# crawl_weekly.ps1
$dominios = @("RRHH", "IT", "Procesos", "Calidad")
$base_urls = @(
    "https://intranet.capgemini.com/hr",
    "https://intranet.capgemini.com/it", 
    "https://intranet.capgemini.com/processes",
    "https://intranet.capgemini.com/quality"
)

for ($i = 0; $i -lt $dominios.Length; $i++) {
    Write-Host "Procesando dominio: $($dominios[$i])"
    python main.py crawl --url $base_urls[$i] --dominio $dominios[$i] --update-only
}
```

#### Script de Limpieza Mensual
```powershell
# cleanup_monthly.ps1
Write-Host "Obteniendo estadísticas antes de limpieza:"
