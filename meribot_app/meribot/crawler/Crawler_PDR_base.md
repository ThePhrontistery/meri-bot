# Bloque Crawler para Meri-bot: Especificación Funcional y Técnica

### TL;DR

El Crawler de Meri-bot explora la intranet corporativa, extrae texto y metadatos de páginas HTML y documentos (Word, Excel, PDF), y actualiza la base de conocimiento en ChromaDB. Se ejecuta semanalmente y bajo demanda desde Meri-Cli, detecta cambios por fechas de versión y metadatos, y reporta errores con mensajes estándar. Incluye soporte multilenguaje para etiquetar y organizar el contenido.

---

## Goals

### Business Goals

### User Goals

* Disponer de un proceso de ingesta automático y confiable con monitoreo por CLI.

* Ejecutar crawls bajo demanda y verificar su estado en tiempo real.

* Recibir reportes claros de cambios: nuevos documentos, actualizados, no modificados y errores.

### Non-Goals

---

## User Stories

Personas: Administrador de Contenidos y Mantenimiento (Admin)

* US01 (Admin): Como Administrador, quiero configurar urls y rutas semilla, para limitar la información a extraer por el Crawler.

* US02 (Admin): Como Administrador, quiero programar una ejecución semanal, para mantener el conocimiento actualizado automáticamente.

* US03 (Admin): Como Administrador, quiero lanzar el Crawler bajo demanda, para forzar una actualización inmediata cuando se publiquen documentos críticos.

* US04 (Admin): Como Administrador, quiero ver un resumen de resultados (nuevos, actualizados, no cambiados, errores), para evaluar el éxito del proceso.

* US05 (Admin): Como Administrador, quiero revisar los errores con mensajes estándar, para diagnosticar y corregir problemas rápidamente.

* US06 (Admin): Como Administrador, quiero que se detecten cambios por fecha de modificación y hash de contenido, para evitar reindexar documentos idénticos.

* US07 (Admin): Como Administrador, quiero configurar dominios y metadata almacenado (ej: url original de documento, dominio, fecha, autor, tipo de documento), para definir el modelo de la base de datos.

---

## Functional Requirements

Mapa de funcionalidades por prioridad (P0 = MVP, P1 = Próxima fase)

* Descubrimiento y Alcance (Priority: P0) -- Semillas y límites: Configurar URLs semilla, dominios permitidos, profundidad máxima. -- Politeness: Rate limiting, user agent configurable, control de concurrencia. -- Descubrimiento de documentos: Detección y descarga de HTML, .docx, .xlsx, .pdf.

* Extracción y Normalización (Priority: P0) -- Parser HTML: Limpieza, extracción de texto, títulos, encabezados, enlaces, metadatos. -- Parser de documentos: Extracción de texto y metadatos de Word, Excel y PDF.

* Detección de Cambios (Priority: P0) -- Comparación por metadatos (Last-Modified, ETag) y hash de contenido. -- Clasificación: nuevo, actualizado, sin cambios, inaccesible/corrupto.

* Estructuración y Almacenamiento (Priority: P0) -- Chunking: Segmentación del contenido en fragmentos coherentes con tamaño configurable. -- Enriquecimiento: Inclusión de metadatos (fuente, tipo, idioma, fechas). -- Persistencia: Upsert en ChromaDB con claves determinísticas.

* Orquestación y Programación (Priority: P0) -- Ejecución semanal automática. -- Ejecución manual desde Meri-Cli. -- Reintentos con backoff exponencial para fallos temporales.

* Observabilidad y Administración (Priority: P0) -- Logging estructurado y niveles (INFO/WARN/ERROR). -- Mensajes estándar de error y códigos de salida.


---

## User Experience

Aunque es un componente backend, la interacción principal es por Meri-Cli.

Entry Point & First-Time User Experience

