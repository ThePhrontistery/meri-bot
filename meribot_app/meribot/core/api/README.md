# Módulo de API

## Descripción
Este módulo implementa la capa de servicio web que expone los endpoints de la API REST para el chatbot MeriBot. Utiliza FastAPI para proporcionar una interfaz de alto rendimiento y fácil de usar.

**NOTA:** Este módulo ha sido movido dentro de `core/` para mejorar la cohesión arquitectónica, ya que los endpoints están íntimamente ligados al ChatEngine y otras funcionalidades del core.

## Características Principales
- Endpoint `/chatbot/query` para procesar consultas
- Integración con LangChain para el procesamiento de lenguaje natural
- Validación de datos con Pydantic
- Documentación automática con OpenAPI (disponible en `/docs` y `/redoc`)
- Manejo de errores centralizado
- Soporte para CORS

## Estructura del Módulo
```
core/api/
├── __init__.py
├── app.py              # Aplicación principal de FastAPI
└── endpoints/          # Definición de rutas adicionales (vacía por ahora)
```

## Uso

### Iniciar el servidor
```bash
uvicorn meribot.core.api.app:app --reload
```

### Realizar una consulta
```bash
curl -X POST "http://localhost:8000/chatbot/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "¿Cómo puedo solicitar vacaciones?"}'
```

## Variables de Entorno
- `API_PREFIX`: Prefijo para las rutas de la API (por defecto: "")
- `DEBUG`: Modo de depuración (por defecto: False)
- `CORS_ORIGINS`: Orígenes permitidos para CORS (separados por comas)

## Dependencias
- FastAPI
- Uvicorn
- Pydantic
- Python-multipart (para soporte de formularios)

## Documentación
- Documentación interactiva: http://localhost:8000/docs
- Documentación alternativa: http://localhost:8000/redoc