# Capa de Recopilación de Datos

## Descripción
Este módulo se encarga de la extracción, transformación y carga (ETL) de datos desde la intranet de CECA hacia la base de datos vectorial. Incluye herramientas para web scraping, procesamiento de documentos y generación de embeddings.

## Características Principales
- Extracción de datos de múltiples fuentes (web, documentos, APIs)
- Procesamiento de texto (limpieza, normalización, chunking)
- Generación de embeddings con múltiples modelos
- Inserción eficiente en ChromaDB
- Programación de tareas con cron

## Estructura del Módulo
```
crawler/
├── __init__.py
├── scraper.py          # Clase base para web scraping
├── document_loader.py  # Carga de diferentes tipos de documentos
├── text_processor.py   # Procesamiento de texto
├── embeddings.py       # Generación de embeddings
└── tasks/              # Tareas programadas
    ├── daily_sync.py   # Sincronización diaria
    └── full_index.py   # Reindexado completo
```

## Uso Básico

```python
from meribot.crawler import WebScraper, DocumentProcessor

# Inicializar el scraper
scraper = WebScraper(base_url="https://cca.capgemini.com/web/home")

# Extraer contenido
content = scraper.scrape("/ruta/documento")

# Procesar texto
processor = DocumentProcessor()
chunks = processor.process(content, chunk_size=1000)
```

## Configuración
El módulo se configura mediante variables de entorno:

```ini
# Configuración del scraper
SCRAPER_USER_AGENT=MeriBot/1.0
SCRAPER_DELAY=1.0  # segundos entre peticiones

# Configuración de ChromaDB
CHROMA_PATH=./chroma_data
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Tareas Programadas

### Sincronización Diaria
```bash
# Ejecutar la tarea de sincronización diaria
python -m meribot.crawler.tasks.daily_sync
```

### Reindexado Completo
```bash
# Reindexar todos los documentos
python -m meribot.crawler.tasks.full_index --force
```

## Manejo de Errores
Los errores se registran en `logs/crawler.log` con diferentes niveles de severidad:
- ERROR: Errores críticos que requieren atención
- WARNING: Problemas no críticos
- INFO: Información sobre el progreso
- DEBUG: Información detallada para depuración

## Dependencias
- BeautifulSoup4
- Requests
- ChromaDB
- Sentence-Transformers
- Python-dotenv

## Notas de Implementación
- El scraper sigue las directrices de robots.txt
- Se implementa respeto a los encabezados `Retry-After`
- Se utiliza caché para evitar solicitudes duplicadas
- Los datos sensibles nunca se registran