* Instalación y setup:

  * Definir archivos de configuración (semillas, dominios permitidos, profundidad, límites).
  
  * Definir categorias de metadatos.

  * Probar con un comando de dry-run para validar alcance.

* Guía de uso:

  * Meri-Cli ofrece ayuda contextual (meri crawler --help) y ejemplos de comandos.

Core Experience

* Step 1: Configurar el Crawler

  * Establecer seeds, allowed_domains, max_depth, file_types.

  * Validaciones: URLs válidas, dominios no vacíos, tipos soportados.

  * Resultado: Configuración persistida y verificada.

* Step 2: Programar ejecución semanal

  * Comando para registrar el cron/scheduler interno.

  * Validaciones: expresión cron válida; confirmación de próxima ejecución.

* Step 3: Ejecutar bajo demanda

  * Comando run con opciones (—full, —since, —url, —dry-run).

  * Validaciones: parámetros compatibles; cancelar si ya hay job en curso (o encolar).

* Step 4: Reporte y resultados

  * Comando report muestra resumen por estado: nuevos, actualizados, sin cambios, errores.

  * Opciones de formato: tabla y JSON para consumo por otras herramientas.

Advanced Features & Edge Cases

* Páginas inaccesibles, timeouts y redirecciones circulares: registrar ERROR y continuar.

* Documentos corruptos o con formato no soportado: registrar WARN/ERROR con mensaje estándar.

* Ciclos de enlaces y contenido duplicado: detección por historial y hash; evitar recrawl infinito.

* Archivos muy grandes: abortar por límite configurado y registrar causa.

UI/UX Highlights

* Formatos consistentes de timestamps (ISO 8601) y duraciones.

* Tablas legibles con totales y subtotales por tipo de documento.

---

## Narrative

Meri-bot se apoya en información corporativa que cambia con frecuencia: nuevas políticas, procedimientos actualizados y documentos que se publican sin un aviso centralizado. El equipo administrador necesitaba una forma confiable de mantener el conocimiento al día sin invertir horas en tareas manuales de copia y pega. Ahí entra el Crawler.

Una vez configurado con las páginas semilla y dominios permitidos, el Crawler recorre la intranet, detecta y extrae texto y metadatos de páginas HTML y documentos Word, Excel y PDF. Fragmenta el texto en partes manejables y actualiza ChromaDB con una estructura consistente. Cada semana se ejecuta automáticamente y, cuando hay urgencia, el equipo lo dispara desde Meri-Cli. Los reportes muestran qué cambió y dónde hubo problemas, con mensajes claros que facilitan la corrección rápida.

El resultado es un Meri-bot que responde con información más fresca y relevante, mientras el equipo reduce drásticamente el esfuerzo operativo. La empresa gana precisión y velocidad en la difusión del conocimiento, y los usuarios confían más en las respuestas del bot.

---

## Success Metrics

### User-Centric Metrics

### Business Metrics

### Technical Metrics

### Tracking Plan

* Eventos: CRAWL_STARTED, CRAWL_COMPLETED, CRAWL_FAILED.

* Ítems: PAGE_FETCHED, DOC_DOWNLOADED, ITEM_NEW, ITEM_UPDATED, ITEM_UNCHANGED, ITEM_FAILED.

* Métricas por corrida: duration_sec, pages_crawled, docs_processed, new_count, updated_count, unchanged_count, error_count, warnings_count, throughput.

* Auditoría: config_version utilizada, usuario/servicio que lanzó el job, timestamp ISO 8601.

---

## Propósito y Alcance

El Crawler de Meri-bot es el componente responsable de descubrir, extraer y estructurar información desde la intranet corporativa, abarcando páginas HTML y documentos (Word, Excel, PDF). Su rol es mantener actualizada la base de conocimiento que alimenta las respuestas de Meri-bot, minimizando intervención manual. Es necesario porque centraliza y automatiza la ingesta de contenido, garantiza la frescura del índice y estandariza los metadatos y etiquetas, contribuyendo a respuestas más precisas y confiables.

