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

## 🔹 Capa de Lógica de la Aplicación (Contenedor)
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

 
## 🔄 Flujo General
============================================================
1. Usuario → Widget → Servidor Web
2. Servidor Web → FastAPI → LangChain
3. LangChain → ChromaDB → Recupera información
4. LangChain → Respuesta → FastAPI → Widget → Usuario
5. Scraper Host → Extrae datos → Embeddings → ChromaDB
6. meri-cli → Administración - Administra scraping y base vectorial

## ✅ Recomendaciones
============================================================
- Utiliza GitHub Copilot para acelerar el desarrollo de cada módulo.
- Documenta cada componente en su propio README.
- Implementa pruebas unitarias (FastAPI, scraper, etc)
- Monorepo con submódulos: `meribot.api`, `meribot.crawler`, etc.
- Usa Docker Compose para orquestar los servicios.
