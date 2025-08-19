(WIP)
# Meri-bot: Aplicación Conversacional basada en IA sobre Intranet

# Introducción

## Resumen Ejecutivo

Meri-bot es un componente web conversacional basado en inteligencia artificial, diseñado para integrarse fácilmente en portales corporativos existentes. Permite a cualquier usuario realizar preguntas en lenguaje natural sobre la información interna de la empresa (intranet C&CA y Talent), obteniendo respuestas rápidas y comprensibles. El objetivo es ofrecer una experiencia similar a ChatGPT, pero centrada en la información de Capgemini, evitando la sensación de un “chatbot tradicional”.

## Objetivo General

Ofrecer una interfaz conversacional amigable para consultar información sobre las intranets internas de C&CA y Talent acelerando el acceso a políticas internas, documentación técnica, procedimientos y respuestas a dudas administrativas.

# Experiencia de Usuario en la Interfaz

## Ubicación y desarrollo del widget

El widget estará embebido en la página del portal (como bloque HTML/JavaScript).

No tenemos acceso al entorno real en agosto ni al entorno de desarrollo, así que hay que trabajar con un entorno simulado.

Lo más sencillo es crear una carpeta web en el proyecto, copiar la página del portal, e implementar el widget y el JS ahí.

### Sketchs propuestos por el cliente