---

## Fuentes de Información

* Tipos de fuentes:

  * Páginas HTML.

  * Documentos adjuntos: Word (.docx), Excel (.xlsx), PDF (.pdf).

* Alcance:

  * Debe extraer información de todo el contenido disponible dentro de los dominios permitidos.

* Acceso y autenticación:

  * MVP: acceso público a la intranet (sin credenciales).

---

## Frecuencia y Disparadores

* Ejecución automática: semanal, mediante programador interno o integración con el scheduler del entorno.

* Ejecución manual: disponible desde Meri-Cli (meri crawler run).

* Detección de cambios:

  * Por metadatos HTTP: Last-Modified, ETag.

  * Por metadatos de documentos: fecha de modificación, versión si existe.

  * Por hash de contenido (SHA-256) post-normalización para confirmar diferencias reales.

* Política de actualización: upsert solo cuando cambie contenido o metadatos relevantes.

---

## Procesamiento y Filtrado

* Extracción:

  * HTML: limpieza de boilerplate, obtención de texto visible, títulos, jerarquía de encabezados, enlaces salientes, metadatos (title, description, last-modified si disponible).

  * Documentos (adjuntos): lectura de Word, Excel y PDF; extracción de texto, tablas como texto etiquetado y metadatos (autor, fecha, título si aplica).

* Definición de “adjunto”: cualquier archivo descargable de tipo .docx, .xlsx, .pdf enlazado desde las páginas o listado en directorios públicos.

* Metadatos mínimos por ítem: source_url, source_type (html, docx, xlsx, pdf), content_hash, content_length, last_modified, crawl_timestamp, language, title (si aplica), parent_url, version_hint (si aplica).

* Exclusiones:

  * No hay exclusiones por defecto; se debe permitir configurarlas por patrones (P1).

---

## Estructuración y Almacenamiento

* Base de datos vectorial: ChromaDB.

* Estructura de datos (JSON por fragmento/chunk):

  * id: identificador determinístico (hash de source_url + chunk_index).

  * source_url, parent_url, source_type.

  * title, language, version_hint.

  * text: contenido del fragmento.

  * chunk_index, chunk_total, chunk_strategy (por longitud/párrafo/sección).

  * content_hash, last_modified, crawl_timestamp.

  * tags: lista opcional (e.g., dominios, departamento, confidencialidad si aplica).

* Chunking:

  * Tamaño objetivo configurable (e.g., 500–1,000 tokens) con solapamiento ligero.

  * Preservar límites semánticos cuando sea posible (párrafos, secciones).

* Operación de upsert:

  * Si content_hash no cambió: marcar como unchanged (no reindexar).

  * Si cambió: actualizar registros asociados.

* Embeddings:

  * Generación e inserción puede realizarla este bloque o un servicio de indexado separado.

  * MVP: al menos producir estructura lista para indexación en ChromaDB.

---

## Gestión de Errores y Edge Cases

* Logging y reporte:

  * Nivel INFO/WARN/ERROR con logs estructurados.

  * Reporte automático en Meri-Cli al finalizar la corrida y consultas intermedias vía status.

* Mensajes estándar:

  * No se pudo acceder al recurso .

  * Acceso restringido al recurso .

  * Documento corrupto o formato no soportado: <URL|archivo>.

  * Tiempo de espera excedido al obtener .

* Edge cases:

  * Páginas inaccesibles, 4xx/5xx: registrar y continuar.

  * Redirecciones infinitas/bucles: detectar por umbral y abortar la rama.

  * Archivos enormes: abortar por límite configurado y registrar.

  * Contenido duplicado: detectar por hash/URL canónica y omitir.

* Códigos de salida del job:

  * 0: éxito sin errores.

  * 1: éxito con advertencias/errores parciales.

  * 2: fallo crítico (job no completado).

