# 📋 Inventario de Endpoints - MeriBot API Refactorizada

## 🎯 Endpoints Principales del Chatbot

### 1. **POST /chatbot/query**
- **Función**: Endpoint principal para interacciones con el chatbot
- **Método**: POST
- **Payload**:
  ```json
  {
    "question": "string",
    "conversation_id": "string (opcional)",
    "domains": ["string"] (opcional)
  }
  ```
- **Respuesta**:
  ```json
  {
    "response": "string",
    "conversation_id": "string", 
    "intent": "string",
    "confidence": float,
    "citations": [],
    "source": "string",
    "suggested_questions": []
  }
  ```

### 2. **OPTIONS /chatbot/query**
- **Función**: Manejo de CORS preflight
- **Método**: OPTIONS
- **Respuesta**: Headers CORS + status ok

### 3. **GET /chatbot/health**
- **Función**: Health check del servicio
- **Método**: GET
- **Respuesta**:
  ```json
  {
    "status": "ok",
    "service": "meribot-api"
  }
  ```

### 4. **GET /chatbot/allowed_domains**
- **Función**: Obtener dominios permitidos para filtrado
- **Método**: GET
- **Respuesta**:
  ```json
  {
    "allowed_domains": ["domain1", "domain2", ...]
  }
  ```

## 🕷️ Endpoints del Crawler

### 5. **POST /scrape**
- **Función**: Scraping básico de documentos
- **Método**: POST
- **Payload**:
  ```json
  {
    "url": "string",
    "domain": "string"
  }
  ```

### 6. **POST /crawl-and-process**
- **Función**: Proceso completo de crawling + procesamiento + ingesta
- **Método**: POST
- **Payload**:
  ```json
  {
    "url": "string", 
    "domain": "string"
  }
  ```

### 7. **POST /process-docs**
- **Función**: Procesamiento de documentos ya descargados
- **Método**: POST
- **Payload**:
  ```json
  {
    "url": "string",
    "domain": "string"
  }
  ```

## 📊 Endpoints Adicionales (del Router process_docs)
- **GET /list-documents**: Listar documentos en ChromaDB
- **DELETE /delete-document**: Eliminar documento específico

## 🔧 Configuración de la API
- **Título**: "MeriBot API"
- **Versión**: "0.1.0"
- **Descripción**: "API para el servicio de chatbot de C&CA"
- **CORS**: Habilitado para todos los orígenes (desarrollo)
- **Documentación**: Disponible en `/docs` y `/redoc`

## 🎯 Plan de Testing
1. **Chatbot Core**: /chatbot/* endpoints
2. **Crawler Services**: /scrape, /crawl-and-process, /process-docs
3. **Administrative**: /list-documents, /delete-document
4. **Edge Cases**: Validaciones, errores, CORS