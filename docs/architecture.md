# 📘 Arquitectura del Proyecto MeriBot
Este documento describe cómo construir Meribot, chatbot conversacional modular utilizando GitHub Copilot, basado en una arquitectura empresarial distribuida en capas. Cada componente puede desarrollarse como microservicio o módulo independiente.

## 🧠 Capas Principales
============================================================
MeriBot se compone de varias capas modulares que pueden desarrollarse como microservicios:

1. **Interfaz de Usuario**: Widget JS embebido en la intranet.
2. **Servidor Web**: Sirve la página y comunica con FastAPI.
3. **Lógica de Aplicación**: FastAPI + LangChain.
4. **Recopilación de Datos**: Scraper con cron job.
5. **Almacenamiento**: ChromaDB para embeddings.
6. **Administración**: CLI para scraping y gestión de vectores.

## 📌 Resumen de la arquitectura (basado en el RFP)
============================================================

 - El widget web (HTML/JS) se integra en el portal anfitrión y se comunica por HTTP con FastAPI.
 - El servidor FastAPI expone una API REST y conecta con LangChain.
 - El scraper extrae info de la intranet (automatizado por cron).
 - Los datos extraidos van a una base de datos vectorial ChromaDB
 - La BBDD vectorial ChromaDB deberia funcionar inicialmente local (dev)
 - Todo el acceso es indirecto: el usuario nunca toca datos o modelos directamente.
 - Seguridad y simplicidad: sin cambios en el portal anfitrión, sin exponer lógica interna, sin acceso en tiempo real a sistemas fuente

 ## 🔹 Capa de Interacción del Usuario
============================================================
Usuario (PC)
 └── Navegador Web
      └── Widget Meri-bot (JS embebido)
           └── Comunicación vía HTTP/REST con Servidor Web

- El widget se desarrolla en JavaScript y se embebe en la web descargada 'Cloud & Custom Applications.html'
- Se comunica con el backend vía peticiones HTTP (POST/GET).
- Requiere una interfaz amigable para capturar y mostrar respuestas.

## 🔹 Capa de Servidor Web CCA (Intranet)
============================================================
Servidor Web CCA – Intranet C&CA
 └── (DEV) Sirve la Página Web descargada: 'Cloud & Custom Applications.html'
     (PROD) Sirve la Página Web Intranet: https://cca.capgemini.com/web/home
      └── Embebe el chatbot Meri-bot

- Utiliza un simple python -m http.server (es suficiente para hacer pruebas locales).
- Asegura la integración con la red interna y autenticación corporativa.

## 🔹 Capa de Lógica de la Aplicación (FastAPI Core)
============================================================
```
meribot/core/
├── api/
│   ├── app.py                    # Aplicación FastAPI principal
│   └── endpoints/                # Endpoints organizados por módulos
├── chatengine.py                 # Motor de conversación principal
├── conversation/                 # Gestión de diálogos y contexto
├── llm/                         # Integración con modelos de lenguaje
└── templates/                   # Plantillas de respuesta
```

### 🔌 Endpoints de la API
- **POST** `/chatbot/query` - Procesa consultas del usuario
  - Recibe: `question`, `conversation_id` (opcional), `domains` (opcional)
  - Devuelve: `response`, `conversation_id`, `intent`, `confidence`, `citations`
- **GET** `/chatbot/health` - Verificación de estado del servicio
- **GET** `/chatbot/allowed_domains` - Lista de dominios permitidos para scraping
- **GET** `/` - Página principal del widget
- **GET** `/widget` - Interfaz del widget chatbot

### 🧠 Motor de Conversación (ChatEngine)
- **Procesamiento de Mensajes**: Análisis de intención y contexto
- **Gestión RAG**: Retrieval-Augmented Generation con ChromaDB
- **Integración LLM**: Conexión con modelos de OpenAI/Azure
- **Manejo de Contexto**: Persistencia de conversaciones
- **Validación**: Control de calidad de respuestas

### 🔧 Configuración y Middlewares
- **CORS**: Configurado para integración con intranets
- **Archivos Estáticos**: Servicio de CSS, JS e imágenes del widget
- **Gestión Errores**: Manejo robusto de excepciones
- **Logging**: Registro detallado para debugging y monitoreo

## 🔹 Capa de Recopilación de Datos
============================================================
Scraper Host
 |── Cron Job
 │    └── Ejecuta tareas periódicas
 └── WebScraper (Python CLI)
      └── Extrae datos de la intranet
      └── Genera embeddings
      └── Inserta en ChromaDB

- El scraper se ejecuta automáticamente o manualmente.
- Extrae políticas, documentación y procedimientos internos.
- Los datos se transforman en vectores para búsqueda semántica.

## 🔹 Capa de Almacenamiento de Datos
============================================================
Base de Datos Vectorial
 ├── ChromaDB
 │    └── Almacena embeddings
 │    └── Permite búsqueda semántica
 └── Accesible por LangChain vía retrievers

- ChromaDB se utilizan para almacenar vectores.
- Permiten búsquedas rápidas y relevantes desde LangChain.

## 🔹 Capa dAdministrativa
============================================================
Herramienta meri-cli (CLI)
 |── Gestión del Scraper Host
 │    └── Ejecutar scraping manual
 │    └── Ver logs / errores
 └── Gestión de la Base Vectorial
      └── Validar ingestas
      └── Limpiar vectores
      └── Ajustar índices
      └── Sincronizar datos

- meri-cli es una herramienta en Python para administración técnica.
- Permite control total sin afectar el flujo conversacional.

 
## 🔄 Flujo de Procesamiento de Consultas
============================================================

### 📱 Flujo Principal de Usuario
```
Usuario → Widget JavaScript → POST /chatbot/query → ChatEngine → Respuesta
```

1. **Usuario** escribe pregunta en el widget embebido
2. **Widget** envía petición HTTP POST a `/chatbot/query`
3. **FastAPI** recibe y valida la petición (`QueryRequest`)
4. **ChatEngine** procesa el mensaje:
   - Analiza la intención de la consulta
   - Busca información relevante en ChromaDB (RAG)
   - Genera respuesta usando LLM si es necesario
   - Aplica validaciones de calidad
5. **API** devuelve respuesta estructurada con metadatos
6. **Widget** muestra la respuesta al usuario

### 🕷️ Flujo de Recopilación de Datos
```
Scheduler → Crawler → Scraping → Procesamiento → ChromaDB
```

1. **Scheduler** ejecuta tareas de scraping programadas
2. **Crawler** extrae contenido de sitios web permitidos
3. **Procesamiento** limpia y estructura los datos
4. **Embeddings** genera vectores semánticos
5. **ChromaDB** almacena documentos y vectores para búsqueda

### ⚙️ Flujo de Administración
```
meri-cli → Comandos → Gestión Sistema → Logs/Reportes
```

1. **Administrador** ejecuta comandos CLI
2. **meri-cli** procesa comandos administrativos
3. **Sistema** ejecuta operaciones de mantenimiento
4. **Logs** registran actividades y resultados

## ✅ Recomendaciones
============================================================
- Utiliza GitHub Copilot para acelerar el desarrollo de cada módulo.
- Documenta cada componente en su propio README.
- Implementa pruebas unitarias (FastAPI, scraper, etc)
- Monorepo con submódulos: `meribot.api`, `meribot.crawler`, etc.
- Usa Docker Compose para orquestar los servicios.