---

## Interfaz de Administración

* Integración Meri-Cli (comandos sugeridos):

  * meri crawler config set|get|test

  * meri crawler run \[--full|--since=ISO8601|--url=|--dry-run\]

  * meri crawler schedule set|get|remove

  * meri crawler status

  * meri crawler report \[--format=table|json\]

  * meri crawler logs \[--level=info|warn|error\] \[--since=ISO8601\]

  * meri crawler retry-failures \[--window=24h\]

* Métricas básicas mostradas:

  * pages_crawled, docs_discovered, docs_processed, new_count, updated_count, unchanged_count, error_count, warnings_count, duration_sec, throughput_items_per_min, last_success_at, next_run_at.

* Salidas:

  * Tabla legible y opción JSON para integración con otras herramientas.

* Conexión:

  * Meri-Cli invoca al servicio Crawler vía API local o proceso hijo; códigos de salida y JSON estándar para interoperabilidad.

---

## Escalabilidad y Límites

* MVP:

  * Volumen objetivo: decenas de páginas y decenas de documentos por corrida.

---

## Requerimientos Técnicos Específicos

* Dependencias/librerías recomendadas:

  * HTTP y parsing HTML: requests (o equivalente), parser HTML robusto (BeautifulSoup/lxml).

  * Documentos: biblioteca para PDF (por ejemplo, PDFMiner o PyMuPDF), para Word (python-docx), para Excel (openpyxl). Alternativa unificadora: Apache Tika/textract/unstructured.

  * Hashing: SHA-256 estandarizado sobre texto normalizado.

  * ChromaDB: cliente oficial para upsert y consultas.

* Formatos de entrada/salida:

  * Entrada: lista de seeds, include/exclude patterns, límites operativos (JSON/YAML).

  * Salida: registros por chunk con estructura JSON descrita; reportes agregados en JSON.

* Integraciones:

  * Meri-Cli: interfaz de comandos, captura de códigos de salida y parseo de JSON.

  * ChromaDB: upsert de embeddings o payload para embedding posterior (según arquitectura).

  * Scheduler: cron del entorno o planificador interno.

* Configuración clave:

  * seeds: array de URLs.

  * allowed_domains: array de dominios / categorías.

  * max_depth, max_pages, max_runtime.

  * rate_limit_rps, concurrency.

  * file_types: \[html, docx, xlsx, pdf\].

  * auth: type, credentials_ref (opcional).

  * chunk_size, chunk_overlap.

---

## Technical Considerations

### Technical Needs

* Componentes:

  * Crawler Service: orquestación, fetch, descubrimiento, control de colas.

  * Parsers: HTML y documentos.

  * Normalizer: limpieza y chunking.

  * Change Detector: comparación de metadatos y hash.

  * Storage Adapter: integración con ChromaDB.

  * CLI Adapter: interfaz con Meri-Cli para comandos, estado y reportes.

* Modelos de datos:

  * Entidades: Page, Document, Chunk, CrawlRun, CrawlItemResult.

  * Estados: new, updated, unchanged, failed.

### Integration Points

* Meri-Cli para administración y monitoreo.

* ChromaDB para almacenamiento vectorial.

* Secret manager/variables de entorno para credenciales.

* Scheduler (cron/servicio del entorno).

### Data Storage & Privacy

* Flujo:

  * Fetch → Parse → Normalize/Chunk → Detect Changes → Upsert → Report.

* Estrategia:

  * Almacenar chunks con metadatos completos; no almacenar binarios salvo referencia (URL).

  * Logs con datos mínimos necesarios; evitar PII en mensajes.


### Potential Challenges

* Documentos mal formados.

* Estructuras de navegación con loops o páginas “infinitas”.

* Contenido dependiente de JavaScript (fuera de alcance en MVP).

* Diferencias sutiles en metadatos que no implican cambios reales (normalizar criterios).

---