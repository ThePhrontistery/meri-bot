# Capa de Lógica de la Aplicación

## Descripción
Este módulo contiene la lógica principal del chatbot MeriBot, incluyendo el procesamiento de lenguaje natural, la gestión de conversaciones y la integración con servicios externos como LangChain y ChromaDB.

## Características Principales
- Procesamiento de lenguaje natural con LangChain
- Gestión de contexto de conversación
- Integración con bases de datos vectoriales
- Sistema de plugins para funcionalidades extendidas
- Caché de respuestas frecuentes

## Estructura del Módulo
```
core/
├── __init__.py
├── chat_engine.py      # Motor principal del chat
├── conversation.py     # Gestión de conversaciones
├── plugins/            # Plugins de funcionalidad
│   ├── base_plugin.py  # Clase base para plugins
│   ├── faq_plugin.py   # Plugin para preguntas frecuentes
│   └── doc_search.py   # Búsqueda en documentación
└── utils/              # Utilidades
    ├── cache.py        # Sistema de caché
    └── logger.py       # Utilidades de registro
```

## Uso Básico

```python
from meribot.core.chat_engine import ChatEngine

# Inicializar el motor de chat
chat_engine = ChatEngine()

# Procesar un mensaje
response = chat_engine.process_message(
    user_message="¿Cómo solicito vacaciones?",
    conversation_id="conv_123"
)
```

## Configuración
El módulo se puede configurar mediante variables de entorno o un archivo de configuración:

```ini
[core]
model_name = gpt-3.5-turbo
max_tokens = 1000
temperature = 0.7
cache_ttl = 3600  # segundos
```

## Plugins
Los plugins permiten extender la funcionalidad del chatbot. Para crear un nuevo plugin:

```python
from meribot.core.plugins.base_plugin import BasePlugin

class MiPlugin(BasePlugin):
    name = "mi_plugin"
    description = "Descripción de mi plugin"
    
    async def process(self, message: str, context: dict) -> str:
        # Lógica del plugin
        return "Respuesta procesada"
```

## Pruebas
```bash
# Ejecutar pruebas unitarias
pytest tests/core/

# Ejecutar pruebas con cobertura
pytest --cov=meribot.core tests/core/
```

## Dependencias
- LangChain
- ChromaDB
- Pydantic
- Redis (para caché distribuida)
