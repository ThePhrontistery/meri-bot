# Resumen Técnico Detallado MeriBot

## Índice
- [Arquitectura tecnica](#arquitectura-tecnica)
- [Flujo tecnico](#flujo-tecnico)
  - [Meri-cli scraper y carga de documentos](#meri-cli-scraper-y-carga-de-documentos)
  - [Meribot motor conversacional y presentacion](#meribot-motor-conversacional-y-presentacion)
    - [Detalles sobre la consulta y generación de respuestas](#detalles-sobre-la-consulta-y-generación-de-respuestas)
    - [Comportamiento observado en la búsqueda semántica y generación de citas](#comportamiento-observado-en-la-búsqueda-semántica-y-generación-de-citas)
    - [Mejoras-recomendación](#mejoras-recomendación)

---

## Arquitectura tecnica

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

## Flujo tecnico

### Meri-cli scraper y carga de documentos

- Herramienta CLI en Python que realiza scraping de la intranet CCA.
- Extrae documentos en formatos HTML, PDF, Word y Excel.
- Fragmenta semánticamente el contenido en "chunks" para mejorar la recuperación.
- Genera embeddings de cada fragmento, almacenando metadatos relevantes (dominio, fecha, tipo, URL).
- Carga los vectores en la base de datos vectorial (ChromaDB) para consultas semánticas posteriores.

### Meribot motor conversacional y presentacion

- El usuario realiza una consulta a través del panel web embebido.
- Se aplica filtro por dominio e idioma según la consulta.
- FastAPI recibe la petición y consulta la base vectorial.
- LangChain procesa la consulta y genera una respuesta relevante.

#### Detalles sobre la consulta y generación de respuestas

Cuando el usuario envía una consulta desde el panel web, FastAPI actúa como intermediario, recibiendo la petición y gestionando la comunicación con la base vectorial (ChromaDB). Utiliza LangChain para realizar una búsqueda semántica de los fragmentos más relevantes y generar la respuesta final.

#### Comportamiento observado en la búsqueda semántica y generación de citas

- El método `similarity_search` de LangChain sobre ChromaDB devuelve los documentos más similares según el embedding, pero no filtra por un umbral de similitud (score). Por defecto, se devuelven los `top_k` resultados, aunque algunos puedan ser poco relevantes para la consulta.
- Esto puede provocar que en la respuesta se incluyan más citas de las necesarias, o que aparezcan documentos que no contienen literalmente el término buscado, sino que son "similares" semánticamente. Este es un comportamiento típico de los modelos de embeddings: la similitud no garantiza coincidencia exacta, sino proximidad conceptual.
- Para mejorar la precisión y relevancia de las citas mostradas al usuario, es recomendable aplicar un filtrado adicional tras la búsqueda, descartando aquellos fragmentos cuyo score de similitud esté por debajo de un umbral definido. Así se evita mostrar referencias poco útiles o irrelevantes.
- Además, se pueden implementar tratamientos post-búsqueda, como la validación de la presencia literal de términos clave en los fragmentos recuperados, o el ajuste dinámico de `top_k` según la calidad de los resultados.

#### Mejoras-recomendación

- Revisar y ajustar los parámetros de la función de búsqueda (`top_k`, umbral de score) y aplicar filtros adicionales tras la consulta a la base vectorial para garantizar que las citas y documentos referenciados sean realmente relevantes para la pregunta del usuario.

---

**Este resumen técnico proporciona una visión clara y profesional de la arquitectura y el flujo de trabajo de MeriBot, facilitando la comprensión y el mantenimiento del sistema.**
