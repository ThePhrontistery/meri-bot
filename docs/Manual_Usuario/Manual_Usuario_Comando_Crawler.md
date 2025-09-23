# Manual de Usuario - Comando Crawler MeriBot

**Versión**: 1.0  
**Fecha**: 23 de Septiembre, 2025  
**Audiencia**: Administradores técnicos y DevOps  
---
# Índice
- [Que es el Crawler de MeriBot](#que-es-el-crawler-de-meribot)
- [Requisitos previos](#requisitos-previos)
- [Configuracion del Crawler](#configuracion-del-crawler)
- [Comandos del Crawler](#comandos-del-crawler)
- [Ejemplos practicos](#ejemplos-practicos)
- [Interpretacion de resultados](#interpretacion-de-resultados)
- [Comandos de administracion de base de datos](#comandos-de-administracion-de-base-de-datos)
- [Configuracion avanzada](#configuracion-avanzada)
- [Solucion de problemas](#solucion-de-problemas)
- [Mejores practicas](#mejores-practicas)
- [Monitoreo y mantenimiento](#monitoreo-y-mantenimiento)
- [Soporte tecnico](#soporte-tecnico)
- [Automatizacion proximamente](#automatizacion-proximamente)
---

## Que es el Crawler de MeriBot

El Crawler es una herramienta de línea de comandos que permite extraer, procesar y almacenar documentos de sitios web internos para alimentar la base de conocimiento de MeriBot. Convierte páginas web, PDFs, documentos Office y otros formatos en información estructurada que el chatbot puede utilizar para responder consultas.

### Capacidades del Crawler:
- Extracción de contenido de sitios web
- Procesamiento de PDFs, Word, Excel
- Navegación automática con control de profundidad
- Clasificación por dominios temáticos
- Generación automática de embeddings
- Almacenamiento en base vectorial (ChromaDB)
- Detección de contenido duplicado
- Reportes detallados de procesamiento

---

## Requisitos previos

### Configuración del Sistema
1. **Servidor MeriBot activo**: El crawler se comunica con la API
2. **Python 3.12+** instalado
3. **Dependencias instaladas**: Ver `requirements.txt`
4. **Archivo de configuración**: `crawler_config.yaml` configurado

### Iniciar el Sistema
Antes de usar el crawler, asegúrate de que el servidor esté corriendo:

```powershell
cd meribot_app
python start_server_direct.py
```

Esto iniciará:
- **API Server**: http://localhost:8000
- **Crawler API**: http://localhost:8000/crawler/*
- **Documentación**: http://localhost:8000/docs

---

## Configuracion del Crawler

### Archivo de Configuración (`crawler_config.yaml`)

```yaml
# Dominios permitidos para crawling
allowed_domains:
  - "capgemini.com"
  - "cca.capgemini.com"
  - "intranet.capgemini.com"
  - "ejemplo.com"

# Configuración de ChromaDB
chroma:
  persist_directory: "chroma_data"
  collection_name: "meri_chunks"

# Configuración de procesamiento
processing:
  chunk_size: 1000
  chunk_overlap: 200
  max_depth: 4
  max_pages: 100
```

### Variables de Entorno Requeridas
El crawler utiliza las siguientes variables desde el archivo `.env`:

```env
# Azure OpenAI para embeddings
AZURE_OPENAI_API_KEY=tu_clave_aqui
AZURE_OPENAI_ENDPOINT=https://tu-endpoint.openai.azure.com/
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small

# Configuración de base de datos
CHROMA_PERSIST_DIRECTORY=chroma_data
CHROMA_COLLECTION_NAME=meri_chunks

# Configuración del crawler
CRAWLER_CONFIG_PATH=crawler_config.yaml
```

---

## Comandos del Crawler

### Comando Principal: `crawl`

#### Sintaxis Básica
```powershell
python -m meribot.meri-cli.main crawl --url "https://ejemplo.com" --dominio "ejemplo.com"
```

#### Parámetros Obligatorios
- `--url`: URL inicial para el crawling
- `--dominio`: Dominio temático al que pertenece la información

#### Parámetros Opcionales
- `--max-depth`: Profundidad máxima de navegación (default: 4)
- `--max-pages`: Número máximo de páginas a explorar
- `--include`: Patrón regex para incluir URLs
- `--exclude`: Patrón regex para excluir URLs
- `--formats`: Formatos a recolectar (default: html,pdf,docx,xlsx)
- `--output`: Directorio destino para documentos
- `--update-only`: Solo actualizar documentos nuevos o modificados
- `--dry-run`: Simular crawling sin descargar
- `--manual`: Lista de URLs separadas por comas
- `--api-host`: Host del API (default: http://localhost:8000)

---

## Ejemplos practicos

### Ejemplo 1: Crawling Básico
```powershell
python -m meribot.meri-cli.main crawl \
  --url "https://intranet.capgemini.com/policies" \
  --dominio "RRHH"
```

### Ejemplo 2: Crawling con Límites
```powershell
python -m meribot.meri-cli.main crawl \
  --url "https://cca.capgemini.com/procedures" \
  --dominio "Procesos" \
  --max-depth 2 \
  --max-pages 50
```

### Ejemplo 3: Crawling con Filtros
```powershell
python -m meribot.meri-cli.main crawl \
  --url "https://intranet.capgemini.com" \
  --dominio "IT" \
  --include ".*/(support|help|documentation)/.*" \
  --exclude ".*/temp/.*"
```

### Ejemplo 4: URLs Manuales Específicas
```powershell
python -m meribot.meri-cli.main crawl \
  --url "https://base.com" \
  --dominio "Calidad" \
  --manual "https://site.com/doc1.pdf,https://site.com/doc2.html"
```

### Ejemplo 5: Simulación (Dry Run)
```powershell
python -m meribot.meri-cli.main crawl \
  --url "https://ejemplo.com" \
  --dominio "test" \
  --dry-run
```

---

## Interpretacion de resultados

### Salida Típica del Comando
```
Iniciando proceso de crawling...
URL inicial: https://intranet.capgemini.com/policies
Dominio: RRHH
Profundidad máxima: 4

Conectando con el servicio de crawling: http://localhost:8000/crawler/crawl-and-process

Crawling completado exitosamente!

Resultados del procesamiento (15 archivos):
  policy_vacations.pdf: Procesado y almacenado correctamente
  procedure_expenses.html: Procesado y almacenado correctamente
  form_sick_leave.docx: Advertencia: Documento ya existía, actualizado
  guide_onboarding.pdf: Error: No se pudo procesar el documento

📈 Resumen:
  ✅ Exitosos: 12
  ❌ Errores: 1
  ⚠️  Advertencias: 2
```

### Estados de Procesamiento

#### ✅ **Exitosos**
- Documento descargado correctamente
- Contenido extraído y procesado
- Embeddings generados
- Almacenado en ChromaDB

#### ⚠️ **Advertencias**
- Documento ya existía (actualizado)
- Formato parcialmente compatible
- Algunos elementos no procesados

#### ❌ **Errores**
- No se pudo acceder al documento
- Formato no compatible
- Error en generación de embeddings
- Problema de almacenamiento

---

## Comandos de administracion de base de datos

### Listar Documentos
```powershell
python -m meribot.meri-cli.main db list-documents
```

### Eliminar Documento por ID
```powershell
python -m meribot.meri-cli.main db delete --id "documento_123"
```

### Eliminar por URL
```powershell
python -m meribot.meri-cli.main db delete --url "https://ejemplo.com/doc.pdf"
```

### Eliminar por Source Path
```powershell
python -m meribot.meri-cli.main db delete --source-path "/documents/policy.pdf"
```

### Obtener Información de Documento
```powershell
python -m meribot.meri-cli.main db info --id "documento_123"
```

### Obtener Estadísticas de la Base
```powershell
python -m meribot.meri-cli.main db stats
```

---

## Configuracion avanzada

### Dominios Temáticos Disponibles
Configure en `crawler_config.yaml` los dominios según su organización:

```yaml
domains:
  RRHH:
    - "recursos-humanos"
    - "personal"
    - "nominas"
  IT:
    - "tecnologia"
    - "sistemas"
    - "soporte"
  Procesos:
    - "procedimientos"
    - "metodologias"
    - "calidad"
```

### Formatos Soportados
- **HTML**: Páginas web estándar
- **PDF**: Documentos Adobe PDF
- **DOCX**: Documentos Microsoft Word
- **XLSX**: Hojas de cálculo Excel
- **TXT**: Archivos de texto plano
- **MD**: Archivos Markdown

### Patrones de Inclusión/Exclusión
Utiliza expresiones regulares para controlar qué URLs procesar:

```powershell
# Incluir solo páginas de documentación
--include ".*/docs?/.*"

# Excluir archivos temporales y de prueba
--exclude ".*/temp/.*|.*/test/.*"

# Incluir múltiples patrones
--include ".*/(policies|procedures|guides)/.*"
```

---

## Solucion de problemas

### **Problema**: "Dominio no permitido"
**Causa**: El dominio no está en `allowed_domains` del archivo de configuración.  
**Solución**: 
1. Editar `crawler_config.yaml`
2. Añadir el dominio a la lista `allowed_domains`
3. Reiniciar el servidor

### **Problema**: "Error de conexión con el API"
**Causa**: El servidor MeriBot no está corriendo.  
**Solución**:
```powershell
cd meribot_app
python start_server_direct.py
```

### **Problema**: "No se pueden procesar algunos documentos"
**Causa**: Formato no soportado o documento corrupto.  
**Solución**:
1. Verificar que el formato esté en la lista soportada
2. Intentar descargar el documento manualmente
3. Usar `--formats` para especificar formatos específicos

### **Problema**: "Timeout en el procesamiento"
**Causa**: Documentos muy grandes o muchas páginas.  
**Solución**:
1. Usar `--max-pages` para limitar el alcance
2. Reducir `--max-depth`
3. Procesar en lotes más pequeños

### **Problema**: "Embeddings no se generan"
**Causa**: Problemas con Azure OpenAI.  
**Solución**:
1. Verificar las variables de entorno `AZURE_OPENAI_*`
2. Comprobar conectividad con Azure
3. Verificar quotas y límites de API

---

## Mejores practicas

### Recomendaciones:

1. **Planifica el crawling**: Usa `--dry-run` primero para evaluar el alcance
2. **Controla la profundidad**: Empieza con `--max-depth 2` para sitios grandes
3. **Usa filtros específicos**: Evita contenido irrelevante con `--include/--exclude`
4. **Procesa por dominios**: Organiza el contenido por área temática
5. **Monitorea recursos**: El procesamiento puede consumir memoria y CPU
6. **Valida resultados**: Revisa los logs para identificar problemas

### Estrategia de Crawling Incremental:

1. **Primera ejecución**: Crawling completo con `--max-depth 3`
2. **Actualizaciones**: Usar `--update-only` para nuevos contenidos
3. **Mantenimiento**: Ejecutar crawling completo semanalmente
4. **Monitoreo**: Revisar estadísticas de la base regularmente

### Evita:

- Crawling sin límites de profundidad en sitios grandes
- Procesamiento simultáneo de múltiples dominios
- Ignorar los logs de error
- Crawling frecuente de contenido estático

---

## Monitoreo y mantenimiento

### Comandos de Monitoreo
```powershell
# Ver estadísticas de la base
python -m meribot.meri-cli.main db stats

# Listar documentos recientes
python -m meribot.meri-cli.main db list-documents | head -20

# Verificar conectividad con el API
curl http://localhost:8000/crawler/health
```

### Mantenimiento Regular
1. **Semanal**: Crawling incremental de fuentes principales
2. **Mensual**: Crawling completo y limpieza de duplicados
3. **Trimestral**: Revisión de configuración y dominios
4. **Anual**: Optimización de índices y rendimiento

---

## Soporte tecnico

### **Para problemas con el crawler:**

**Logs del sistema:**
- Logs del crawler: `logs/meribot_crawler.log`
- Logs del servidor: `logs/meribot_core.log`

**Comandos de diagnóstico:**
```powershell
# Verificar configuración
python -m meribot.meri-cli.main config validate

# Probar conectividad
python -m meribot.meri-cli.main crawler test-connection

# Ver logs en tiempo real
tail -f logs/meribot_crawler.log
```

**Contacto:**
- Email técnico: [devops-meribot@capgemini.com]
- Ticket sistema: Portal IT C&CA
- Documentación: `/docs/`

---

## Automatizacion proximamente

### Scheduler Automático
```powershell
# Configurar crawling automático
python -m meribot.meri-cli.main scheduler setup \
  --frequency weekly \
  --domains "RRHH,IT,Procesos"

# Ver tareas programadas
python -m meribot.meri-cli.main scheduler list

# Pausar/reanudar scheduler
python -m meribot.meri-cli.main scheduler pause
python -m meribot.meri-cli.main scheduler resume
```

---

*© 2025 Capgemini - Cloud & Custom Applications. Manual de Usuario Crawler MeriBot v1.0*
