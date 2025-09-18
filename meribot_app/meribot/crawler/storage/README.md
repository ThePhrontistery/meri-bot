# Capa de Almacenamiento de Datos

## Descripción
Este módulo gestiona el almacenamiento y recuperación de datos vectoriales utilizando ChromaDB. Proporciona una capa de abstracción sobre la base de datos vectorial para facilitar su uso en la aplicación.

## Características Principales
- Interfaz unificada para operaciones CRUD en ChromaDB
- Gestión de colecciones de documentos
- Búsqueda semántica eficiente
- Caché de consultas frecuentes
- Respaldo y restauración de datos

## Estructura del Módulo
```
services/storage/
├── __init__.py
├── vector_store.py    # Clase principal para el almacenamiento vectorial
├── models.py          # Modelos de datos para documentos y resultados
├── query_builder.py   # Constructor de consultas avanzadas
└── backup_manager.py  # Utilidades para respaldo y restauración
```

## Uso Básico

```python
from meribot.services.storage import VectorStore

# Inicializar el almacenamiento
store = VectorStore(collection_name="documentos")

# Insertar documentos
docs = [
    {"text": "Texto del documento 1", "metadata": {"source": "intranet"}},
    {"text": "Texto del documento 2", "metadata": {"source": "manuales"}}
]
store.add_documents(docs)

# Buscar documentos similares
results = store.similarity_search("término de búsqueda", k=3)
```

## Configuración

### Variables de Entorno
```ini
# Configuración de ChromaDB
CHROMA_DB_PATH=./chroma_data
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Configuración de caché
CACHE_ENABLED=true
CACHE_TTL=3600  # segundos
```

### Configuración Avanzada
```python
from chromadb.config import Settings

chroma_settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data",
    anonymized_telemetry=False
)

store = VectorStore(
    collection_name="documentos",
    embedding_function=embedding_fn,
    client_settings=chroma_settings
)
```

## Operaciones Principales

### Búsqueda por Similitud
```python
# Búsqueda básica
results = store.similarity_search("texto de búsqueda", k=5)

# Búsqueda con filtros
filters = {"source": "intranet", "year": {"$gte": 2022}}
results = store.similarity_search("texto", k=5, filter=filters)
```

### Gestión de Colecciones
```python
# Listar colecciones
collections = store.list_collections()

# Eliminar colección
store.delete_collection("coleccion_antigua")
```

## Rendimiento
- Índices optimizados para búsqueda semántica
- Caché de consultas frecuentes
- Compresión de embeddings para ahorrar espacio
- Batch processing para inserciones masivas

## Mantenimiento

### Respaldo de Datos
```bash
# Crear respaldo
python -m meribot.services.storage.backup_manager --backup --output=backups/backup_$(date +%Y%m%d).zip

# Restaurar desde respaldo
python -m meribot.services.storage.backup_manager --restore --input=backups/backup_20230808.zip
```

### Monitorización
Se recomienda monitorear:
- Uso de memoria
- Tiempo de respuesta de consultas
- Tamaño de la base de datos
- Tasa de aciertos en caché

## Dependencias
- ChromaDB
- Numpy
- tqdm (para barras de progreso)
- orjson (para serialización eficiente)
