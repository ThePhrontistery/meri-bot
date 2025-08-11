README - Creación de Chatbot Empresarial con GitHub Copilot
Este documento describe cómo construir un chatbot modular utilizando GitHub Copilot, basado en una arquitectura empresarial distribuida en capas. Cada componente puede desarrollarse como microservicio o módulo independiente.

Resumen de la arquitectura (basado en el documento):
 - El scraper extrae info de la intranet (automatizado por cron).
 - Los datos van a una base vectorial ChromaDB
 - El BBDD vectorial ChromaDB deberia funcionar inicialmente local (dev)
 - El servidor FastAPI expone una API REST y conecta con LangChain.
 - El widget web (HTML/JS) se integra en el portal y se comunica por HTTP con FastAPI.
 - Todo el acceso es indirecto: el usuario nunca toca datos o modelos directamente.
 - Seguridad y simplicidad: sin cambios en el portal, sin exponer lógica interna, sin acceso en tiempo real a sistemas fuente

============================================================
🔹 Capa de Interacción del Usuario
============================================================
Usuario (PC)
 └── Navegador Web
      └── Widget Meri-bot (JS embebido)
           └── Comunicación vía HTTP/REST con Servidor Web

- El widget se desarrolla en JavaScript y se embebe en la intranet.
- Se comunica con el backend vía peticiones HTTP (POST/GET).
- Requiere una interfaz amigable para capturar y mostrar respuestas.

============================================================
🔹 Capa de Servidor Web CECA (Intranet)
============================================================
Servidor Web CECA – Intranet C&C&A
 └── Sirve la Página Web Intranet
      └── Embebe el chatbot Meri-bot

- Utiliza un simple python -m http.server (es suficiente para hacer pruebas locales).
- Asegura la integración con la red interna y autenticación corporativa.

============================================================
🔹 Capa de Lógica de la Aplicación (Contenedor)
============================================================
Contenedor Docker
 |── Servicio FastAPI
 │    └── Endpoint: /chatbot/query
 │    └── Recibe peticiones del Widget
 └── Lógica LangChain
      └── Procesa la consulta
      └── Accede a herramientas (retrieval, chains, agents)
      └── Consulta la base vectorial si es necesario

- FastAPI gestiona las peticiones y respuestas.
- LangChain permite el uso de LLMs y recuperación semántica.
- Docker facilita el despliegue y escalabilidad.

============================================================
🔹 Capa de Recopilación de Datos
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

============================================================
🔹 Capa de Almacenamiento de Datos
============================================================
Base de Datos Vectorial
 ├── ChromaDB
 │    └── Almacena embeddings
 │    └── Permite búsqueda semántica
 └── Accesible por LangChain vía retrievers

- ChromaDB se utilizan para almacenar vectores.
- Permiten búsquedas rápidas y relevantes desde LangChain.

============================================================
🔹 Capa Administrativa
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

============================================================
🔄 Flujo General
============================================================
1. Usuario → Widget → Servidor Web
2. Servidor Web → FastAPI → LangChain
3. LangChain → Base Vectorial → Recupera información
4. LangChain → Respuesta → FastAPI → Widget → Usuario
5. Scraper Host → Extrae datos → Embeddings → Base Vectorial
6. meri-cli → Administra scraping y base vectorial

============================================================
✅ Recomendaciones
============================================================
- Utiliza GitHub Copilot para acelerar el desarrollo de cada módulo.
- Documenta cada componente en su propio README.
- Usa Docker Compose para orquestar los servicios.
- Implementa pruebas unitarias para FastAPI y el scraper.
- La aplicación se desarrolla como monorepositorio
- La estructura basado en un unico module "meribot" ( - no es valido en nombres de Python)
- Tener submodules (por ejemplo, meribot.api, meribot.crawler, etc.) según cada capa definida más arriba