A continuación se presentan los sketchs propuestos por el cliente, pero son una primera aprozimación. Son sketchs que podemos cambiar (además que a lo largo del documento el cliente ha eliminado iconos y funcionalidades que se presentan en dichos sketchs:

#### Widget meri-bot

Inclusión de widget en home page de web corporativa

- En `Cloud & Custom Applications.html`, el widget aparece justo encima del título principal de bienvenida.

- Permite mostrar cómo se integraría Meri-bot en una web real de la empresa.

- El widget mantiene su funcionalidad y diseño, pero embebido en el flujo visual de la página.

Elementos visuales del widget de entrada

- Mensaje de bienvenida sin nombre del usuario pues en MVP la página de C&CA que aloja el widget no tiene reconocimiento del usuario.

- Caja de texto con placeholder.

- Botón de envío con diseño corporativo.

No existe identificación de los usuarios

Debe haber un parametro que pase al widget el usuario autenticado para que ponga “Bienvenido, Iwan”? NO, no es necesario en MVP reconocer el usuario, con lo cual no se podrá identificar el nombre. Lo podemos dejar con “Bienvenido”.

Es decir, no existe gestión de usuarios para meri-bot. Es la página que la aloja la que debe realizar esta gestión. Por ahora la web de C&CA no dispone de gestión de usuarios. Por el hecho de entrar a C&CA desde un portátil de empresa, se puede entrar. Pero no reconoce ni guarda credenciales de usuarios

¿Se requiere integración con el sistema de usuarios corporativo (SSO)? NO en MVP

Ejemplo integración en web de C&CA:  cca.capgemini.com:

#### Panel de Conversación: Experiencia de Usuario en la Interfaz

Una vez que el usuario realiza la primera consulta en Meri-bot, la interacción con la IA durante esa sesión debe visualizarse en un panel que aparece por encima de la página del portal subyacente. Esto NO debe implementarse como un pop-up tradicional de JavaScript, sino como un <div> posicionado con atributos/properties CSS apropiado (z-index: 9999; position:fixed etc etc)

#### Flujo en Panel de conversación:

Al hacer clic en Botón de envío, se abre el panel de conversación. Al entrar en el panel se comienza una nueva conversación, y por lo tanto el historial de conversación estará vacío.

Parte de arriba: Una vez se haya iniciado una conversación y se tenga respuesta de la IA, se mostrarán todas las preguntas del usuario y las respuestas de Meri-bot como historial:

Se mostrará el icono que represente al usuario. Al lado se mostrará su pregunta/consulta

Debajo se mostrará un icono que represente a Meri-bot. Al lado se mostrará la respuesta de la IA

Debajo y a la derecha se mostrará un icono que tendrá el/los enlaces a las URL de los documentos que ha encontrado la IA y que ha usado para dar la respuesta

Parte intermedia: Se mostrará un mensaje visible "Meri-bot puede tener errores. Por favor chequee las respuestas y las fuentes"

Abajo:

Se mostrará el icono que represente al usuario.

Al lado se mostrará el Filtro selector de dominios. Se puede elegir uno, varios o ningún dominio. Esto permite limitar la búsqueda a ese ámbito. El usuario puede seleccionar uno o varios dominios. Puede no seleccionar ninguno, y entonces la búsqueda será en todos los dominios (lo mismo si selecciona todos)

Al lado se mostrará una Caja de texto donde el usuario podrá escribir su consulta o pregunta.

Botón de envío con diseño corporativo

Una vez se envíe la pregunta, se reflejará dicha pregunta en el historial

La respuesta de meri-bot deberá ser siempre de forma "streaming”.  Es decir, se deberá responder al usuario en el momento que estén disponibles los primeros caracteres, análogo al comportamiento estandar de los LLM' s como Office365, ChatGPT etc

No existe un máximo de preguntas/respuestas en una conversación en el panel de conversación

- Botón de cierre (X) en la esquina superior derecha del panel. El panel se cerrará y volverá al estado inicial del widget.

El usuario debe poder cerrar el panel fácilmente (por ejemplo, mediante un botón de cierre visible en la esquina superior derecha). Al cerrarse el panel, el usuario regresa a la página original del portal, y la conversación previa se pierde (en MVP no se requiere, de momento, guardar el historial de chats).

Este enfoque garantiza una experiencia no intrusiva y coherente con los portales modernos, facilitando el uso de Meri-bot sin desorientar al usuario ni interferir con la navegación habitual.

**Aclaración de Iwan del día 31 julio:

es decir: hay "cajita chat". en el portal; En el  momento que el usuario ha escrito un prompt/pregunta y ha clicado en el botón de envío, entonces se abre al " floating panel" con toda la interacción con la IA y todas las siguientes interacciones ocurren también en este panel mientras está abierto. Cuando de cierra el panel, se pierde todo el contenido y el usuario volverá a la página original

#### Filtros en el prompt con la IA (dominios)

La imagen muestra una funcionalidad de filtro desplegable integrada en la interfaz de Meri-bot. A la izquierda de la caja de texto principal hay un botón con icono de filtro.

Al hacer clic en este selector, aparece un menú desplegable con varias opciones de dominio o categoría:

Talent

Onboarding

Formación

Pero en la aplicación este debería depender en la ingestión de documentos de cierto dominio o categoría .

(PREGUNTA: donde se guarda esté lista. Se obtiene desde la BBDD Vectorial? RESPUESTA: Desde un fichero de configuración etc.)

El fichero de configuración : contendría la lista de los valores de los dominios,

Se gestiona desde meri-cli, la app de administrador

(MVP) Generar un fichero de configuración con 3 o 5 valores.

Pero hay que ver las consecuencias de que existan documentos con dominios que ya no existen (Spike)

Descripción funcional:

El usuario puede seleccionar el dominio o la categoría sobre la cual quiere realizar la consulta, antes de enviar su pregunta.

El filtro es visualmente claro, sencillo y contextual al cuadro de entrada.

La opción elegida aparece resaltada en una “píldora” junto al icono de filtro.

Al cambiar de filtro, la consulta que realice el usuario se limitará a la información correspondiente a la categoría seleccionada, facilitando respuestas más relevantes y precisas.

Esta funcionalidad permite personalizar y acotar las búsquedas, mejorando la precisión de las respuestas y evitando resultados irrelevantes al usuario. Es especialmente útil en sistemas con grandes volúmenes de información categorizada, como una intranet corporativa.

## Panel de Administración (NO SE REQUIERE)

No existe panel de administración online, visual. Solo se implementará meri-cli por línea de comandos.

# Descripción funcional

## Valor y Escenarios de Uso

Consultar políticas internas actualizadas.

Acceso ágil a documentación técnica y procedimientos.

Resolución rápida de dudas administrativas comunes.

## ¿Cómo funciona Meri-bot? (Explicación Conceptual)

Imagina que toda la documentación de la intranet se convierte en una gran biblioteca. Pero, en lugar de buscar manualmente, haces una pregunta y una IA te busca y resume el mejor fragmento, aunque uses palabras diferentes a las del documento.

### Flujo de trabajo ilustrado:

Analogía:

Embedding = traducir tu pregunta a un “código digital” que la IA puede comparar con “códigos digitales” de todos los documentos.

Vector store = un archivo donde cada fragmento de texto tiene su “código digital”.

RAG (Retrieval Augmented Generation) = la IA primero busca, luego responde usando lo encontrado, no inventando.

## Ejemplo de Uso Paso a Paso

Escenario: Marta quiere saber cómo solicitar teletrabajo.

1. Escribe: “¿Cómo pido trabajar en remoto?”

2. Meri-bot convierte la pregunta en un “código digital” y busca los documentos más parecidos.

3. Selecciona el fragmento relevante (“Procedimiento para solicitar teletrabajo”).

4. Redacta una respuesta clara y directa para Marta, basada en ese fragmento.

5. Marta recibe la respuesta y puede seguir preguntando o pedir más detalles.

## Historias de usuario

Como administrador, quiero poder configurar las fuentes de scraping desde un fichero o interfaz para mantener el sistema actualizado sin tocar el código. Sí en MVP. Las fuentes de scrapting estarán en un fichero de configuración.

Como desarrollador, quiero definir reglas de recursividad para el scraper para evitar que acceda a enlaces irrelevantes o externos.

Como usuario, quiero ver un enlace a los/s documentos fuente de la información para poder verificarla o ampliar el contenido. Sí en MVP. Se mostrará un icono que al pinchar en el mostrará el/los enlaces (urls) a los documentos origen.

Como responsable de RRHH, quiero que ciertos documentos críticos se actualicen inmediatamente para asegurar que la información esté disponible en tiempo real.

Como administrador, quiero registrar todas las preguntas y respuestas para poder auditar el uso del sistema y detectar mejoras. No en MVP. Lo que se requiere es poder tener log con todos los procesos que se van ejecutando, con la finalidad de debug y de detectar bugs (dónde hay un error, qué proceso lo origina, y qué tipo de error es)

Preguntas:

¿Desea que el chatbot registre y audite todas las interacciones (preguntas y respuestas) en logs para análisis posterior? Sí, almacenamiento en log

Paco: Las auditorias sobre consultas no pueden incluir datos personales, pero no es un problema porque no disponemos de identificación de usuarios

Como usuario, quiero poder enviar feedback sobre las respuestas para ayudar a mejorar la calidad del sistema. Eliminado de MVP

Vemos en el sketch que en el panel de conversación hay una mano hacia arriba y otra hacia abajo que se refiere al Feedback.

qué feedback quieres en el widget. Se guarda como feedback ligado a conversacion y se guarda con la conversacion, sobre el dominio, ambos? NO en MVP. No se va a implementar el feedback en MVP.

No hay botones de feedback (👍 / 👎). (En MVP)

Qué significa el botón de Retry en el sketch del panel de conversación? Nada, Eliminado del MVP

el sketch tiene simbolo + de subir documentos. Se pueden subir documentos? NO, no se debe mostrar el botón +. El usuario no debe poder subir documentos

Como usuario internacional, quiero poder hacer preguntas en inglés y recibir respuestas, aunque los documentos estén en español. Esto se refiere a que si la consulta se formula en un idioma, la IA debe responder en ese idioma (aunque los documentos extraídos estarán todos en español)

Como administrador, quiero controlar qué usuarios pueden acceder a qué dominios de información para proteger contenidos sensibles. Por ahora no en MVP. por ahora no tenemos impedimentos

## Expectativas Claras: Lo que puede y NO puede hacer Meri-bot

### Lo que sí:

Responde preguntas usando información de la intranet extraída regularmente.

Puede explicar políticas, procedimientos, o pasos prácticos.

Permite conversaciones contextuales (seguir preguntando sobre lo mismo).

### Lo que no:

No responde sobre información que aún no ha sido extraída (“puede tardar hasta una semana en aparecer”).

No inventa información, pero puede resumir.

No se conecta en tiempo real a sistemas internos: las respuestas pueden no reflejar cambios de última hora.

Si la pregunta es demasiado general o fuera de contexto, puede pedir que la reformules.

## Integración y Naturaleza como Componente Web

Se integra mediante HTML embebido (copiar y pegar).

No requiere cambios en el portal anfitrión ni en autenticación.

Ligero y seguro: nunca expone sistemas internos.

# Sincronización y Actualización de Datos (scraper)

El sistema trabaja solo con copias locales de la información obtenida por scraping automático (ej. semanal).

Nunca accede a los sistemas fuente en tiempo real, garantizando separación y seguridad.

Scraper: Proceso que visita la intranet, descarga documentos y páginas, y extrae el texto relevante.

# Fuentes de Información

Las fuentes de datos son las webs internas o Sharepoints/Teams internos de donde tenemos que obtener los documentos con la información.

El administrador configurará las fuentes de datos en fichero de configuración “Fuentes de Información” desde meri-cli

MVP:  Las fuentes de datos serán la web de C&CA y algunos documentos de RRHH que se están construyendo en este momento y que se alojarán en un Teams  o sharepoint interno de donde salen documentos relevantes de RRHH/Talent (todavía no está)

La web C&CA  es cca.capgemini.com/web/home (Cloud & Custom Applications)

(No MVP) En futuros evolutivos se incorporará la web de RRHH (Talent)

La web de RRHH es talent.capgemini.com/es  (Spain Intranet Homepage | Talent Capgemini)

# Dominios

Dominios (Talent, Onboarding, Formación)

- ¿en el scraper, los dominios son preconfigurables? Los dominios estarán en un fichero de configuración, este fichero de configuración lo gestionará el Administrador desde meri-cli. Los dominios se asociarán al Metadata. Los dominios sirven para el filtro.

# Formatos de documentos

¿Qué tipos de archivos/documentos deben ser soportados?

Meri-Cli debe tener fichero de configuración con estas fuentes.

(MVP) : Html, pdf, Word. Por ahora no imágenes.

# Extracción de documentos

¿Existen áreas o secciones específicas dentro de las webs que deban ser excluidas del scraping?

Los documentos se tratan con langchain

# Planificación del scraper

¿Con qué frecuencia debe actualizarse la base de datos de documentos? (En tiempo real, diario, semanal). En tiempo real para los documentos críticos/semanalmente para los demás

El Administrador puede programar el scraper de forma periódica desde un menú de configuración de Meri-bot? NO. Mediante meri-cli

El Administrador puede programar el scrapper en tiempo real desde un menú de configuración de Meri-bot? NO. Mediante meri-cli

(RFP) Existen documentos críticos donde algunos documentos deben actualizarse de inmediato (por ejemplo, cuando cambia una normativa urgente o hay una comunicación relevante para toda la organización). Por eso, el sistema debe permitir actualizar selectivamente ciertos documentos sin esperar al siguiente ciclo batch

Por línea de comandos, en meri-cli para el crawlling, para la gestión de bases de datos, etc. No se realiza online

(RFP) : Separación estricta: El scraper nunca expone sus credenciales o lógica al usuario final.

¿Hay alguna librería, framework o lenguaje de preferencia para el desarrollo del scraper?

Paco: Alguna librería python en concreto obligatoria? Phyton Script

# Especificación tecnológica

## Tipo de componente visual

Como Componente Web. Se integra mediante HTML embebido (copiar y pegar).

(RFP) Interfaz Web (HTML embebido)

¿Qué es? Un bloque HTML y JavaScript que se inserta en cualquier portal interno (como un “widget”).

Comunicación: Cuando el usuario hace una consulta, esta se envía vía HTTP al servicio FastAPI, que responde con el texto procesado.

Separación: No requiere que el portal anfitrión entienda nada de IA; No requiere cambios en el portal anfitrión ni en autenticación.

simplemente aloja el widget y muestra respuestas.

Ligero y seguro: nunca expone sistemas internos.

## Arquitectura Técnica (Simplificada y Visual)

## Arquitectura Técnica y Componentes — Detallado, Sin Jerga Inútil

### 1. Scraper de la Intranet (Python Script)

¿Qué es? Un programa Python (puede ser una simple aplicación de consola) que visita la intranet, descarga documentos y páginas, y extrae el texto relevante.

Automatización: Este script se puede programar con un cron job (Linux/Mac) o una tarea programada (Task Scheduler, Windows) para ejecutarse automáticamente, por ejemplo, cada semana.

Almacenamiento: Los textos extraídos se convierten en “embeddings” (vectores) y se guardan en una base de datos especializada (ChromaDB, Pinecone).

Función crítica: Separa el proceso de recopilación (scraping) del acceso en tiempo real, aumentando seguridad y rendimiento.

Debería tener distintas posibles fuentes: páginas de Talent, Sharepoint, Teams etc.

Hay diferencia entre la frecuencia de ingestión entre los fuentes

### 2. Base de Datos Vectorial (Vector Store: ChromaDB/Pinecone)

¿Qué es? Un sistema de almacenamiento que no guarda solo el texto, sino su representación matemática (“embedding vector”).

Para qué sirve: Permite búsquedas semánticas rápidas (“dame los fragmentos más parecidos a esta pregunta, aunque no sean iguales en palabras”).

Soporte de metadata: Cada fragmento almacenado puede tener metadatos (ej: url original de documento, dominio, fecha de creación, fecha de modificación, autor, tipo de documento, tamaño del documento).

Ejemplo:

{

"texto": "Procedimiento para teletrabajo...",

"vector": [...],

"metadata": {

"dominio": "RRHH",

"fecha": "2024-07-01",

"fuente": "Manual Empleado"

}

}

Ventaja: Permite a futuro añadir filtros por dominio, fecha, etc., en la interfaz o en la consulta.

Preguntas:

¿Dónde se alojará el repositorio de documentos extraídos antes de su vectorización?

BBDD vectorial dónde la alojamos?

Todo en local.

Vamos a intentar contenedores (Pablo Jimenez).

En Corpus se hizo así, en local. Una persona hace documents sets que se comparte

No guardamos documentos enteros, solo trozos con el embeding.

No pensar solo en Dominios, sino en distintas urls base

Cada url base tiene un nombre por ej 3 urls importantes de RRHH.

El identificador no puede ser la url completa.

El documento no se guarda en binario. Se hace langchain y luego recuperamos.

Por ej. Tenemos doc de 10.000 pags, lo dividmos en trozos. Cortamos. Y entonces la respuesta saldrá con la primera parte del documento en 1ª instancia, y no la de los siguientes trozos. Pero no es problema para nosotros:

Vamos a empezar a trabajar con los documentos pequeños:

Tijera

Bloques de n caracteres (1000 caracteres, con solapamiento de 200? Sí). Nos puede ayudar Iwan, Carlos, Sange

¿Cómo se identificará unívocamente cada documento?

¿Qué metadatos son imprescindibles? (ej: url original de documento, dominio, fecha de creación, fecha de modificación, autor, tipo de documento, tamaño del documento).

### 3. Motor de Consulta Conversacional (FastAPI + LangChain)

¿Qué es? Un servicio web en Python usando FastAPI.

FastAPI expone un endpoint REST donde se reciben preguntas en lenguaje natural.

LangChain maneja el flujo: toma la pregunta, consulta la base de vectores, arma un “prompt” para el LLM, y devuelve la respuesta.

Desacoplamiento: El frontend web NO accede a los datos o LLM directamente. Siempre pasa por este servicio.

Ventaja: Seguridad, modularidad, facilidad de mantener y evolucionar la lógica sin “romper” la UI.

### 4. Interfaz Web (HTML embebido)

¿Qué es? Un bloque HTML y JavaScript que se inserta en cualquier portal interno (como un “widget”).

Comunicación: Cuando el usuario hace una consulta, esta se envía vía HTTP al servicio FastAPI, que responde con el texto procesado.

Separación: No requiere que el portal anfitrión entienda nada de IA; simplemente aloja el widget y muestra respuestas.

## Uso de Metadata en el Vector Store: Filtros y Dominios

¿Por qué usar metadata? Permite asignar a cada fragmento información sobre su dominio, origen, tipo, etc.

Ejemplo de uso:

El usuario podría elegir solo ver información de “RRHH” o “IT”.

Al preguntar, la consulta se puede limitar a fragmentos con ese dominio (filtro en la búsqueda).

¿Cómo se implementa?

Al cargar los documentos, el scraper añade campos de metadata.

La API de consulta puede recibir un filtro (ej.: domain="RRHH").

El vector store devuelve solo los fragmentos que cumplan el filtro.

Ventaja para el futuro: Permite construir una UI más avanzada con filtros, menús por dominio, búsqueda acotada por fechas, etc.

## Cómo se conecta todo (flujo técnico, práctico):

## Ejemplo de ejecución completa (con metadata):

1. Automatización: El script de scraping se ejecuta cada lunes a las 2:00am.

2. Scraping: Extrae políticas de RRHH, procedimientos IT, etc. Cada fragmento se almacena con metadata (dominio, fecha).

3. Usuario: Marta abre el portal, selecciona “RRHH” en el filtro y pregunta “¿Cómo solicito teletrabajo?”

4. WebUI: Envía la consulta y el filtro a la API FastAPI.

5. API: Busca solo en fragmentos de dominio “RRHH”, genera el prompt y consulta el LLM.

6. Respuesta: Devuelve a Marta la política actual de teletrabajo.

## ¿Qué hay que saber para ampliar o modificar el sistema?

El script de scraping puede ser adaptado para nuevas fuentes o formatos (PDF, Word, web).

El vector store se puede ampliar con nuevos metadatos.

La API FastAPI puede exponer nuevos endpoints para consultas filtradas.

La UI puede mostrar filtros, menús y búsquedas avanzadas a futuro.

## Seguridad y buenas prácticas

Separación estricta: El scraper nunca expone sus credenciales o lógica al usuario final.

Validación: El servicio FastAPI valida tanto las preguntas como los filtros.

Auditoría: Todo acceso y respuesta se puede registrar para trazabilidad.

## Roles del Prompt: System Prompt vs User Prompt

### ¿Qué es el system prompt?

El “system prompt” es un mensaje fijo que el sistema envía siempre que interactúa con el modelo.

Establece el rol, estilo y límites del comportamiento de la IA (tono, ámbitos permitidos, formatos, temas prohibidos).

Es más autoridad: no puede ser sobrescrito por el usuario ni por mensajes posteriores (nebuly.com, Reddit).

Ejemplo de system prompt básico:

“Eres Meri-bot, asistente interno de Capgemini España. Tus respuestas deben citar fuentes relevantes, evitar temas sensibles, y rechazar cualquier solicitud fuera del dominio de documentación interna.”

OJO: tenemos que implementar un buen System Prompt.

### ¿Qué es el user prompt?

El user prompt es lo que envía el usuario final: preguntas, comandos o solicitudes específicas.

Son dinámicos por conversación, reflejan intenciones concretas del usuario.

No pueden alterar las reglas establecidas por el system prompt (Reddit).

Ejemplo de user prompt:

“¿Cómo solicito teletrabajar en Madrid?”

## Guardrails: cómo definir y aplicar límites seguros

### Objetivo de los guardrails

Son controles de seguridad que aseguran que las interacciones con Meri-bot sean adecuadas, veraces, y alineadas con las políticas corporativas (nebuly.com, arXiv, Medium).

Los guardrails es un tema del system prompt que se tendrá que definir.

### Tipos de guardrails clave

#### 1. Input Guardrails (antes de la consulta al modelo):

Filtro de contenido tóxico o inadecuado.

Validación de contexto (ej. aceptar consultas solo dentro del dominio esperado).

Depuración de información sensible (PII) (Medium).

#### 2. Output Guardrails (tras la generación de respuesta):

Detección de contenido erróneo, tóxico o sesgado.

Verificación de coherencia con fuentes recuperadas (incluso reintentar la generación si falla) (Medium).

#### 3. Protección contra ataques adversariales y prompt injection:

Escaneo automático de los fragmentos recuperados para detectar instrucciones ocultas.

Rechazo de inputs sospechosos o documentos contaminados (Wikipedia).

#### 4. Privacidad y control de acceso:

No exponer contenidos sensibles o internos sin autorización.

Adaptar el nivel de acceso según perfil o contexto del usuario (nb-data.com, Medium).

### Ejemplo de integración de prompts y guardrails (Meri-bot)

1. Input Guardrail comprueba que la consulta es válida y segura.

2. Se realiza la recuperación semántica vía embeddings y vector database.

3. Se configura el prompt enviado al modelo:

message[0]: role = "system", content = reglas y estilo.

message[1]: role = "user", content = consulta del usuario.

4. (Opcional en esta versión: Output Guardrail revisa la respuesta generada.

Si pasa, se muestra al usuario.

Si falla (por toxicidad, invalidez, incoherencia), puede reintentar o responder con un mensaje genérico.

Nota: por limitar la complejidad de la aplicación en una primera versión MVP, las Output Guardrails NO tienen que implementarse.

## Gestión de Documentos y Actualización Selectiva en la Base Vectorial

Para que Meri-bot mantenga siempre la información más relevante y actualizada, es fundamental que los documentos originales sean perfectamente identificables en la base vectorial, incluso después de haber sido fragmentados en múltiples “chunks” o trozos. Cada documento, al ser ingerido, se divide en varios fragmentos semánticos, y todos los fragmentos de un mismo documento comparten un identificador de documento en sus metadatos. De esta manera, es posible filtrar, localizar y gestionar de forma conjunta todos los fragmentos que pertenecen a un mismo documento.

Esta arquitectura tiene varias ventajas clave:

Actualización integral de documentos: Cuando un documento es actualizado (por ejemplo, un procedimiento de RRHH, una política crítica o una ficha técnica), es imprescindible eliminar todos los fragmentos asociados a la versión anterior y reemplazarlos por los nuevos. Así se garantiza que nunca coexistan en el sistema fragmentos de distintas versiones de un mismo documento, evitando inconsistencias y duplicidades.

Filtrado y trazabilidad: Gracias al identificador de documento en los metadatos, es posible filtrar todos los fragmentos relacionados, tanto para auditoría como para mostrar la procedencia de cada respuesta, o para operaciones de mantenimiento.

Soporte tanto batch como actualizaciones selectivas: Aunque la actualización por lotes (batch) es el escenario habitual (por ejemplo, una sincronización nocturna de toda la documentación) existen casos críticos donde algunos documentos deben actualizarse de inmediato (por ejemplo, cuando cambia una normativa urgente o hay una comunicación relevante para toda la organización). Por eso, el sistema debe permitir actualizar selectivamente ciertos documentos sin esperar al siguiente ciclo batch.

Mecanismos de actualización bajo demanda: Un reto pendiente y crítico es habilitar flujos para que documentos urgentes puedan ser sustituidos rápidamente. Esto podría lograrse permitiendo que usuarios autorizados suban directamente un documento a través de la interfaz o, preferiblemente, mediante la monitorización de una carpeta o repositorio especial (por ejemplo, una biblioteca de SharePoint). Cuando se detecta un nuevo documento o una versión modificada en esa ubicación prioritaria, se dispara automáticamente el proceso de actualización en la base vectorial, reemplazando todos los fragmentos antiguos por los nuevos.

Gobernanza y seguridad: Es fundamental definir claramente quién puede solicitar o ejecutar una actualización inmediata, para evitar riesgos de manipulación o sustitución accidental de información crítica. Este aspecto requiere un diseño cuidadoso y políticas de control de acceso robustas.

En resumen, la identificación granular y la gestión centralizada de los fragmentos por documento son esenciales para mantener la coherencia, la trazabilidad y la agilidad de Meri-bot. La solución definitiva para las actualizaciones selectivas y la ingesta de documentos urgentes sigue abierta y debe ser una prioridad en la evolución de la arquitectura. (Hacer spike)

### Preguntas sobre Actualización y mantenimiento de documentos

El documento se convierte en fragmentos. No se guarda nunca el documento original pdf o Word. Solo la representación textual en varias partes (chunk que tienen antes o después algo para preview , se solapan). En el metadata tenemos que asociar ese crunck con el documento original. La app meri-cli de línea de comandos debería ser capaz de actualizar o eliminar.

Debería haber otro scraping para borrar o eliminar lo anterior. Quitar los embedings anteriores y hacer nuevos.

Preguntas:

¿Cómo se debe gestionar la actualización, modificación o eliminación de documentos en las fuentes originales?

¿Desea que se mantenga un histórico de versiones de los documentos? NO

Queremos algún mantenimiento de los identificadores de documentos? (Qué ocurre si un documento se cambia de directorio? qué ocurre si un documento desaparece de la página web? Usamos un directorio propio de documentos que cargamos antes de vectorizarlos (y entonces dónde alojamos este repositorio)? Cómo reconocemos que un documentos ha sido modificado o eliminado?)

Lo que debe desaparecer para la eliminación de documentos, realmente es borrar trocitos. Encontrar el documento de nuevo, y se sustituye o añaden trocitos.

Cómo detectamos que un documento ha cambiado? (fecha de modif, fecha de creación, tamaño), los podemos meter como Metadata

Para saber los borrados, cómo?

Con una lista de documentos y comparar? Proceso:

Alguien arranca proceso de ingesta

Saco la nueva lista de los documentos, a local, para ello puedo apuntar a una URL, es decir: los documentos que los contiene. Se puede lanzar un comando para ver la fecha de creación, de modificación, etc, y todavía no lo has descargado.

Comparo con la lista anterior que tengo en mi local

Comparo ambas listas

Lo que hay en lista anterior que no está en la última: Tengo que borrarlo de la BBDD vectorial

Reto/ Spike

### Preguntas sobre Documentos críticos

(RFP) Ciertos documentos críticos se deben actualizar inmediatamente para asegurar que la información esté disponible en tiempo real.

Cómo sabemos qué documentos son críticos para RRHH, es decir secciones concretas en la web de RRHH (Talent?) NO

El Administrador o Responsable de RRHH puede configurar los documentos que son críticos para RRHH? SÍ, desde Meri-cli en un fichero de configuracion

Tratar por URL, para que el web scraper procese todos los enlaces de esta web.

Definir nivel de iteración/algoritmo.

Formas:

recoger todos los enlaces, después procesar todos los enlaces de cada página (NO es la idea). Tenemos que definir el nivel de iteraciones

Mejor: fichero de configuración, con harcodeado, carpeta crítica en el sharepoint/Teams para el proyecto. Nos ayuda a definir por ejemplo “Onboarding” y otro “RRHH”. Recogemos los documentos de diferentes formatos

Si recogemos de Teams -> tenemos lista de documentos

Si recogemos de una web (C&CA o Talent) -> Tenemos lista de enlaces

## Buenas prácticas recomendadas

Mantén el system prompt breve pero específico, con instrucciones claras sobre tono, estilo, temas permitidos y prohibidos (Medium, arXiv, NVIDIA Docs, AWS Documentation, confident-ai.com).

Input guardrails rápidos y ligeros (check de categorías, patrones detectables) para evitar latencia. Sí en MVP

Output guardrails consistentes: idealmente >90 % de fiabilidad para evitar falsos positivos frecuentes (confident-ai.com).  NO en MVP

Logging y auditoría: registrar inputs rechazados, fallos o respuestas conflictivas.  Sí en MVP

Feedback humano para refinar reglas. No en MVP

Revisión periódica del system prompt y reglas: actualizar estilo, políticas o nuevas fuentes de documentos.

Posibilidad de reintentos: si la salida falla una validación, intentar generar nuevamente con el mismo prompt o uno editado.

# Apéndices

## Preguntas Frecuentes (FAQ) respondidas por el cliente

¿Qué pasa si pregunto algo que no está en los documentos? Meri-bot te avisará y pedirá que reformules o que amplíes tu pregunta. Sí en MVP

¿Por qué la respuesta a veces tarda en reflejar cambios? Las actualizaciones dependen del scraping (normalmente semanal).

¿Puedo sugerir mejoras o reportar errores? NO en MVP. A futuro el usuario podrá enviar feedback desde la interfaz para que el equipo mejore respuestas y añada nuevos documentos.

¿La IA puede inventar respuestas? No, solo responde con base en la información extraída. Puede resumir, pero no inventar datos. Sí en MVP

Guardarraíl en System Prompt:

¿Cómo reconocer que una pregunta no es relevante o no es adecuada? Respuesta: El system prompt, en la salida, en el texto generado se debe poner el guardrail con las respuestas irrelevantes, etc ("no tengo respuestas", "no hay información relevante", "la pregunta está fuera del ámbito", etc)

Si no encuentra nada relevante, o la información no existe, o no existe el documento -> Entonces debe dar respuesta de que no lo encuentra, pero No debe alucinar ni inventar nada.

¿Ponemos un máximo de preguntas/respuestas en una conversación en el panel de conversación? Respuesta: A nivel de servidor debería haber un máximo para todos los usuarios

Las respuestas del LLM pueden contener markdown, Hay que mostrar html renderizado en markdown, lo que se usa en angular es bastante listo, pero no soporta renderizar diagramas.

Que Agente de IA debemos usar? Alguna preferencia? GPT 4.1, Claude…?

GPT4.1 es más costoso que nano.

Empezamos en 4.1 y luego bajamos a nano, para bajar de capacidad.

Para desarrollar uso el más potente (4.1), pero va a entrar GPT 5.

En la app usaremos GPT es posible que usemos nano por ej para pruebas. O al final se usará nano que será más ligero, más barato.

En la app: Usar última versión, por ej chat GPT 5 pero la versión nano

### Equipos VIBE SQUAD y Modelo de trabajo

¿Cómo nos organizaremos? Cliente propone que haya 2 equipos les llamaraios: Meri-bot y Mari-bot. Es una referencia interna, una broma, relacionada con Meritxell.

#### Simulación de Proveedores de meri-bot

Se dispondrá de 2 equipos VIBE SQUAD de desarrollo vibe coding para Meri-bot (Trabajando como dos proveedores distintos). Ambos equipos implementarán dos aplicaciones conversacionales basadas en IA .

Cada equipo deberá crear su propio prototipo. Y generar la guía de estilos.

#### Pautas UX/UI- Prototipo

UX/UI a pensar. Filtros/dominios, etc

Pista: para no confundir al usuario empujando hacia abajo, para no romper la home:

Dejar entrar al usuario (saludo). Un dif capa por encima

Que pueda cerrar este dif flotando

Enlaces a cada documento, etc

Si vemos que lo que nos da tiene buena pinta lo dejamos (mejor probar y luego lo dejamos definido)

Meri-bot y mari-bot tendrán las mismas funcionalidades, misma arquitectura y stack tecnológico Con los mismos patrones de diseño, y misma guía de estilo básica heredada de la web que va a alojarla (guía de estilo de la web C&CA).

La diferencia entre meri-bot y mari-bot será visual

un equipo que implementará un widget integrado que llamará a un panel de conversación. Con su propio prototipo y guía de estilos

otro equipo que implementará un icono flotante de chatbot integrado con un texto de chat, que llamará a un panel de conversación. Con su propio prototipo y guía de estilos

#### Modelo de trabajo- Roles y Tareas por Rol

Ambos equipos VIBE SQUAD implementarán con vibe coding con el modelo definido (lo más aproximado)

#### Modelo VIBE SQUAD definido al que deben adaptarse los dos equipos

#### Modelo VIBE SQUAD adaptado a 2 equipos

1 Product Manager para ambos equipos VIBE SQUAD

Dado que no disponemos de equipo transversal de UX/UI. Cada equipo VIBE SQUAD deberá generar su propio prototipo

Es necesaria buena documentación previa antes de que los Vibe Builder empiecen a  “vibe codificar”

Ya sabemos que seremos más rápidos, pero el objetivo es comprobar que construimos con calidad

Priorizar: Calidad de código. No generar código spaguetti. Revisar/code review.

Por lo tanto, tenemos que generar la documentación pertinente en formato .md para pasarla como contexto en los prompts de vibe coding (Copilot_Instructions,md, README, guía de estilos, PRD, lista de tareas por funcionalidad o user story, etc:.

Cada equipo deberá generar la guía de diseño particular (que deberá estar alineada con la guía de diseño de la web de C&CA que alojará Meri-bot

(Product Navigator o Product Manager) A partir del RFP y del documento de requisitos agrupados extraerá las funcionalidades principales, se obtendrá el story map para cada user story, y se definirán cada usser story con sus criterios de aceptación

(Vibe developer) Definirá las buenas prácticas, los patrones y principios de diseño ( DDD, TDD, SOLID y DRY, etc.)

(Todos) Se elaborará una lista de tareas técnicas para cada user story a implementar.

### DevOps

¿Generamos un repo por cada funcionalidad principal o un solo repo con directorios separados?

Mono repo por cada equipo. No separar por funcionalidades

En GitHub tendremos un repositorio para cada equipo (repositorio meri-bot y otro repositorio mari-bot.

### Estructura de carpetas del Proyecto

Estructura de carpetas:

Basada en un unico module "meribot" (- no es valido en nombres de Pytjhon)

tener sub modules como

meribot.api

meribot.crawler

etc

### Comandos y herramientas a usar

Se debe utilizar

uv con pytproyect.toml (pip prohibido)

ruff. para formateo/verificacion de estilos

mypy para verificacion de tipos

pytest para tests

### Cómo probar

No es necesario Flask ni ningún framework. Con un simple python -m http.server es suficiente para hacer pruebas locales.

El widget luego se conectará al servidor FastAPI, que estará en el mismo equipo.

### Arquitectura y Despliegue

#### Despliegue

El cliente

Elegirá el mejor producto (meri-bot o bien mari-bot)

Decidirá si poner en producción el producto elegido. Es decir, decidirá si  se integrará a futuro en la la web C&CA: Cloud & Custom Applications, pues la web C&CA es propiedad del equipo SDO de C&CA)

En producción, habrá un solo contenedor con FastAPI.

En dev (en vuestra maquina) NO es necesario tener un contenedor inicialmente. Evita dependencias de WIndows (rutas, modules especifico). Seria algo para meter en el Copilot_instructions.txt

En producción el widget se alojará en el servidor web de C&CA.

El script Python (meri-cli) se ejecutará en consola o en la nube, según lo programe un cron job.

#### Arquitectura

Resumen de la arquitectura (basado en el documento):

- El scraper extrae información de la intranet C&CA(automatizado por cron).

- Los datos van a una base vectorial (ChromaDB o Pinecone). La bdd vectorial deberia funcionar inicialmente en local (dev). ChromaDb suponemos sería la mejor opción.

- El widget web (HTML/JS) se integra en el portal y se comunica por HTTP con FastAPI.

- El servidor FastAPI expone una API REST y conecta con LangChain.

- Todo el acceso es indirecto: el usuario nunca toca datos o modelos directamente.

- Seguridad y simplicidad: sin cambios en el portal, sin exponer lógica interna, sin acceso en tiempo real a sistemas fuente.

## Glosario Básico

#### Embedding:

Un método para transformar texto en un formato matemático que facilita comparar preguntas y documentos, incluso si usan palabras distintas.

#### Vector Store (base vectorial):

Un sistema de almacenamiento donde cada fragmento de texto tiene un “código digital” para búsquedas eficientes.

#### RAG (Retrieval Augmented Generation):

Técnica en la que la IA busca información relevante y la utiliza para construir respuestas precisas.

#### Prompt:

La pregunta o instrucción que el usuario da a la IA.

#### Guardrail:

Mecanismo de protección para evitar respuestas inadecuadas o peligrosas.

#### DDD

En programación, DDD, o Diseño Guiado por el Dominio, es una metodología centrada en el dominio del negocio, donde el objetivo principal es alinear el desarrollo del software con las necesidades y procesos específicos de la organización. DDD no es una metodología de desarrollo en sí misma, sino más bien un conjunto de principios y patrones que ayudan a modelar y construir software complejo reflejando el dominio del negocio.

Cuándo aplicar DDD?

Proyectos a Largo Plazo: Cuando se espera que el sistema evolucione y se mantenga durante un período prolongado. Colaboración entre Equipos: Cuando hay múltiples equipos trabajando en diferentes partes del sistema y se necesita una clara delimitación de responsabilidades

En resumen, DDD busca:

Comprender profundamente el dominio del negocio:

Esto implica entender las reglas, procesos y conceptos clave del negocio que el software debe manejar.

Modelar el software a partir del dominio:

El diseño del software se basa en el modelo del dominio, utilizando un lenguaje común entre desarrolladores y expertos del negocio.

Gestionar la complejidad:

DDD ayuda a dividir sistemas complejos en subdominios más manejables, facilitando el desarrollo y mantenimiento.

Mejorar la comunicación:

El lenguaje ubicuo, un lenguaje compartido entre el equipo de desarrollo y los expertos del negocio, ayuda a evitar malentendidos y a alinear los esfuerzos.

Conceptos clave en DDD:

Modelo de dominio:

Es la representación del dominio del negocio, incluyendo conceptos, reglas y relaciones.

Subdominios:

Divisiones del dominio en áreas más pequeñas y manejables, cada una con su propio modelo y reglas.

Contextos delimitados:

Un contexto delimitado es un espacio donde un modelo de dominio es válido y consistente.

Lenguaje ubicuo:

El lenguaje común utilizado por todos los miembros del equipo, incluyendo desarrolladores y expertos del negocio, para hablar sobre el dominio.

Entidades y objetos de valor:

Son los elementos básicos del modelo de dominio, las entidades con identidad y los objetos de valor sin identidad.

Repositorios:

Patrón para acceder y persistir los datos del dominio.

Beneficios de DDD:

Software más alineado con el negocio:

El software se adapta mejor a las necesidades del negocio y a los cambios que puedan surgir.

Mayor comprensión del dominio:

El equipo de desarrollo adquiere un conocimiento profundo del negocio, lo que se traduce en soluciones más precisas.

Reducción de la complejidad:

La división del sistema en subdominios facilita el desarrollo y mantenimiento.

Mejora de la comunicación:

El lenguaje ubicuo reduce los malentendidos y facilita la colaboración entre los equipos.

Mayor adaptabilidad:

El diseño modular permite realizar cambios y mejoras de forma más sencilla.

Desventajas de DDD:

Curva de aprendizaje:

Requiere un conocimiento profundo del dominio y de los conceptos de DDD, lo que puede llevar tiempo.

Complejidad inicial:

Puede ser más complejo de implementar al principio en comparación con otros enfoques.

En resumen, DDD es una herramienta poderosa para construir sistemas complejos, especialmente en proyectos donde el dominio del negocio es crítico y está sujeto a cambios frecuentes, según Databay Solutions y Itequia, donde el objetivo es lograr una solución que se ajuste a las necesidades del negocio..

#### TDD

En programación, TDD, o Desarrollo Guiado por Pruebas (Test-Driven Development), es una metodología donde se escriben pruebas automatizadas antes de escribir el código de producción. Se sigue un ciclo iterativo de tres pasos: rojo (red), verde (green), y refactorización (refactor). Primero, se crea una prueba que falla (rojo), luego se escribe el código mínimo para que la prueba pase (verde), y finalmente se refactoriza el código para mejorarlo sin cambiar su comportamiento.

Explicación detallada:

1. Desarrollo Dirigido por Pruebas:

TDD invierte el orden tradicional de desarrollo. En lugar de escribir código y luego probarlo, se escribe la prueba primero, lo que ayuda a definir claramente los requisitos y el comportamiento deseado del código.

2. Ciclo Rojo-Verde-Refactorización:

1. Red (Rojo):

Define un requerimiento específico o una historia de usuario.

Escribe una prueba unitaria que describa el comportamiento esperado del código que aún no existe.

La prueba debe fallar inicialmente porque el código correspondiente aún no ha sido implementado.

2. Green (Verde):

Escribe el código mínimo necesario para que la prueba pase.

El objetivo es hacer que la prueba pase con la solución más simple posible, sin preocuparse por la calidad o la limpieza del código en esta etapa.

3. Refactorización:

Revisa el código escrito para asegurarte de que sigue los principios de diseño y buenas prácticas.

Elimina duplicaciones, mejora la legibilidad, y optimiza el código sin cambiar su comportamiento.

Después de la refactorización, vuelve a ejecutar todas las pruebas para asegurar que todo sigue funcionando correctamente.

Recomendaciones:

Comienza con pruebas simples:

Practica el ciclo Red-Green-Refactor con funcionalidades pequeñas para familiarizarte con el proceso.

Utiliza herramientas de testing:

Aprende a usar herramientas como JUnit, PyTest o RSpec para automatizar tus pruebas.

Integra TDD con metodologías ágiles:

Combina TDD con prácticas como la integración continua para asegurar que las pruebas se ejecuten automáticamente con cada cambio.

Participa en la comunidad:

Comparte tus experiencias y aprende de otros desarrolladores que utilizan TDD.

Al seguir estos pasos y recomendaciones, podrás aplicar TDD en tus proyectos de desarrollo y aprovechar sus beneficios, como código más limpio, robusto y fácil de mantene

5. Beneficios:

Mejora la calidad del código: Al escribir pruebas primero, se fomenta un diseño más limpio y modular, lo que ayuda a crear código más robusto y fácil de mantener.

Reduce errores: Al detectar errores en una etapa temprana, se minimizan los problemas en etapas posteriores del desarrollo.

Diseño emergente: TDD ayuda a descubrir nuevos casos de prueba y requisitos a medida que se escribe el código, lo que puede llevar a un diseño más completo y adaptado a las necesidades.

Puede decirse que aplicar TDD se separa en dos fases bien diferenciadas. La primera de ellas es recopilar todas las funcionalidades que se espera del sistema de información en forma de varios (muchos) test unitarios. Mientras que la segunda, trata de implementar (programar) el cuerpo de la aplicación para que todos los test se ejecuten correctamente. Para llevar a cabo la segunda fase se deberán programar todos los elementos que finalmente compondrán la aplicación en sí misma.

Beneficios de usar TDD en un proyecto de software

La programación orientada a test cubre dos aspectos importantes en el desarrollo de software. Permite delimitar el alcance de un proyecto, ya que todos los requisitos de usuario deberían estar reflejados en casos de test. En muchas ocasiones, la enumeración de los test se considera parte del contrato que el proveedor de los servicios de programación deberá llevar a cabo. Y al mismo tiempo, será el justificante de entrega de un proyecto funcionando correctamente por parte del proveedor.

La ejecución correcta de los casos valida la implementación y por tanto el trabajo realizado, así como también ofrece garantías del correcto funcionamiento ante evoluciones y la subsanación de errores.

Cómo implementar la metodología Test Driven Development

Prácticamente todos los lenguajes de programación modernos, juntamente con los frameworks de programación que les acompañan proporcionan funcionalidades, ya sea nativamente o mediante librerías de terceros, para poder ejecutar test unitarios automáticamente durante la fase de construcción del programa. Si alguno de los test falla, el binario final no se construye, mostrando al usuario qué test no superaron la prueba, ya sea porque ocurrió un error o porque retornaron un resultado incorrecto.

Se debe tener presente que para aplicar TDD se requiere un estilo de programación muy concreto, en donde los programadores realicen unidades funcionales fáciles de invocar por parte de un test. Esto requiere que el programa tenga un buen diseño de componentes y haga una buena gestión de dependencias entre éstos. Ya que un test debe tener un acceso directo y simple a la invocación de una unidad funcional cualquiera, sin tener que instanciar cientos de componentes para poder consumir un método determinado. Así que es básico realizar una buena descomposición de componentes y separación de responsabilidades.

Sin embargo, los programadores juniors suelen carecer de la visión general y la experiencia necesaria para realizar un buen diseño de componentes que sean fáciles de instanciar y utilizar y que sólo respondan a una responsabilidad concreta y reutilizable. Es con el tiempo o con ayuda de otros programadores seniors, que alcanzarán la madurez necesaria para aplicar TDD correctamente. Aun así conviene introducir TDD en las fases iniciales de todo proyecto de software y guiarles en el proceso.

En el caso de realizar la aplicación con Java, los test se escriben como clases y métodos. La librería más habitual para ejecutar estas clases en forma de Test se denomina jUnit, y la herramienta de construcción Maven se encarga de lanzar a ejecución todas las clases marcadas como test vía jUnit de forma automática.

Los test se consideran código fuente del proyecto, y por tanto debe formar parte del código bajo el control de versiones. Así que, si los ficheros fuente Java están habitualmente en src/main/java, las clases de testing estarán en src/test/java.

Cómo se escribe un test en TDD

La respuesta dependerá del lenguaje de programación. Pero prácticamente todos ellos siguen un mismo patrón o pseudo código en donde hay unas fases bien diferenciadas por cada caso unitario. Su implementación puede variar en función del tipo de proyecto donde se intenta implantar TDD. En proyectos nuevos será mucho más sencillo de introducir, que en aquellos ya existentes y programados sin tener presente el TDD, por el hecho de que en proyectos nuevos suele ser más fácil realizar una buena separación de componentes. Aun así, cualquier test debe tener los siguientes pasos.

Fases de un test unitario:

Instanciación del componente. Los test están destinados a comprobar un caso sobre un componente. Conviene mantener a los test especializados en una determinada situación. Es un error escribir casos que prueben muchas funcionalidades. Así que en esta fase, el programador debe recuperar o crear sólo una instancia del componente o unidad funcional que quiere probar

Ejecución del componente. Dado el componente recuperado del paso anterior, lo siguiente es invocar la ejecución del mismo, ya sea una función o un método de una clase. Esta invocación se debe realizar con unos parámetros conocidos, de tal manera que se sepa de antemano cuál es el resultado que deberá ofrecer si el funcionamiento es correcto.

Comprobación del resultado. Al realizar la llamada de la unidad funcional conociendo los argumentos y suponiéndose que es una funcionalidad determinista (es decir, que ante los mismos parámetros, siempre ofrecerá el mismo resultado) se comprueba el resultado obtenido por la ejecución de dicha lógica. Si el resultado proporcionado es igual al esperado el test pasa correctamente. Si no, se lanza una excepción que avisa del error. Éste, suele provocar la finalización del proceso de construcción de la aplicación.

Es importante recalcar que los test deben comprobar únicamente una funcionalidad. Deben ser pequeños y concisos, así que en cualquier proyecto se pueden acumular cientos de test con normalidad. Los test pequeños y concretos son más fáciles de mantener, de probar y sobreviven con más frecuencia a los cambios de las aplicaciones.

#### Principios SOLID y DRY

#### SOLID

Los principios SOLID son un conjunto de cinco principios de diseño de software orientados a objetos que promueven la creación de código más limpio, mantenible y flexible. Estos principios son: Responsabilidad Única, Abierto/Cerrado, Sustitución de Liskov, Segregación de Interfaces, e Inversión de Dependencias.

En detalle:

1. Principio de Responsabilidad Única (SRP):

Una clase o módulo debe tener una única razón para cambiar. En otras palabras, cada clase debe tener una única responsabilidad bien definida.

2. Principio Abierto/Cerrado (OCP):

Las entidades de software (clases, módulos, funciones, etc.) deben estar abiertas para la extensión, pero cerradas para la modificación. Esto significa que puedes agregar nuevas funcionalidades sin alterar el código existente.

3. Principio de Sustitución de Liskov (LSP):

Las subclases deben ser sustituibles por sus clases base sin alterar la corrección del programa. Esto asegura que las clases hijas no rompan el comportamiento esperado de las clases padres.

4. Principio de Segregación de Interfaces (ISP):

Los clientes no deben depender de interfaces que no utilizan. Es mejor crear interfaces más específicas para cada cliente en lugar de forzar a los clientes a depender de interfaces grandes y complejas que no necesitan.

5. Principio de Inversión de Dependencias (DIP):

Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones. Además, las abstracciones no deben depender de detalles, sino que los detalles deben depender de las abstracciones.

Al aplicar estos principios, se busca lograr un código más fácil de entender, modificar y extender, lo que resulta en sistemas de software más robustos y mantenibles.

#### DRY

El principio DRY (Don't Repeat Yourself) en programación es una práctica que busca evitar la duplicación de código. En lugar de copiar y pegar el mismo código en diferentes partes de un programa, se debe buscar una única representación o fuente de verdad para esa funcionalidad, que pueda ser reutilizada. Esto promueve la creación de código más limpio, legible y fácil de mantener, reduciendo errores y facilitando las actualizaciones.

En resumen, DRY significa:

No repetir código:

Evitar copiar y pegar fragmentos de código idénticos o similares en diferentes lugares del programa.

Crear una única fuente de verdad:

Encontrar la forma de encapsular la lógica duplicada en una función, clase, módulo o cualquier otra estructura reutilizable.

Reutilizar código:

En lugar de duplicar el código, llamarlo o acceder a él desde diferentes partes del programa cuando sea necesario.

¿Por qué es importante DRY?

Reducción de errores:

Al tener una única implementación de una funcionalidad, es más fácil corregir errores y mantener el código consistente. Si un error se encuentra en una funcionalidad reutilizada, solo necesita ser corregido en un lugar.

Mejora de la mantenibilidad:

Código más limpio y modular es más fácil de entender y modificar, lo que facilita las actualizaciones y la corrección de errores a largo plazo.

Aumento de la reutilización:

Las funciones y componentes reutilizables pueden ser utilizados en diferentes partes del proyecto, ahorrando tiempo y esfuerzo.

Mayor legibilidad:

Al evitar la repetición, el código se vuelve más claro y conciso, facilitando su comprensión.

Ejemplos de cómo aplicar DRY:

Funciones:

En lugar de repetir el mismo código para calcular el área de diferentes figuras, se puede crear una función calcular_area(figura, datos) que reciba el tipo de figura y sus datos como parámetros.

Clases:

Si varias clases comparten la misma lógica, se puede crear una clase base con esa lógica y hacer que las otras clases hereden de ella.

Módulos:

Se pueden crear módulos con funcionalidades comunes y reutilizarlos en diferentes partes del programa.

En esencia, el principio DRY es una práctica que ayuda a los desarrolladores a escribir código más eficiente, mantenible y con menos errores, promoviendo la reutilización y la claridad del código.

#### aplicar DDD, TDD y principios SOLID y DRY a la vez

Sí, es posible aplicar DDD (Desarrollo Dirigido por Dominio), TDD (Desarrollo Guiado por Pruebas) y los principios SOLID y DRY simultáneamente en el desarrollo de software. De hecho, estas prácticas se complementan y pueden mejorar la calidad y mantenibilidad del código.

Elaboración:

DDD (Desarrollo Dirigido por el Dominio):

Se centra en modelar el software de acuerdo con el dominio del problema, utilizando conceptos y vocabulario del negocio. Esto ayuda a crear un modelo de software que sea más comprensible y relevante para los usuarios y expertos en el dominio.

TDD (Desarrollo Guiado por Pruebas):

Es una metodología de desarrollo que implica escribir pruebas antes que el código de producción. Se escribe una prueba para una funcionalidad específica, luego se escribe el código mínimo para que la prueba pase, y finalmente se refactoriza el código.

Principios SOLID:

Son un conjunto de principios de diseño de software que promueven la flexibilidad, mantenibilidad y reutilización del código. Los principios SOLID incluyen:

Principio de Responsabilidad Única (SRP): Cada clase o módulo debe tener una sola razón para cambiar.

Principio Abierto/Cerrado (OCP): Las entidades de software (clases, módulos, funciones, etc.) deben estar abiertas para la extensión, pero cerradas para la modificación.

Principio de Sustitución de Liskov (LSP): Las subclases deben ser sustituibles por sus clases base.

Principio de Segregación de Interfaces (ISP): Los clientes no deben depender de interfaces que no utilizan.

Principio de Inversión de Dependencias (DIP): Las dependencias deben ser abstraídas y no deben depender de detalles concretos.

Principio DRY (Don't Repeat Yourself):

Evita la duplicación de código, promoviendo la reutilización y la mantenibilidad.

Relación entre ellos:

DDD y TDD se complementan bien. El modelado del dominio en DDD ayuda a definir las pruebas en TDD, asegurando que el código refleje el lenguaje y los conceptos del negocio.

Los principios SOLID ayudan a diseñar un código más robusto y mantenible, lo cual es crucial cuando se trabaja con un dominio complejo modelado en DDD y con pruebas escritas con TDD.

El principio DRY ayuda a mantener el código limpio y consistente, reduciendo la redundancia y la posibilidad de errores.

En resumen, aplicar estas prácticas de forma conjunta:

Fomenta un código más robusto y fácil de entender, ya que se basa en el dominio del problema y sigue principios de diseño sólidos.

Mejora la calidad del código al reducir errores y facilitar la mantenibilidad.

Facilita la evolución del software, ya que el diseño se adapta a los cambios del dominio y las pruebas automatizadas aseguran que las modificaciones no introduzcan nuevos errores.

Por lo tanto, la combinación de DDD, TDD y los principios SOLID y DRY puede conducir a un desarrollo de software más efectivo y de alta calidad.

## Recursos formativos

## Sintaxis Mermaid para el diagrama de arquitectura

flowchart TD

%% User Side

subgraph User["User's PC"]

Browser["Browser"]

Widget["Meri-bot Widget"]

end

subgraph Web["C&CA Web Server"]

Page["Intranet Web Page"]

end

%% FastAPI service in container

subgraph App["Container"]

API["FastAPI Service"]

LangChain["LangChain Logic"]

end

%% Vector Database

subgraph DB["DB Backend"]

VectorDB["ChromaDB / Pinecone"]

end

%% Web Scraper (PC or Cron)

subgraph ScraperHost["Scraper Host"]

Scraper["WebScraper (Python Console)"]

Cron["Cron Job"]

end

%% Flows

Browser -- "accesses" --> Page

Page -- "loads" --> Widget

Widget -- "HTTP request" --> API

API -- "query" --> VectorDB

Scraper -- "extracts & ingests" --> VectorDB

Cron -- "schedules" --> Scraper

API -- "uses" --> LangChain

Widget -- "shows result" --> Browser

%% Security boundaries & comms

Page -.->|embeds| Widget

Browser -. "user actions" .-> Widget

VectorDB -.->|data| API

ScraperHost -. "batch ingest" .-> VectorDB

App -.->|isolated| DB

Web -.->|serves| Page

## meri-cli: Herramienta de línea de comandos para la gestión y el crawling de Meribot

meri-cli es la utilidad en línea de comandos asociada a Meri-bot, pensada para realizar todas las operaciones técnicas y administrativas fuera del entorno web. Su objetivo es facilitar la gestión de fuentes, documentos y la base de datos vectorial, así como permitir operaciones de crawling programáticas o manuales de manera segura y controlada.

### Estructura general

El comando principal es meri-cli, al que se le indican sub comandos y parámetros:

meri-cli [subcomando] [opciones]

### Subcomando: crawl

El subcomando crawl permite lanzar procesos de crawling (exploración automática) sobre una URL inicial, recolectando documentos para su posterior procesamiento e ingesta en la base vectorial.

#### Sintaxis básica

meri-cli crawl --url <URL_INICIAL> [opciones]

#### Opciones y parámetros

(Los que están marcados como “Opcional” se podrían descartar para el MVP. Que si tendrá que estar implementados son los valores por defecto)

--url <URL_INICIAL> (Obligatorio) URL de inicio de la sesión de crawling. Debe pertenecer al dominio permitido; el crawler nunca saldrá de este dominio base.

--max-depth <N> (Opcional) Profundidad máxima de navegación de enlaces a partir de la URL inicial. Por defecto: 2.

--max-pages <N> (Opcional) Número máximo de páginas a explorar en la sesión. Por defecto: sin límite.

--include <regex> (Opcional) Solo incluir URLs que cumplan el patrón indicado (expresión regular).

--exclude <regex> (Opcional) Excluir URLs que cumplan el patrón (ejemplo: rutas de logout, privadas, etc.).

--formats <ext1,ext2,...> (Opcional) Lista de formatos de archivo a recolectar (por ejemplo: html,pdf,docx). Por defecto: todos los soportados.

--output <directorio> (Opcional) Carpeta destino para guardar los documentos descargados o procesados.

--update-only (Opcional) Solo actualiza documentos nuevos o modificados desde la última sesión.

--dry-run (Opcional) Simula el crawling y reporta los documentos/URLs que serían procesados, sin descargar ni guardar nada.

--manual (Opcional) Permite indicar manualmente una lista de URLs a procesar en vez de hacer crawling iterativo.

#### Ejemplos de uso

meri-cli crawl --url https://intranet.capgemini.com/recursos --max-depth 3 --formats pdf,docx

meri-cli crawl --url https://intranet.capgemini.com/rrhh --exclude "/privado/" --dry-run

meri-cli crawl --manual --url https://intranet.capgemini.com/doc1.pdf --url https://intranet.capgemini.com/doc2.pdf

### Subcomando: db

El subcomando db permite interactuar directamente con la base de datos vectorial de documentos ya ingeridos. Es útil para tareas de administración, control de versiones, limpieza y auditoría.

#### Sintaxis básica

meri-cli db [opción] [parámetros]

#### Opciones disponibles

list Lista todos los documentos actualmente almacenados, mostrando información relevante (ID, nombre, dominio, fecha de ingreso, versión, etc.).

Opciones para list:

--filter <campo>:<valor> Filtra la lista de documentos por dominio, fecha, tipo, etc.

--show-chunks Muestra también el número de fragmentos (chunks) asociados a cada documento.

delete --id <DOCUMENT_ID> Elimina de la base vectorial todos los fragmentos asociados a un documento específico.

show --id <DOCUMENT_ID> Muestra información detallada y metadatos del documento y/o los fragmentos asociados.

count Devuelve el número total de documentos y/o fragmentos almacenados.

#### Ejemplos de uso

meri-cli db list

meri-cli db list --filter dominio:Talent --show-chunks

meri-cli db show --id 8fa9e

meri-cli db delete --id 8fa9e

meri-cli db count

### Notas

Todas las operaciones de crawling respetan el dominio base de la URL inicial, sin seguir enlaces externos.

Los parámetros de filtrado y exclusión permiten controlar exhaustivamente el ámbito del crawling y evitar la ingesta de documentos no deseados.

Toda actualización de un documento implica la eliminación previa de sus fragmentos antiguos en la base vectorial, garantizando que solo haya una versión activa de cada documento.

Las acciones manuales (ingesta puntual de URLs, borrado de documentos, etc.) requieren permisos de administración (implementado como mecanismo de contraseña sencilla en la primera versión) y quedan registradas para auditoría.

# Alcance y cambios

El alcance está definido en el documento original y no debe cambiarse salvo que exista una necesidad de negocio urgente y muy clara. Si algún área del cliente propone una ampliación, hay que justificar el valor real para el negocio. No se aceptan nuevas funcionalidades sin justificación sólida. Es decir: deberiamos tratar este proyecto real (lo es!) y cambio de alcance no puede ser una decision de equipo