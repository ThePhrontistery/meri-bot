# Resumen Técnico Detallado MeriBot

## Índice
- [arquitectura tecnica](#arquitectura-tecnica)
- [flujo tecnico](#flujo-tecnico)
  - [meri-cli scraper y carga de documentos](#meri-cli-scraper-y-carga-de-documentos)
  - [meribot motor conversacional y presentacion](#meribot-motor-conversacional-y-presentacion)

---

## arquitectura tecnica

- **Scraper (meri-cli):**
  - Desarrollado en Python.
  - Configuración y ejecución por línea de comandos.
  - Permite extracción automatizada y manual de documentos desde la intranet CCA.

- **Base vectorial:**
  - Utiliza ChromaDB (o Pinecone) para almacenamiento de vectores.
  - Los embeddings se enriquecen con metadatos: dominio, fecha, tipo y URL de documento.
  - Permite búsquedas semánticas rápidas y precisas.

- **Motor de consulta:**
  - Backend basado en FastAPI y LangChain.
  - Gestiona peticiones de usuario, recuperación semántica y generación de respuestas.

- **Interfaz web:**
  - HTML + JavaScript embebido en la intranet.
  - Panel flotante conversacional para interacción directa con el usuario.

---

## flujo tecnico

### meri-cli scraper y carga de documentos

- Herramienta CLI en Python que realiza scraping de la intranet CCA.
- Extrae documentos en formatos HTML, PDF, Word y Excel.
- Fragmenta semánticamente el contenido en "chunks" para mejorar la recuperación.
- Genera embeddings de cada fragmento, almacenando metadatos relevantes (dominio, fecha, tipo, URL).
- Carga los vectores en la base de datos vectorial (ChromaDB) para consultas semánticas posteriores.

### meribot motor conversacional y presentacion

- El usuario realiza una consulta a través del panel web embebido.
- Se aplica filtro por dominio e idioma según la consulta.
- FastAPI recibe la petición y consulta la base vectorial.
- LangChain procesa la consulta y genera una respuesta relevante.
- Meribot muestra la respuesta en el panel conversacional, incluyendo enlaces a los documentos fuente para trazabilidad.

---

**Este resumen técnico proporciona una visión clara y profesional de la arquitectura y el flujo de trabajo de MeriBot, facilitando la comprensión y el mantenimiento del sistema.**
