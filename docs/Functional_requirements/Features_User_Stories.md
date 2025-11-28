# INDICE
# 🧩 FUNCIONALES. Meri-bot-Interfaz de Usuario /web 4
## Feature 1: Web-Interfaz Meri-bot y acceso a Panel de conversación 5
### (MVP) USF001-001: Acceso a Meri-bot desde la web de C&CA mediante Icono Flotante (Burbuja de chat) 5
### (Descartado) USF001-00x: Acceso a Meri-bot desde la web de C&CA mediante Caja de Texto 6
## Feature 2: Web-Panel de conversación con historial 7
### (MVP) USF002-001: Panel flotante de conversación desde el icono flotante 8
### (MVP) USF002-002: Filtro de dominios temáticos 9
### (MVP) USF002-003: Píldoras de valores seleccionados en el filtro 10
### (MVP) USF002-004: Bloque Conversacional del usuario sobre documentación interna 10
### (MVP) USF002-005: Bloque de Historial en Panel de conversación 11
### (MVP) USF002-006: Indicador progresivo de respuesta en proceso 12
### (No MVP) USF002-007: Entrega progresiva de Respuesta 13
### (MVP) USF002-008: Respuesta de Meri-bot 13
### (MVP) USF002-009: Enlaces a documentos utilizados en la respuesta 14
### (MVP) USF002-010: Multilingüismo en la interacción 15
### (MVP) USF002-011: Bloque de Aviso de responsabilidad en Panel de conversación 15
### (MVP) USF002-012: Cierre de Panel de conversación y reinicio de historial 16
### (No MVP) USF002-013 Feedback 16
### (No MVP) USF002-014: Fuentes como citas 17
# ⚙️ TÉCNICAS. Meri-bot- Lógica de Aplicación - scraper- RAG 17
## Feature 3: Crawler-Extracción (Scraper) e Ingesta de fragmentos documentos en BBDD vectorial - /crawler 17
### (MVP) USF003-001: Fuentes de scraping 18
### (MVP) USF003-002: Configuración de Descubrimiento y Alcance 19
### (MVP) USF003-003: Extracción y Normalización. Reglas de Scraping 20
### (MVP) USF003-004: Estructuración. Procesamiento y Filtrado. Parseo de documentos. Embeddings. Fragmentación semántica 21
### (MVP) USF003-005: Almacenamiento en BBDD vectorial 21
### (MVP) USF003-006: Evitar la reindexación de documentos idénticos 22
### (No MVP) USF003-007: Reintento de ingesta 22
### (MVP) USF003-008: Logging. Observabilidad y Administración 22
### (No MVP) USF003-009: Autenticación en Scraper 23
## Feature 4: Core-Motor de consulta conversacional. Recepción y procesamiento de consulta. Recuperación de documentos /core y /api 23
### (MVP) USF004-001: Recepción de pregunta de usuario con posibilidad de dominios 24
### (MVP) USF004-002: Configuración de parámetros del motor de consulta 24
### (MVP) USF004-003: Validación de pregunta de usuario (Input Guardrails antes de la consulta al modelo) 24
### (MVP) USF004-004: Extracción de información por dominios de la BBDD vectorial 26
### (MVP) USF004-005: System prompt+ User Prompt. Generación de respuesta en lenguaje natural 26
### (No MVP) USF004-006: Optimización en la entrega de respuestas frecuentes 28
### (MVP) USF004-007: Contexto de la conversación 28
### (MVP) USF004-008: Logging. Registro de consultas y respuestas 29
### (No MVP) USF004-009: Output Guardrails (Post-filtro y validación, tras la generación de respuesta) 29
### (No MVP) USF004-010: Protección contra Ataques Adversariales 30
### (No MVP) USF004-011: Privacidad y Control de Acceso 30
## Feature 5: Services-Gestión de Almacenamiento vectorial con metadatos /services/storage 30
### (No MVP) USF005-001: Privilegios y seguridad de la BBDD 31
### (MVP) USF005-002: Identificación de documentos 31
### (MVP) USF005-003: Definición de fragmentos de documentos. Metadata 31
### (No MVP) USF005-004: Re-Indexación 32
### (No MVP) USF005-005: Numeración de fragmentos de documentos 32
# 🛠️ ADMINISTRACIÓN. Meri-cli. Gestión administrativa por línea de comandos -  /meri-cli 32
## Feature 6: Meri-cli-Configuración de fuentes, dominios, documentos críticos y formato de documentos 33
### (MVP) USF006-001: Configuración de fuentes de scraping (inclusión/exclusión) 33
### (No MVP) USF006-002: Configuración de documentos críticos a escrapear 34
### (MVP) USF006-003: Configuración de dominios temáticos 34
### (MVP) USF006-004: Configuración de formatos de documentos a parsear 34
## Feature 7: Meri-cli-Configuración de crawler/scraping 34
### (MVP) USF007-001: Scraping Planificado 34
### (MVP) USF007-002: Scraping bajo demanda y Actualización de documentos críticos 35
### (MVP) USF007-003: Scraping en modo simulación 35
### (MVP) USF007-004: Monitoreo en tiempo real 36
### (No MVP) USF007-005: Reporte y resultados 36
### (MVP) USF007-006: Gestión de fallos 36
## Feature 8: Meri-cli-Gestión de la base vectorial 36
### (MVP) USF008-001: Visualización del número de fragmentos por documento 37
### (MVP) USF008-002: Consulta, y eliminación de documentos 37
### (No MVP) USF008-003: Reindexaciones 37
### (No MVP) USF008-004: Realizar pruebas y validaciones previas 37
## Feature 9: Meri-cli-Configuración de system prompt 37
### (No MVP) USF009-001: Configuración del system prompt 38
## (No MVP) Feature 10: Meri-cli-Loggins. Trazabilidad y Auditoría 38
### USF010-001: Registro de operaciones técnicas 41
### USF010-002: Registro de consultas y respuestas 41
### USF010-003: Visualización en log: Procesos backend 41
### USF010-004: Visualización en log: Métricas 41
### USF010-005: Visualización en log: Alertas 41
## (Fuera de Scope) Feature 11: Meri-cli-Control de acceso a dominios 42
---------------------------------------------------------------------------------------------------------
# 🧩 FUNCIONALES. Meri-bot-Interfaz de Usuario /web
> **Objetivo**
El componente Meri-Bot se presenta como un widget HTML que se integra fácilmente en cualquier portal interno sin requerir autenticación ni lógica de IA en el cliente. La comunicación se realiza vía HTTP con el motor conversacional (FastAPI).
**Funciones Clave**
Frontend Web (Widget HTML embebido)
Rol: Interfaz de usuario para interacción con Meri-Bot.
Tipo de conexión: Comunicación HTTP con el motor FastAPI.*
Consideraciones:
No requiere autenticación ni lógica de IA.
Se integra fácilmente en cualquier portal interno.
Muestra respuestas y gestiona el panel de conversación.
Elementos del Widget
Burbuja de Chat: Icono flotante ubicado en la esquina inferior derecha del portal.
Panel Central Superpuesto: Panel flotante que se activa al hacer clic en el icono.
**Flujo de Interacción**
Secuencia de uso del widget por parte del usuario:
El usuario accede al portal corporativo y hace clic en la burbuja de Meri-Bot.
Se abre un panel central centrado, flotante y superpuesto sobre la página corporativa, donde el usuario puede comenzar a realizar consultas.
El panel permite visualizar todo el historial de la sesión mediante scroll, y reiniciar la sesión desde el aspa(X), en su esquina superior derecha.
El panel incluye un botón para aplicar filtros de búsqueda por dominio temático.
## Feature 1: Web-Interfaz Meri-bot y acceso a Panel de conversación
### (MVP) USF001-001: Acceso a Meri-bot desde la web de C&CA mediante Icono Flotante (Burbuja de chat)
> **Descripción**
Icono flotante de Meri-bot, sin interrumpir la navegación en el portal anfitrión que lo aloja.
> **Definición**
> Como empleado que ha entrado en la web corporativa C&CA,
> Quiero identificar el chatBOT conversacional Meri-bot de forma rápida y no invasiva, mediante un icono y un mensaje amigable que incite a iniciar una conversación
> Para facilitar su identificación y poder iniciar una conversación de forma intuitiva sin interrumpir mi navegación por la web
> **Criterios de Aceptación**
- ✅ El icono flotante Meri-bot debe estar embebido en el portal anfitrión sin necesidad de instalación.
- ✅ Todo empleado que tiene acceso al portal anfitrión, tiene acceso a Meri-bot.
- ✅ Meri-bot no autentifica ni recoge credenciales del usuario.
- ✅El icono flotante Meri-bot tiene un diseño atractivo, limpio y minimalista y un estilo coherente con el portal anfitrión
- ✅El icono flotante Meri-bot se ubica en la esquina inferior derecha de cualquier página del portal anfitrión.
- ✅El icono flotante Meri-bot incluye imagen Meri-bot o avatar, y un mensaje amigable que invite al usuario a iniciar la interacción con Meri-bot. Mensaje sugerido:
“Pregunta a Meri-bot”
- ✅Al clicar en el icono flotante, se despliega el panel de conversación flotante.
**Requisitos UX/UI**
Elemento de navegación/interacción elegida: Icono flotante que iniciar la conversación con meri-bot en panel de conversación
El icono flotante debe tener un diseño atractivo, limpio y minimalista y estilo (elementos visuales, forma, medida, color, textura) coherente con el portal anfitrión (.css). El icono flotante es amplio y con tamaño de fuente que permita visualizar claramente el texto. Nota: El css del portal anfitrión está disponible en /Cloud & Custom Applications_files/styles-2QPKW3UZ.css
Y debe cumplir con los principios de:
Integración ligera, desacoplada y no invasiva en el portal anfitrión
Usabilidad con responsive design, contraste de colores, tipografía legible, minimización de carga cognitiva
Accesibilidad (visualización clara),
Eficiencia
Satisfacción y
Utilidad
**Requisitos Técnicos**
Integración ligera en la web corporativa C&CA bajada a local (archivo Cloud & Custom Applications.html)
Sin uso de librerías pesadas.
### (Descartado) USF001-00x: Acceso a Meri-bot desde la web de C&CA mediante Caja de Texto
> **Descripción**
Widget HTML con bienvenida y presentación de Meri-bot, con filtro y caja de Texto para consulta y botón de envío de la consulta , sin interrumpir la navegación en el portal anfitrión que lo aloja.
> **Definición**
> Como empleado que ha entrado en la web corporativa C&CA,
> Quiero identificar el chatBOT conversacional Meri-bot de forma rápida y no invasiva, mediante un mensaje de bienvenida y presentación de Meri-bot, con filtro y una caja de texto donde escribir mi pregunta para Meri-bot
> Para incentivar mi curiosidad y poder iniciar una conversación de forma intuitiva sin interrumpir mi navegación por la web
**Criterios de Aceptación**
- ✅ El widget Meri-bot está embebido en el portal anfitrión sin necesidad de instalación.
- ✅El widget Meri-bot se ubica en la parte superior izquierda de la home page del portal anfitrión, justo encima del texto “Ya eres parte de “
- ✅ Todo empleado que tiene acceso al portal anfitrión, tiene acceso a Meri-bot.
- ✅ Meri-bot no autentifica ni recoge credenciales del usuario.
- ✅El widget Meri-bot tiene un diseño atractivo, motivador, limpio y minimalista y un estilo coherente con el portal anfitrión.
- ✅El widget Meri-bot incluye cuadro de texto con un mensaje amigable de bienvenida que invite al usuario a iniciar la interacción con Meri-bot. Mensaje sugerido:
“Hola, soy Meri, ¿cómo puedo ayudarte hoy?”
- ✅Se incluye un filtro minimalista/selector múltiple de dominios temáticos, seguido de la caja de texto multilínea donde el usuario puede escribir y visualizar cómodamente su pregunta antes de enviarla
- ✅ Cada uno de los valores seleccionados por el usuario en el filtro de dominios antes de enviar la pregunta, se deben mostrar como “píldoras” resaltadas encima del cuadro de texto de la pregunta
- ✅Al enviar una consulta, se despliega el panel de conversación flotante.
**Requisitos UX/UI**
Elemento de navegación elegido: Widget
Elemento de interacción elegido: Cuadro de Texto para iniciar la conversación con meri-bot en panel de conversación
El widget debe tener un diseño intuitivo, navegación sencilla, atractivo, limpio y minimalista y estilo (elementos visuales, forma, medida, color, textura) coherente con el portal anfitrión (.css). Nota: El css del portal anfitrión está disponible en /Cloud & Custom Applications_files/styles-2QPKW3UZ.css
Y debe cumplir con los principios de:
Integración ligera, desacoplada y no invasiva en el portal anfitrión
Usabilidad con responsive design, contraste de colores, tipografía legible, minimización de carga cognitiva
Accesibilidad (visualizar claramente todos los componentes),
Eficiencia
Satisfacción y
Utilidad
**Requisitos Técnicos**
Integración en la web corporativa C&CA bajada a local (archivo Cloud & Custom Applications.html) mediante HTML y JavaScript embebido.
Sin uso de librerías pesadas.
## Feature 2: Web-Panel de conversación con historial
Panel de conversación flotante con historial temporal. Al entrar en Meri-bot, se abre un panel flotante sobre la web que permite mantener una conversación continua con la IA.
### (MVP) USF002-001: Panel flotante de conversación desde el icono flotante
> **Definición**
> Como empleado que ha accedido a Meri-bot,
> Quiero que se abra un panel de conversación
> Para realizar preguntas en lenguaje natural sobre la información interna de la empresa, manteniendo una conversación continua y fluida similar a ChatGPT, evitando la sensación de un “chatbot tradicional”
**Criterios de Aceptación**
- ✅El usuario puede activar el panel de conversación haciendo click sobre el icono flotante
- ✅El panel de conversación se despliega inmediatamente sin pantallas intermedias. Panel centrado, flotante y superpuesto sobre la página corporativa
- ✅El panel de conversación es una pop-up flotante cuyo diseño es coherente con el portal anfitrión.
- ✅El panel consta de 3 bloques bien diferenciados:
El bloque de historial de conversación,
El bloque conversacional con filtro de dominios seguido de la caja de texto multilínea para la pregunta del usuario
El bloque con un mensaje de aviso de responsabilidad
- ✅ Al abrir el panel, el historial debe estar vacío.
- ✅El panel de conversación presenta un scroll lateral para facilitar la visualización de todo el panel
- ✅El panel muestra un header con icono/avatar de Meri-bot, un título del tipo “Mi Conversación con Meri-bot”, y Botón (aspa) de cierre de panel
**Requisitos UX/UI**
Elemento de contenidos elegido: pop-up flotante
El panel de conversación debe tener un diseño intuitivo, navegación sencilla, atractivo, limpio y minimalista y estilo (elementos visuales, forma, medida, color, textura) coherente con el portal anfitrión (.css). Nota: El css del portal anfitrión está disponible en /Cloud & Custom Applications_files/styles-2QPKW3UZ.css
Y debe cumplir con los principios de:
Integración ligera, desacoplada y no invasiva en el portal anfitrión
Usabilidad con responsive design, contraste de colores, tipografía legible, minimización de carga cognitiva
Accesibilidad (visualizar claramente todos los componentes). El panel es amplio y con tamaño de fuente que permita visualizar claramente todo su contenido
Eficiencia
Satisfacción y
Utilidad
**Requisitos Técnicos**
NO es una pop-up tradicional de JavaScript, sino un <div> posicionado con atributos/properties CSS apropiados
### (MVP) USF002-002: Filtro de dominios temáticos
> **Descripción**
El sistema permite al usuario aplicar filtros temáticos para acotar los resultados de búsqueda. Estos filtros se presentan como un botón junto a la caja de búsqueda, desplegando un menú con dominios disponibles como “RRHH” y “Formación”.
Características:
Selección de uno, varios o ningún Dominio.
Visualización de dominios seleccionados como etiquetas.
Eliminación individual de etiquetas.
Persistencia de filtros entre mensajes.
El sistema limita la búsqueda a los documentos del dominio o dominios seleccionados.
> **Definición**
> Como empleado que ha accedido a Meri-bot
> Quiero poder seleccionar dominios temáticos (uno/ninguno/varios o todos) antes de enviar mi consulta
> Para obtener respuestas de Meri-bot más precisas y contextualizadas acotadas a los documentos pertenecientes a estos dominios.
**Criterios de Aceptación**
- ✅ El filtro de dominios permite selección múltiple.
- ✅ Los valores ofrecidos se recuperan del [fichero de configuración de dominios]
- ✅ El filtro ofrece tres valores iniciales: Formación, Onboarding y Talent, recogidos del [fichero de configuración de dominios]
- ✅El despliegue de las opciones es minimalista y se muestra justo al lado del botón del filtro para no perder el foco
- ✅Los valores seleccionados en el filtro deben ser enviados, junto con la pregunta, a la capa de procesamiento de la consulta
**Requisitos UX/UI**
Elemento de interacción elegido: Botón de filtro desplegable que permite selección múltiple
El filtro debe tener un diseño atractivo, limpio y minimalista y estilo (elementos visuales, forma, medida, color, textura) coherente con el portal anfitrión (.css)
Debe ocupar el menor espacio posible.
Requisitos técnicos
El filtro debe ser dinámico y permitir desmarcar opciones.
Puede evolucionar hacia filtros más avanzados.
Necesidad de llamada a endpoint de dominios para obtener todos los dominios
### (MVP) USF002-003: Píldoras de valores seleccionados en el filtro
> **Definición**
> Como empleado que ha accedido a Meri-bot y que ha seleccionado uno/varios dominios temáticos,
> Quiero poder ver los filtros seleccionados como píldoras resaltadas,
> Para poder identificar claramente los filtros seleccionados.
**Criterios de Aceptación**
- ✅ Cada uno de los valores seleccionados por el usuario en el filtro de dominios, deben mostrarse como “píldoras” resaltadas encima/delante del cuadro de texto de la pregunta
**Requisitos UX/UI**
Elemento de interacción elegido: cuadro de texto no editable y resaltado
Las píldoras deben tener un diseño atractivo, limpio y minimalista y estilo (elementos visuales, forma, medida, color, textura) coherente con el portal anfitrión (.css)
Visualización de dominios seleccionados como etiquetas.
Eliminación individual de etiquetas.
### (MVP) USF002-004: Bloque Conversacional del usuario sobre documentación interna
> **Descripción**
El usuario puede realizar preguntas en lenguaje natural sobre políticas, procedimientos y documentación interna a la práctica C&CA o general de RRHH, y recibir respuestas claras y contextualizadas.
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero poder realizar preguntas en lenguaje natural sobre información interna de la empresa,
> Para acelerar el acceso a políticas internas de C&CA o de RRHH, documentación técnica, procedimientos y obtener respuestas claras y relevantes a dudas administrativas.
**Criterios de Aceptación**
- ✅ Se muestra la caja de texto multilínea donde el usuario puede filtrar por dominios temáticos, escribir y visualizar cómodamente su pregunta antes de enviarla.
- ✅ Se muestra dentro de la caja de texto, un filtro minimalista/selector múltiple de dominios temáticos
- ✅ Dentro de la caja de texto y a la derecha del icono de filtro, el usuario puede escribir y visualizar cómodamente su pregunta antes de enviarla.
- ✅ Dentro de la caja de texto se muestra el botón de envío de la pregunta.
- ✅ Cuando el usuario envía su pregunta, se desactiva temporalmente la posibilidad de enviar nuevas consultas hasta recibir la respuesta a esta pregunta.
**Requisitos Técnicos**
Comunicación con backend vía HTTP a FastAPI
Al pulsar el botón de envío de la pregunta, se debe enviar la petición completa (idioma de la pregunta, dominios seleccionados y la pregunta).
La lógica de backend debe respetar estas preferencias (idioma de la pregunta, dominios seleccionados)
### (MVP) USF002-005: Bloque de Historial en Panel de conversación
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero disponer del historial de la conversación pregunta-respuesta y poder visualizar los documentos en los que se basa la respuesta
> Para profundizar más en la información y verificar la veracidad de la información
**Criterios de Aceptación**
- ✅ El bloque tiene estilo conversacional diferenciado que permite distinguir claramente entre las preguntas del usuario y las respuestas de Meri-bot.
- ✅ El bloque tiene scroll lateral para facilitar la visualización del historial con todas las preguntas y sus respuestas
- ✅ Durante la conversación, se muestra el historial completo en bloques de pregunta-respuesta
- ✅ Cada bloque de pregunta-respuesta presenta:
Bloque de pregunta en un cuadro:
- ✅ Dentro del cuadro, presenta la/s píldora/s con los valores seleccionados por el usuario en el filtro
- ✅Dentro del cuadro, presenta la pregunta del usuario
- ✅(No MVP) Presenta el icono/avatar del usuario “Tú” después del bloque de pregunta
Bloque de respuesta en un cuadro:
- ✅Presenta el icono/avatar de Meri-bot seguido del bloque de respuesta de Meri-bot
- ✅Dentro del cuadro, debajo de cada respuesta y ajustado a la derecha se muestra un icono de documentos, con tooltip “Ver Fuentes” que despliega un panel de enlaces a documentos utilizados en la respuesta
- ✅ Las preguntas y respuestas se diferencian visualmente mediante distinto color de fondo de las cajas de texto y distinto color de texto
**Requisitos UX/UI**
El bloque de historial debe tener un diseño atractivo, limpio y minimalista y estilo (elementos visuales, forma, medida, color, textura) coherente con el portal anfitrión (.css)
### (MVP) USF002-006: Indicador progresivo de respuesta en proceso
> **Descripción**
Se trata de diseñar una interfaz amigable y progresiva mientras Meri-bot procesa la respuesta para informar al usuario que el sistema está procesándola. De forma similar a como Adobe Acrobat presenta mensajes cortos con [Spinner o bolita giratoria + mensaje],
Ejemplo 1: Bolitas giratorias indicadoras de procesamiento
Ejemplo 2: Spinner
Inicial:
Spinner + mensaje:
⏳ Generando respuesta…
Progreso:
Spinner + mensaje intermedio:
- 🔄 Procesando contenido…
Casi listo:
Spinner con icono más definido + mensaje:
- ✅ Ya casi lo tengo…
> **Definición**
> Como empleado que ha lanzado una pregunta a Meri-bot,
> Quiero ver indicadores visuales progresivos mientras Meri-bot procesa mi pregunta,
> Para saber que mi solicitud está siendo atendida y evitar incertidumbre en la espera de la respuesta.
**Criterios de Aceptación**
- ✅Mientras se genera la respuesta, se muestran indicadores visuales animados (por ejemplo, puntos o pelotitas, o bien [Spinner + mensaje] ) para informar al usuario que el sistema está procesando la respuesta
- ✅El/los indicadores deben mostrarse en el bloque de historial de conversación, justo debajo de la pregunta enviada.
- ✅El indicador debe desaparecer en cuanto se muestre la respuesta de Meri-bot
**Requisitos UX/UI**
El indicador visual debe ser animado y claro, pero no invasivo
**Requisitos Técnicos**
Comunicación con backend vía HTTP a FastAPI
### (No MVP) USF002-007: Entrega progresiva de Respuesta (streaming)
> **Descripción**
Las respuestas de Meri-bot se muestran en modo streaming, revelando el texto conforme se generan los primeros caracteres, siguiendo el comportamiento estándar de los modelos de lenguaje como ChatGPT u Office365. Esto mejora la percepción de velocidad y la experiencia de usuario al reducir el tiempo de espera aparente.
> **Definición**
> Como empleado que ha lanzado una pregunta a Meri-bot,
> Quiero ver cómo la respuesta se va mostrando progresivamente mientras Meri-bot la genera,
> Para tener una experiencia más fluida, saber que el sistema está activo y empezar a comprender la respuesta sin esperar a que esté completa.
**Criterios de Aceptación**
- ✅Se muestra la respuesta en modo streaming revelando el texto conforme se generan los primeros caracteres, con fuente y filtros aplicados, simulando el comportamiento de modelos como ChatGPT.
**Requisitos Técnicos**
System prompt que lo incluya
### (MVP) USF002-008: Respuesta de Meri-bot
> **Definición**
> Como empleado que ha lanzado una pregunta a Meri-bot
> Quiero ver la respuesta precisa en lenguaje natural, contextualizada a los filtros seleccionados y en el idioma en el que le he hecho la pregunta,
> Para tener una respuesta precisa y veraz a mi pregunta.
**Criterios de Aceptación**
- ✅( MVP) Si la pregunta tiene contenido tóxico o inadecuado, entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa]. Ejemplo de mensaje:
- ❌  “Tu pregunta está fuera del ámbito de la intranet.”
- ❌ "Tu consulta contiene lenguaje inapropiado. Por favor, reformúlala para que podamos ayudarte."
- ❌ "No podemos procesar solicitudes que incluyan contenido ofensivo o dañino."
- ✅( MVP) Si la pregunta no es válida, por estar fuera del ámbito definido (ej. temas personales, externos), entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa]. Ejemplo de mensaje:
- ❌  “Tu pregunta está fuera del ámbito de la intranet.”
- ❌ "Tu consulta contiene lenguaje inapropiado. Por favor, reformúlala para que podamos ayudarte."
- ❌ "No podemos procesar solicitudes que incluyan contenido ofensivo o dañino."
- ✅( MVP) Si la pregunta presenta información sensible, como datos personales (nombres completos, direcciones, teléfonos, documentos de identidad, etc.) entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa]. Ejemplo de mensaje:
- 🔒 "Hemos detectado información personal en tu consulta. Por seguridad, la hemos anonimizado antes de continuar."
- 🔒 "Por favor, evita compartir datos personales como direcciones o números de identificación."
- ✅ (MVP) Si Meri-bot no puede generar una respuesta por error del sistema o porque no encuentra la información, entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa]. Ejemplos de mensaje:
- ⚠️ “No encontré información relevante, ¿quieres reformular tu pregunta?”
- ✅ (MVP) Si Meri-bot puede generar una respuesta relativa a la pregunta del usuario, entonces
- ✅Se muestra la respuesta precisa obtenida del fragmento de un documento (citas) o bien se muestra la respuesta como resumen de uno o varios documento/s
- ✅(No MVP) Si la respuesta de Meri-bot está desactualizada, entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa]. Ejemplo de mensaje:
- ⚠️ “La información puede estar desactualizada, última sincronización: [fecha].”
**Requisitos Técnicos**
Comunicación con backend (FastAPI)
### (MVP) USF002-009: Enlaces a documentos utilizados en la respuesta
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero ver un enlace a los documentos fuente utilizados en cada respuesta y poder visualizarlos
> Para poder verificar la veracidad de la respuesta o ampliar el contenido.
**Criterios de Aceptación**
- ✅Debajo de cada respuesta y ajustado a la derecha se muestra un icono de documentos, con tooltip “Ver Fuentes” que despliega un panel de enlaces a documentos utilizados en la respuesta
- ✅ El panel debe incluir al menos un enlace a un documento
- ✅ El enlace a un documento permite abrirlo y visualizarlo en una nueva pestaña o visor.
**Requisitos UX/UI**
El panel de enlaces es discreto y no invasivo.
El icono debe ser pequeño y reconocible.
El panel de enlaces debe respetar el diseño minimalista.
### (MVP) USF002-010: Multilingüismo en la interacción
> **Descripción**
Permitir que usuarios de distintos idiomas, especialmente aquellos que se comunican en inglés, puedan interactuar con Meri-Bot y recibir respuestas en ese idioma, incluso cuando los documentos fuente estén redactados en español, para garantizar una experiencia inclusiva, siguiendo el comportamiento estándar de los modelos de lenguaje como ChatGPT.
> **Definición**
> Como empleado internacional que está en una conversación con Meri-bot,
> Quiero que si pregunto a Meri-bot en un idioma, el sistema debe responder y continuar la interacción en ese idioma,
> Para poder visualizar las respuestas del chatbot en mi idioma preferido
**Criterios de Aceptación**
- ✅Meri-bot responde en el idioma de la pregunta.
- ✅Meri-bot mantiene el mismo idioma a lo largo de toda la conversación, mientras no se cambie el idioma en el que se formule la pregunta
**Requisitos Técnicos**
El LLM está entrenado para realizarlo.
Nota: Parece que no requiere implementación adicional, solo indicaciones en el system prompt
### (MVP) USF002-011: Bloque de Aviso de responsabilidad en Panel de conversación
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero ver un mensaje claro de responsabilidad en el panel flotante de Meribot
> Para entender que dicha información puede no ser 100% precisa, está sujeta a revisión humana y no debe tomarse como consejo profesional.
**Criterios de Aceptación**
- ✅ Debe mostrarse un mensaje visible que indique que Meri-bot puede tener errores.
- ✅ El mensaje debe incluir una recomendación de revisar las fuentes.
- ✅ Se muestra un mensaje de aviso de responsabilidad visible del tipo “Meri-bot puede tener errores. Por favor chequee las respuestas y las fuentes”.
### (MVP) USF002-012: Cierre de Panel de conversación y reinicio de historial
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero poder cerrar el panel de conversación y que al cerrarlo no se guarde el historial de conversación
> Para proteger mi privacidad y empezar una nueva sesión limpia cuando lo desee
**Criterios de Aceptación**
- ✅ El panel muestra en el header, un botón visible tipo aspa que me permite cerrarlo.
- ✅ Al cerrar el panel,
Se elimina el historial,
Redirige a la página del portal anfitrión desde la que se inició la conversación con Meri-bot
**Requisitos UX/UI**
El botón de Cierre debe ser un icono tipo aspa
### (No MVP) USF002-013 Feedback
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero poder valorar cada respuesta (útil/no útil) como feedback
> Para ayudar a mejorar la calidad del sistema.
**Criterios de Aceptación**
- ✅ Se muestran los botones de feedback debajo de la respuesta.
**Requisitos UX/UI**
botones de feedback (👍 / 👎)
**Requisitos Técnicos**
Se guarda el feedback del usuario con la finalidad de refinar reglas y para logging y auditoría
### (No MVP) USF002-014: Fuentes como citas
> **Descripción**
Mostrar las fuentes como citas, al estilo Anthropic, o como en Perplexity.ai en particular y en los trabajos de investigación en general. Cada respuesta presenta citas en el texto, dichas citas están numeradas y enlazan directamente a las referencias correspondientes.
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero la respuesta con generación con citas,
> Para que se muestren citas granulares en la respuesta, haciendo referencia a los números de los fragmentos y mostrando luego los propios fragmentos como extractos, como hace Perplexity.ai en particular y en los trabajos de investigación en general.
**Criterios de Aceptación**
--
**Requisitos UX/UI**
--
**Requisitos Técnicos**
System prompt con Inline Citations
-------------------------------------------------------------------------------------
# ⚙️ TÉCNICAS. Meri-bot- Lógica de Aplicación - scraper- RAG
## Feature 3: Crawler-Extracción (Scraper) e Ingesta de fragmentos documentos en BBDD vectorial
> **Objetivo**
Permitir la ingesta automatizada, estructurada y segura de documentos internos provenientes de fuentes corporativas (como SharePoint, Teams, etc.), transformándolos en fragmentos semánticos enriquecidos con metadatos para su posterior consulta mediante lenguaje natural.
Scraper Host:  Scraper en Python (Extracción, generación de embeddings/fragmentos, Ingesta en BBDD vectorial ChromaDB)
**Funciones Clave**
Scraping
El sistema debe realizar scraping sobre fuentes internas autorizadas.
Las fuentes incluyen portales como SharePoint, Teams entre otros.
Scraper en Python que extrae documentos desde
- (MVP) C&CA (.html)
- (No MVP) C&CA, SharePoint y Teams, Talent
Se debe permitir configurar reglas de inclusión/exclusión por URL, formato, profundidad, etc.
Fragmentación Semántica
Cada documento extraído se divide en fragmentos o “chunks” semánticos.
Cada fragmento se representa como un vector semántico (embedding) y se almacena en una base vectorial. ChromaDB será la base de datos a usar.
Todos los fragmentos de un mismo documento comparten un identificador único para facilitar su trazabilidad y actualización.
Enriquecimiento con Metadatos
Cada fragmento debe incluir metadatos como:
Dominio temático (ejemplo RRHH, Formación)
Fecha y Hora de ingesta.
Fuente original (URL y/o nombre del documento)
Tipo de documento
Identificador único del documento
Ingesta en Base Vectorial
Los fragmentos enriquecidos se almacenan en una base de datos vectorial que permite búsquedas semánticas eficientes.
La base debe soportar operaciones como búsqueda, filtrado, eliminación y auditoría.
Actualización Selectiva
El sistema debe permitir:
Actualización por lotes (batch) periódica mediante tareas programadas.
Actualización inmediata de documentos críticos.
Actualización manual y selectivas (documentos críticos), mediante meri-cli o monitorización de carpetas especiales (ej. biblioteca SharePoint), sin esperar al siguiente ciclo de scraping
Toda actualización implica la eliminación previa de los fragmentos antiguos para evitar versiones duplicadas.
### (MVP) USF003-001: Fuentes de scraping
> **Definición**
> Como administrador,
> Quiero que únicamente se realice scraping de fuentes de scraping internas autorizadas y contenidas en un [fichero de configuración de fuentes]
> Para mantener el sistema actualizado sin tocar el código.
Nota: Las fuentes de scraping pueden ser sitios web, paths, SharePoint/Teams
 (MVP) La fuente de scraping es la web interna C&CA
 (No MVP) Las fuentes de scraping son la la web interna C&CA, sharepoint/Teams de RRHH, posiblemente la web interna de RRHH (Talent)
**Criterios de Aceptación**
> - ✅ Se realiza scraping de cada una de las fuentes del [fichero de configuración de fuentes].
### (MVP) USF003-002: Configuración de Descubrimiento y Alcance
> **Definición**
> Como administrador,
> Quiero configurar dominios, rutas semilla y formatos de documentos
> Para limitar el alcance del Crawler a las fuentes de scraping internas autorizadas y para los tipos de documentos contenidos en ficheros de configuración
Nota:
[fichero de configuración de fuentes]
[fichero de configuración de formatos de documentos]
**Criterios de Aceptación**
- ✅ Configurado scraping para cada una de las fuentes del [fichero de configuración de fuentes].
 (MVP) Se recogerá de la web interna C&CA
 (No MVP) Se recogerá de la web interna C&CA, del sharepoint/Teams de RRHH y  de la web interna de RRHH (Talent)
- ✅ Configurado scraping  para cada uno de los tipos de documentos de un [fichero de configuración de formatos de documentos]
  (MVP) Los formatos permitidos son: HTML/PDF/Word (docx/doc), Excel (xlsx)
- ✅ Configuración de  seeds, allowed_domains, max_depth, file_types.
- ✅ Configuración de Validaciones: URLs válidas, dominios no vacíos, tipos soportados.
- ✅archivo de configuración (YAML/JSON) para seeds, dominios, límites, etc
**Requisitos Técnicos**
Semillas y límites: Configurar URLs semilla, dominios permitidos, profundidad máxima. -- Politeness: Rate limiting, user agent configurable, control de concurrencia. -- Descubrimiento de documentos: Detección y descarga de HTML, .docx, .xlsx, .pdf.
Configurabilidad y Exclusiones. -- Listas de inclusión/exclusión por patrón (URL, MIME, tamaño). -- Respeto opcional de robots.txt y sitemaps. -- Límite de tamaño por archivo y tiempo máximo de crawl.
 (No MVP) Robustez avanzada: -- Manejo de CAPTCHA/SSO (documentado, fuera del MVP). -- Renderizado opcional de JS con navegador headless (fuera del MVP). -- Alertas externas (Slack/Email) fuera de alcance del MVP.
### (MVP) USF003-003: Extracción y Normalización. Reglas de Scraping
> **Definición**
> Como administrador,
> Quiero que se definan reglas de scraping (recursividad, profundidad, exclusiones, rutas, patrones, comparar listas de documentos entre versiones)
> Para evitar que se recojan documentos irrelevantes o externos
**Criterios de Aceptación**
- ✅ El sistema debe generar una lista de documentos antes y después del scraping.
- ✅ Debe identificar documentos nuevos, modificados y eliminados.
- ✅ El scraper debe permitir excluir rutas por patrón (regex).
- ✅ Las exclusiones deben estar definidas en el fichero de configuración.
- ✅Páginas inaccesibles, timeouts y redirecciones circulares: registrar ERROR y continuar.
- ✅Documentos corruptos o con formato no soportado: registrar WARN/ERROR con mensaje estándar.
- ✅ciclos de enlaces y contenido duplicado: detección por historial y hash; evitar recrawl infinito.
- ✅Archivos muy grandes: abortar por límite configurado y registrar causa.
- ✅Recorrer URLs semilla, respetando límites de dominio y profundidad.
- ✅ Se detectan enlaces a HTML, .docx, .xlsx, .pdf.
**Requisitos Técnicos**
--Parser HTML: Limpieza, extracción de texto, títulos, encabezados, enlaces, metadatos. -- Parser de documentos: Extracción de texto y metadatos de Word, Excel y PDF. Parsers para cada tipo de fuente (HTML: BeautifulSoup/lxml - Word: python-docx - Excel: openpyxl - PDF: PyMuPDF o pdfminer)
-- Etiquetado por documento y por fragmento.
--Detección de Cambios  -- Comparación por metadatos (Last-Modified, ETag) y hash de contenido. -- Clasificación: nuevo, actualizado, sin cambios, inaccesible/corrupto.
### (MVP) USF003-004: Estructuración. Procesamiento y Filtrado. Parseo de documentos. Embeddings. Fragmentación semántica
> **Definición**
> Como administrador,
> Quiero que el crawler pueda trocear los documentos en fragmentos con metadatos,
> Para permitir la indexación, y facilitar búsqueda semántica
**Criterios de Aceptación**
- ✅ Se extrae texto principal y metadatos
- ✅Cada documento debe dividirse en fragmentos de tamaño configurable.
- ✅ Cada fragmento debe tener su vector semántico.
- ✅ Cada documento se normaliza y se divide en fragmentos con metadatos. Como: dominio, fecha, fuente (título, autor, versión, URL, etc), tipo de documento.
- ✅ Chunking configurable, preservando límites semánticos.
- ✅Todos los fragmentos de un mismo documento comparten un identificador único para facilitar su trazabilidad y actualización
- ✅Detección de duplicados y cambios
- ✅ Se calcula hash de contenido y se compara con versiones previas.
**Requisitos Técnicos**
Cada documento extraído se divide en fragmentos o “chunks” semánticos.
Cada fragmento se representa como un vector semántico (embedding) y se almacena en una base vectorial. ChromaDB será la base de datos a usar.
Todos los fragmentos de un mismo documento deben compartir un identificador único para facilitar su trazabilidad y actualización
-- Chunking: Segmentación del contenido en fragmentos coherentes con tamaño configurable. -- Enriquecimiento: Inclusión de metadatos (fuente, tipo, idioma, fechas). -
### (MVP) USF003-005: Almacenamiento en BBDD vectorial
> **Definición**
> Como administrador,
> Quiero que los documentos fragmentados se almacenen como vectores
> Para permitir búsquedas semánticas eficientes
**Criterios de Aceptación**
- ✅ Cada fragmento de un documento se almacena en la BBDD vectorial ChromaDB
- ✅ Todos los fragmentos de un documento tienen el mismo metadata y ID
- ✅ Se adaptan los datos extraídos al formato vectorial requerido.
- ✅ Upsert de fragmentos con claves determinísticas y metadatos.
**Requisitos Técnicos**
Persistencia: Upsert en ChromaDB con claves determinísticas.
### (MVP) USF003-006: Evitar la reindexación de documentos idénticos
> **Definición**
> Como administrador,
> Quiero que se detecten cambios por fecha de modificación y hash de contenido,
> Para evitar reindexar documentos idénticos
**Criterios de Aceptación**
- ✅ Comparación por fecha de modificación. El sistema debe verificar si la fecha de modificación del documento ha cambiado respecto a la última indexación.
- ✅Comparación por hash de contenido. Si la fecha de modificación no está disponible o no ha cambiado, el sistema debe calcular y comparar el hash del contenido para detectar cambios.
- ✅Evitar reindexación innecesaria. Los documentos que no presenten cambios en fecha ni en hash no deben ser reindexados.
- ✅Registro de decisiones. El sistema debe registrar si un documento fue reindexado o ignorado, indicando el motivo (fecha modificada, hash distinto, sin cambios).
- ✅Manejo de errores en metadatos. Si no se puede obtener la fecha o el contenido para calcular el hash, el sistema debe registrar un error y continuar con el resto del proceso.
**Requisitos Técnicos**
Cada documento extraído se divide en fragmentos o “chunks” semánticos.
### (No MVP) USF003-007: Reintento de ingesta
> **Definición**
> Como administrador,
> Quiero rententar la ingesta de elementos fallidos,
> Para completar el índice sin reprocesar todo.
### (MVP) USF003-008: Logging. Observabilidad y Administración. Registro
> **Definición**
> Como administrador,
> Quiero ver un resumen de resultados (nuevos, actualizados, no cambiados, errores)
> Para evaluar el éxito del proceso, diagnosticar y corregir problemas
**Criterios de Aceptación**
- ✅ Resumen visible al finalizar el proceso. Al completar el proceso de scraping, debe mostrarse un resumen con los siguientes datos: Número de elementos nuevos, Número de elementos actualizados, Número de elementos sin cambios, Número de errores detectados
- ✅ Formato estructurado del resumen. El resumen debe presentarse en un formato legible (tabla, JSON, o similar) que permita su interpretación rápida por el administrador
- ✅Accesibilidad del resumen. El resumen debe estar disponible desde la interfaz de administración o enviado por notificación (email, dashboard, etc.), según configuración
- ✅Identificación de errores. Los errores deben incluir información útil para diagnóstico: tipo de error, URL o fuente afectada, y timestamp.
- ✅Persistencia del resumen. El resumen debe guardarse en una base de datos o sistema de logs para futuras consultas o auditorías.
Criterios Técnicos
Definir nivel de logging necesario para auditoría
Se puede empezar con display de mensajes (prints por terminal) de todas las etapas del proceso.
Logging estructurado y niveles (INFO/WARN/ERROR). -- Reportes de ejecución y métricas básicas en Meri-Cli. -- Mensajes estándar de error y códigos de salida.
### (No MVP) USF003-009: Autenticación en Scraper
> **Definición**
> Como administrador,
> Quiero definir credenciales opcionales,
> Para acceder a contenidos protegidos si fuera necesario. (SharePoint/Teams de RRHH)
## Feature 4: Core+ api-Motor de consulta conversacional. Recepción y procesamiento de consulta. Recuperación de documentos /core y /api
Procesamiento de consulta y recuperación de documentos en fragmentos
> **Objetivo**
Procesa la pregunta en lenguaje natural mediante FastAPI + LangChain, accediendo a la BBDD vectorial ChromaDB. Gestiona el contexto, plugins de funcionalidades, respuestas frecuentes.
Debe proporcionar una interfaz programática clara (ChatEngine) para la integración con el módulo API.
Nota: NLP, o Procesamiento del Lenguaje Natural: Procesamiento de entendimiento de la consulta del usuario, interpretación y generación de respuesta en lenguaje natural.
### (MVP) USF004-001: Recepción de pregunta de usuario con posibilidad de dominios
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero poder seleccionar dominios temáticos (uno/ninguno/varios o todos) y mandar mi pregunta, sobre información interna de la empresa, en lenguaje natural,
> Para obtener respuestas de Meri-bot precisas y contextualizadas acotadas a los documentos pertenecientes a estos dominios, acelerando el acceso a políticas internas de C&CA o de RRHH, documentación técnica y procedimientos internos.
**Criterios de Aceptación**
- ✅ El sistema debe aceptar preguntas en lenguaje natural sin necesidad de comandos técnicos.
- ✅Se debe reconocer el idioma de la pregunta, el/los dominios seleccionados y la pregunta
**Requisitos Técnicos**
Comunicación con backend vía HTTP a FastAPI
/api
Necesidad de creación de endpoint de dominios para obtener todos los dominios
FastAPI
Recibe peticiones del Widget. Endpoint para procesarlas.
### (MVP) USF004-002: Configuración de parámetros del motor de consulta
> **Definición**
> Como desarrollador,
> Quiero poder configurar parámetros clave del motor de chat,
> Para adaptar el comportamiento del chatbot a las necesidades del negocio.
**Criterios de Aceptación**
- ✅ Parámetros admitidos question,  conversation_id, domains
- ✅ El sistema permite la configuración de parámetros clave (modelo, temperatura, tokens, caché) mediante variables de entorno o archivo de configuración.
### (MVP) USF004-003: Validación de pregunta de usuario (Input Guardrails antes de la consulta al modelo)
> **Descripción**
Comprueba que la consulta es válida y segura. El sistema valida las preguntas antes de enviarlas al modelo de IA, filtrando contenido tóxico, inadecuado o fuera de contexto
> **Definición**
> Como administrador,
quiero que el sistema valide las preguntas del usuario, y filtre contenido inadecuado o fuera de contexto en las preguntas del usuario
para aceptar consultas solo dentro del dominio esperado y evitar respuestas irrelevantes o incorrectas
**Criterios de Aceptación**
- ✅ Validación de contexto / dominio. El sistema debe mostrar un mensaje claro cuando una pregunta no sea válida, por estar fuera del ámbito definido (ej. temas personales, externos). Posibles acciones: Rechazar la consulta/Redirigir al usuario. Mensajes sugeridos:
- ⚠️ "Meribot está diseñado para responder preguntas relacionadas con [dominios]. ¿Podrías reformular tu consulta en ese contexto?"
- ⚠️ "Tu pregunta parece estar fuera del alcance de Meribot. ¿Te gustaría que te redirijamos a otro recurso?"
- ✅ Contenido tóxico o inadecuado. Detecta lenguaje ofensivo, violento, discriminatorio, sexual, etc. Posibles acciones: Bloquear la consulta/Solicitar reformulación. Mensajes sugeridos:
- ❌ "Tu consulta contiene lenguaje inapropiado. Por favor, reformúlala para que podamos ayudarte."
- ❌ "No podemos procesar solicitudes que incluyan contenido ofensivo o dañino."
- ✅Depuración de información sensible. Detecta datos personales como nombres completos, direcciones, teléfonos, documentos de identidad, etc. Posibles acciones: Eliminar o anonimizar la pregunta antes de enviar al modelo/Advertir al usuario. Mensajes sugeridos:
- 🔒 "Hemos detectado información personal en tu consulta. Por seguridad, la hemos anonimizado antes de continuar."
- 🔒 "Por favor, evita compartir datos personales como direcciones o números de identificación."
**Requisitos Técnicos**
FastAPI
Validación de datos con Pydantic
(No MVP) Registrar las preguntas rechazadas, fallos o respuestas conflictivas con el fin de Logging y auditoría, para registrar cuándo y por qué se activan los guardrails.
(No MVP) Usa clasificadores de contenido (como Detoxify, Perspective API, etc.) para evaluar toxicidad y sesgo.
### (MVP) USF004-004: Extracción de información por dominios de la BBDD vectorial
> **Descripción**
Se realiza la recuperación semántica vía embeddings y vector database.
> **Definición**
> Como usuario,
> Quiero que el sistema recupere información relevante, usando búsquedas semánticas de los documentos extraídos de las fuentes de datos internas, y que pertenezcan al/los dominio/s seleccionados,
> Para obtener respuestas precisas basadas en la documentación interna y confiar en la información que recibo
**Criterios de Aceptación**
- ✅La búsqueda de fragmentos de documentos se limita a los dominios seleccionados.
- ✅ La búsqueda de fragmentos de documentos debe limitarse a los dominios seleccionados por el usuario
- ✅ El sistema recupera fragmentos relevantes de documentos desde la base vectorial cuyo metadata de dominio coincida con el valor del dominio seleccionado por el usuario en el filtro de dominios.
- ✅ El sistema recupera al menos un fragmento relevante por cada pregunta válida.
- ✅ Los fragmentos recuperados están relacionados con el dominio seleccionado y semánticamente con la pregunta realizada
- ✅ Se recuperan como máximo fragmentos de 5 documentos (métrica configurable)
**Requisitos Técnicos**
Se realiza la recuperación semántica vía embeddings y vector database.
### (MVP) USF004-005: System prompt+ User Prompt. Generación de respuesta en lenguaje natural
> **Descripción**
Genera respuestas usando System Prompt + User Prompt.
Configuración del System Prompt
> **Definición**
> Como desarrollador,
> Quiero configurar el system prompt,
> Para definir el estilo y límites de las respuestas de la IA y garantizar que las respuestas sean rápidas, claras, útiles, que se basen únicamente en el contexto proporcionado y en el idioma de la pregunta del usuario.
**Criterios de Aceptación**
- ✅El system prompt es persistente y no puede ser alterado por el usuario.
- ✅ El prompt enviado al modelo debe incluir el system prompt y el user prompt:
- ✅El user prompt debe incluir el/los dominio/s seleccionado/s por el usuario, la preferencia de idioma, y la propia pregunta.
- ✅El system prompt debe incluir:
- ✅Tiempo de respuesta: Las respuestas deben generarse en segundos, gracias a la búsqueda semántica en la base vectorial. (métrica configurable)
- ✅Si Meri-bot no puede generar una respuesta por error del sistema o porque no encuentra la información suficiente, entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa] que invite al usuario a reformular la pregunta. Mensaje sugerido:
- ⚠️ “No encontré información relevante, ¿quieres reformular tu pregunta?”
- ✅Si Meri-bot puede generar una respuesta,
- ✅ Preferencia de idioma. La respuesta debe realizarse en el idioma de la consulta.
- ✅ La respuesta debe estar redactada de forma clara y comprensible.
- ✅ Las respuestas deben estar basadas únicamente en fragmentos de documentos relevantes y pertenecientes al dominio seleccionado por el usuario
- ✅la respuesta puede ser un resumen, pero el LLM no puede inventar, para que el usuario confíe en que la información proviene de fuentes reales
- ✅La respuesta se entrega citando las fuentes utilizadas, incluyendo los enlaces (URL) de los documentos originales y filtros aplicados.
- ✅(No MVP) Si la respuesta de Meri-bot está desactualizada: como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa]. Mensaje sugerido:
- ⚠️ “La información puede estar desactualizada, última sincronización: [fecha].”
- ✅(No MVP) Respuestas en streaming. Las respuestas se muestran progresivamente conforme se generan, sin esperar a que esté completa, mejorando la experiencia de usuario (como en ChatGPT u Office Copilot).
**Requisitos Técnicos**
Se configura el prompt enviado al modelo:
message[0]: role = "system", content = reglas y estilo.
message[1]: role = "user", content = consulta del usuario.
**Definición de reglas de comportamiento del modelo (tono, estilo, temas permitidos).**
Permitir extender la funcionalidad del chatbot mediante plugins para añadir nuevas capacidades sin modificar el núcleo del sistema.
El sistema debe ser accesible y seguro para garantizar el cumplimiento de estándares y la protección de la información
Debe permitir filtrar consultas por dominio o categoría, obteniendo la lista de dominios dinámicamente.
### (No MVP) USF004-006: Optimización en la entrega de respuestas frecuentes
> **Definición**
> Como usuario frecuente de Meri-bot,
> Quiero que las respuestas a preguntas comunes se sirvan rápidamente
> Para mejorar la experiencia y reducir la latencia.
**Criterios de Aceptación**
- ✅ Respuestas cacheadas disponibles. Las preguntas frecuentes deben tener respuestas almacenadas en caché para evitar consultas repetitivas al backend
- ✅ Tiempo de respuesta reducido. Las respuestas a preguntas comunes deben servirse en menos de X milisegundos (definir según SLA interno)
- ✅ Respuestas cacheadas disponibles. Las preguntas frecuentes deben tener respuestas almacenadas en caché para evitar consultas repetitivas al backend
**Requisitos Técnicos**
Debe gestionar una caché de respuestas frecuentes, con tiempo de vida configurable e invalidación automática
### (MVP) USF004-007: Contexto de la conversación
> **Definición**
> Como empleado que está en una conversación con Meri-bot,
> Quiero que el sistema mantenga el contexto de la conversación
> Para poder realizar preguntas de seguimiento y obtener respuestas coherentes.
**Criterios de Aceptación**
- ✅ El sistema debe mantener el contexto de las preguntas de una conversación durante la sesión activa del panel de conversación.
**Requisitos Técnicos**
Endpoint que mantiene el id de la conversación, filtros y contexto
### (MVP) USF004-008: Logging. Registro de consultas y respuestas
> **Definición**
> Como administrador,
> Quiero que todas las interacciones y procesos relevantes queden registrados en logs,
> Para facilitar el diagnóstico de errores y la mejora continua.
**Criterios de Aceptación**
- ✅ Cada interacción debe quedar registrada en un log con timestamp.
- ✅ El log debe incluir la pregunta y la respuesta, así como los metadatos relevantes (como es el dominio, la URL del documento usado en la respuesta, etc)
- ✅Se deben registrar logs de errores, eventos críticos y fallos de generación de respuesta.
Criterios Técnicos
Definir nivel de logging necesario para auditoría sin comprometer la privacidad
Se puede empezar con display de mensajes (prints por terminal) de todas las etapas del proceso.
Por ejemplo: Meter en la respuesta los prints para comprobar que se tiene la respuesta completa con los enlaces (citations, nombre de fichero y URL).
### (No MVP) USF004-009: Output Guardrails (Post-filtro y validación, tras la generación de respuesta)
> **Descripción**
Aplica Output Guardrails para validar la respuesta generada, tras la generación de respuesta
Detección de contenido erróneo, tóxico o sesgado.
Verificación de coherencia con fuentes recuperadas (incluso reintentar la generación si falla) (Medium).
Si falla (por toxicidad, invalidez, incoherencia), puede reintentar o responder con un mensaje genérico
Nota: por limitar la complejidad de la aplicación en una primera versión, las Output Guardrails NO tienen que implementarse.
> **Definición**
> Como administrador,
> Quiero que el sistema valide las respuestas de Meribot, detectando contenido erróneo, tóxico o sesgado y la coherencia con fuentes recuperadas
> Para asegurar que las respuestas de Meri-bot sean adecuadas, veraces, y alineadas con las políticas corporativas
**Criterios de Aceptación**
- ✅ Detección de contenido erróneo, tóxico o sesgado. Evalúa si la respuesta generada contiene errores factuales, sesgos ideológicos, lenguaje ofensivo, etc. Posibles acciones: Bloquear la respuesta/Reintentar la generación/Mostrar advertencia. Mensajes sugeridos:
- ❌ "La respuesta generada no cumple con nuestros estándares de calidad. Estamos generando una nueva versión..."
- ⚠️ "La información proporcionada puede contener sesgos o errores. Por favor, verifica con fuentes confiables."
- ✅ Verificación de coherencia con fuentes recuperadas (RAG). Compara la respuesta generada con los documentos recuperados. Si hay incoherencias, se puede reintentar la generación o alertar al usuario. Posibles acciones: Reintentar con nueva recuperación/Mostrar advertencia/Incluir citas o referencias. Mensajes sugeridos:
- 🔄 "La respuesta no coincide con las fuentes disponibles. Estamos intentando generar una versión más precisa..."
- ⚠️ "No se ha encontrado suficiente evidencia en las fuentes recuperadas para respaldar esta respuesta."
**Requisitos Técnicos**
(No MVP) Registrar las preguntas rechazadas, fallos o respuestas conflictivas con el fin de Logging y auditoría, para registrar cuándo y por qué se activan los guardrails.
(No MVP) Usa clasificadores de contenido (como Detoxify, Perspective API, etc.) para evaluar toxicidad y sesgo
(No MVP) USF004-010: Protección contra Ataques Adversariales
Detección de intentos de manipulación mediante prompt injection.
Rechazo de documentos contaminados o inputs sospechosos.
Escaneo automático de fragmentos recuperados para identificar instrucciones ocultas.
### (No MVP) USF004-011: Privacidad y Control de Acceso
> **Descripción**
Prevención de exposición de contenidos sensibles sin autorización.
Adaptación del nivel de acceso según el perfil del usuario.
## Feature 5: Services-Gestión de Almacenamiento vectorial con metadatos /services/storage
> **Descripción**
Capa de abstracción sobre la base de datos vectorial para facilitar su uso en la aplicación, permitiendo la gestión del almacenamiento y recuperación de datos vectoriales utilizando ChromaDB.
**Definición de la BBDD vectorial. Fragmentos. Metadatos.**
Fragmentos
Almacena fragmentos (chunks) de documentos como vectores semánticos en una base vectorial (ChromaDB)
Metadatos
Incluye metadatos en los fragmentos, como: url original de documento, dominio, fecha de creación/modificación, autor, tipo de documento, tamaño, número de página, origen de la fuente
Accesibilidad.
Accesible por LangChain vía retrievers
Permite búsquedas semánticas y filtradas.
Soporta trazabilidad y gestión por documento.
### (No MVP) USF005-001: Privilegios y seguridad de la BBDD
> **Definición**
> Como administrador,
> Quiero secretos en almacén seguro y mínimos privilegios,
> Para reducir riesgos y cumplir con normas de seguridad
### (MVP) USF005-002: Identificación de documentos
> **Definición**
> Como administrador,
> Quiero que todos los fragmentos de un documento compartan un identificador (ID único),
> Para poder identificar, actualizar o eliminar documentos fácilmente y facilitar su gestión
Criterios de aceptación
- ✅ Todos los fragmentos de un mismo documento deben compartir un identificador único.
- ✅ El identificador debe ser persistente y trazable.
- ✅ El sistema debe permitir modificar/eliminar todos los fragmentos de un documento por su ID.
### (MVP) USF005-003: Definición de fragmentos de documentos. Metadata
> **Definición**
> Como administrador,
> Quiero que cada fragmento tenga metadatos como dominio, fecha de scraping, fecha de creación, modificación, fuente, tamaño y tipo de documento
> Para para poder filtrar, recuperar, mantener y auditar la información
Criterios de aceptación
- ✅Cada fragmento debe incluir metadatos como:
Dominio temático (ejemplo RRHH, Formación)
Fecha y Hora de ingesta.
Fecha y Hora de creación/modificación del documento
Fuente original (URL y/o nombre del documento)
Tipo de documento
Identificador único del documento
### (No MVP) USF005-004: Re-Indexación
> **Definición**
> Como administrador,
> Quiero poder reindexar de distintas maneras (incremental/full y on-demand),
> Para mantener frescura de la BBDD
### (No MVP) USF005-005: Numeración de fragmentos de documentos
> **Definición**
> Como administrador,
> Quiero numerar los fragmentos secuencialmente
> Para que se muestren citas granulares en la respuesta, haciendo referencia a los números de los fragmentos y permitiendo mostrar los propios fragmentos como extractos

-------------------------------------------------------------------------------------------
# 🛠️ ADMINISTRACIÓN. Meri-cli. Gestión administrativa por línea de comandos -  /meri-cli
> **Objetivo**
Proporcionar una herramienta de línea de comandos (Meri-cli) que permita a administradores técnicos gestionar de forma segura y eficiente las operaciones de scraping, gestión de la BBDD vectorial (indexado, etc), y además realizar otras tareas administrativas y de auditoría, como configurar la información de los ficheros de configuración,sin necesidad de modificar el código fuente.
Funcionalidades Clave
Gestión de Crawling
Permite ejecutar procesos de scraping sobre fuentes internas (ej. SharePoint, Teams).
Admite configuración avanzada: profundidad de navegación, formatos de archivo, exclusiones, simulaciones (dry-run), ingesta manual por URL.
Subcomando crawl
Ejecuta sesiones de crawling sobre una URL inicial.
Opciones disponibles:
--url: URL de inicio (obligatoria).
--max-depth: profundidad de navegación.
--max-pages: límite de páginas.
--include / --exclude: patrones de inclusión/exclusión.
--formats: tipos de archivo (ej. PDF, DOCX, HTML).
--dry-run: simulación sin descarga.
--manual: ingesta directa de URLs específicas.
Gestión y Actualización Selectiva de documentos
Permite actualizar documentos modificados sin esperar al ciclo batch.
Toda actualización implica eliminación previa de fragmentos antiguos.
Subcomando db
Interactúa con la base vectorial para tareas de mantenimiento:
list: muestra documentos almacenados.
show: visualiza metadatos y fragmentos.
delete: elimina documentos por ID.
count: devuelve el número total de documentos y fragmentos.
Filtros por dominio, fecha, tipo, etc.
Seguridad y Control
Requiere permisos de administración para ejecutar comandos sensibles.
Todas las acciones quedan registradas para auditoría.
## Feature 6: Meri-cli-Configuración de fuentes, dominios, documentos críticos y formato de documentos
El administrador puede definir las fuentes de scraping, los dominios temáticos, los documentos críticos y los formatos de documentos, desde ficheros de configuración gestionados por línea de comandos.
### (MVP) USF006-001: Configuración de fuentes de scraping (inclusión/exclusión)
> **Definición**
> Como administrador,
> Quiero poder definir, en un [fichero de configuración de fuentes], las fuentes de scraping de donde se extraen los documentos (sitios web, paths, SharePoint/Teams
> Para mantener el sistema actualizado sin tocar el código.
 (MVP) Se recogerá de la web interna C&CA
 (No MVP) Se recogerá de la web interna C&CA, del sharepoint/Teams de RRHH, de la web interna de RRHH (Talent)
**Criterios de Aceptación**
- ✅ El administrador debe poder definir las fuentes desde un fichero de configuración.
### (No MVP) USF006-002: Configuración de documentos críticos a escrapear
> **Definición**
> Como administrador,
> Quiero poder definir en un [fichero de configuración de documentos críticos], las URLs de los documentos críticos a scrapear, (por ejemplo, cuando cambia una normativa urgente o hay una comunicación relevante para toda la organización)
> Para controlar la ingesta puntual y permitir al sistema reconocerlos y actualizarlos selectivamente sin esperar al siguiente ciclo batch del scraping. (Control de la ingesta puntual)
### (MVP) USF006-003: Configuración de dominios temáticos
> **Definición**
> Como administrador, quiero poder definir en un [fichero de configuración de dominios], los dominios temáticos para tener autonomía y adaptarlos a las decisiones estratégicas de C&CA y de RRHH.
 (MVP) Son los dominios Formación, Onboarding y Talent
 (MVP) USF006-004: Configuración de formatos de documentos a parsear
> **Definición**
> Como administrador,
> Quiero poder configurar en un [fichero de configuración de formatos de documentos], los formatos de documentos
> Para que el sistema pueda parsearlos y trocearlos en fragmentos
Nota: (MVP) Los formatos permitidos son: HTML/PDF/Word (docx/doc), Excel (xlsx)
### (MVP) USF006-004: Configuración de formatos de documentos a parsear
> **Definición**
> Como administrador, 
> Quiero poder configurar en un [fichero de configuración de formatos de documentos], los formatos de documentos
> Para que el sistema pueda parsearlos y trocearlos en fragmentos
Nota: (MVP) Los formatos permitidos son: HTML/PDF/Word (docx/doc), Excel (xlsx)
## Feature 7: Meri-cli-Configuración de crawler/scraping- Subcomando: crawl
> **‘Requisitos en RFP’**
Subcomando: crawl
El subcomando crawl permite lanzar procesos de crawling (exploración automática) sobre una URL inicial, recolectando documentos para su posterior procesamiento e ingesta en la base vectorial.
Sintaxis básica
meri-cli crawl --url <URL_INICIAL> [opciones]
Opciones y parámetros (los que están marcados como “ Opcional” se podrían descartar para el MVP. Que si tendra que estar implementados son los valores por defecto)
■ --url <URL_INICIAL> (Obligatorio) URL de inicio de la sesión de crawling. Debe pertenecer al dominio permitido; el crawler nunca saldrá de este dominio base.
■ --max-depth <N> (Opcional) Profundidad máxima de navegación de enlaces a partir de la URL inicial. Por defecto: 2.
■ --max-pages <N> (Opcional) Número máximo de páginas a explorar en la sesión. Por defecto: sin límite.
■ --include <regex> (Opcional) Solo incluir URLs que cumplan el patrón indicado (expresión regular).
■ --exclude <regex> (Opcional) Excluir URLs que cumplan el patrón (ejemplo: rutas de logout, privadas, etc.).
■ --formats <ext1,ext2,...> (Opcional) Lista de formatos de archivo a recolectar (por ejemplo: html,pdf,docx). Por defecto: todos los soportados.
■ --output <directorio> (Opcional) Carpeta destino para guardar los documentos descargados o procesados.
■ --update-only (Opcional) Solo actualiza documentos nuevos o modificados desde la última sesión.
■ --dry-run (Opcional) Simula el crawling y reporta los documentos/URLs que serían procesados, sin descargar ni guardar nada.
■ --manual (Opcional) Permite indicar manualmente una lista de URLs a procesar en vez de hacer crawling iterativo.
### (MVP) USF007-001: Scraping bajo demanda y Actualización de documentos críticos
> **Definición**
> Como Administrador,
> Quiero que lanzar el Crawler bajo demanda,
> Para forzar una actualización inmediata cuando se publiquen documentos críticos y que la información urgente esté disponible en tiempo real.
**Criterios de Aceptación**
- ✅ Disparador manual desde Meri-Cli
- ✅Comando CLI para lanzar el crawler bajo demanda.
- ✅Se puede ejecutar el scraping de forma manual y con filtros por URL, profundidad, formatos, etc. para documentos críticos
**Requisitos Técnicos**
Orquestación y Programación -- Ejecución manual desde Meri-Cli. -- Reintentos con backoff exponencial para fallos temporales.
Meri-Cli ofrece ayuda contextual (meri crawler --help) y ejemplos de comandos.
Comando run con opciones (—full, —since, —url, —dry-run).
Validaciones: parámetros compatibles; cancelar si ya hay job en curso (o encolar).
### (MVP) USF007-002: Scraping en modo simulación
> **Definición**
> Como administrador,
> Quiero poder ejecutar scraping en modo simulación (dry-run),
> Para validar qué documentos se procesarían.
**Criterios de Aceptación**
- ✅ Probar con un comando de dry-run para validar alcance.
### (MVP) USF007-003: Scraping Planificado
> **Definición**
> Como administrador,
> Quiero que el scraper pueda recoger documentos de manera periódica, programar una ejecución semanal,
> Para mantener el conocimiento actualizado automáticamente
**Criterios de Aceptación**
- ✅ Se puede ejecutar el scraping automáticamente según una [frecuencia] definida y con filtros por URL, profundidad, formatos, etc. Siendo [frecuencia]== semanal
- ✅ Se puede configurar la [frecuencia] de lanzamiento
- ✅ Comando para registrar el cron/scheduler interno.
- ✅Validaciones: expresión cron válida; confirmación de próxima ejecución.
**Requisitos Técnicos**
cron job para Scraper
Orquestación y Programación -- Ejecución semanal automática.
Usar un scheduler (ej: APScheduler) o integración con cron.
### (No MVP) USF007-004: Monitoreo en tiempo real
> **Definición**
> Como administrador,
> Quiero revisar los errores con mensajes estándar,
> Para diagnosticar y corregir problemas rápidamente.
**Criterios de Aceptación**
- ✅Comando status muestra progreso: crawled, en cola, throughput, ETA.
- ✅Manejo de errores parciales con contadores y últimos mensajes.
- ✅Comando report muestra resumen por estado: nuevos, actualizados, sin cambios, errores.
### (No MVP) USF007-005: Reporte y resultados
> **Definición**
> Como administrador,
> Quiero ver un resumen de resultados (nuevos, actualizados, no cambiados, errores),
> Para evaluar el éxito del proceso
**Criterios de Aceptación**
- ✅ Se generan reportes claros de resultados
- ✅Se puede exportar a tabla y JSON para consumo por otras herramientas.
### (MVP) USF007-006: Gestión de fallos
> **Definición**
**Criterios de Aceptación**
- ✅ Comando retry-failures para reintentar solo los ítems fallidos.
- ✅ Validaciones: ventana temporal y número máximo de reintentos.
- ✅ Manejo robusto de errores. Continuar ante fallos parciales, registrar y reportar todos los errores. Mensajes estándar para “no answer found” y “acceso restringido”.
## Feature 8: Meri-cli-Gestión de la base vectorial-Subcomando: db
> **Objetivo**
Desde meri-cli se pueden listar, eliminar o consultar documentos y fragmentos almacenados en la base vectorial.
**‘Requisitos en RFP’**
Subcomando: db
El subcomando db permite interactuar directamente con la base de datos vectorial de documentos ya ingeridos. Es útil para tareas de administración, control de versiones, limpieza y auditoría.
Sintaxis básica
meri-cli db [opción] [parámetros]
Opciones disponibles
■ list Lista todos los documentos actualmente almacenados, mostrando información relevante (ID, nombre, dominio, fecha de ingreso, versión, etc.).
Opciones para list:
○ --filter <campo>:<valor> Filtra la lista de documentos por dominio, fecha, tipo, etc.
○ --show-chunks Muestra también el número de fragmentos (chunks) asociados a cada documento.
■ delete --id <DOCUMENT_ID> Elimina de la base vectorial todos los fragmentos asociados a un documento específico.
■ show --id <DOCUMENT_ID> Muestra información detallada y metadatos del documento y/o los fragmentos asociados.
■ count Devuelve el número total de documentos y/o fragmentos almacenados.
### (MVP) USF008-001: Visualización del número de fragmentos por documento
> **Definición**
> Como administrador,
> Quiero poder ver el número de fragmentos por documento,
> Para entender el volumen de información
**Criterios de Aceptación**
- ✅ El sistema debe permitir consultar el número de fragmentos asociados a un documento
### (MVP) USF008-002: Consulta, y eliminación de documentos
> **Definición**
> Como administrador,
> Quiero listar, consultar documentos y eliminar todos los fragmentos de un documento de la base vectorial
> Para mantener la calidad y coherencia de los datos
**Criterios de Aceptación**
- ✅ El sistema debe permitir consultar y eliminar todos los fragmentos asociados a un documento por su ID.
- ✅ La operación debe confirmarse antes de ejecutarse
### (No MVP) USF008-003: Reindexaciones
> **Definición**
> Como administrador,
> Quiero poder programar reindexaciones (incremental/full y on-demand),
> Para mantener frescura
### (No MVP) USF008-004: Realizar pruebas y validaciones previas
> **Definición**
> Como administrador,
> Quiero poder realizar dry-runs y validaciones previas,
> Para evitar dañar el índice de los fragmentos de los documentos
Nota: Un "dry run" es una prueba o ensayo de un proceso, evento o actividad, realizado antes de la ejecución real, con el objetivo de identificar posibles problemas y mejorar la preparación. Se traduce al español como simulacro, ensayo, o prueba.
## Feature 9: Meri-cli-Configuración de system prompt
> **Objetivo**
El administrador puede configurar el system prompt por línea de comandos
### (No MVP) USF009-001: Configuración del system prompt
> **Definición**
**Criterios de Aceptación**
- ✅ El administrador debe poder editar el system prompt desde un fichero o parámetro.
- ✅ Los cambios deben reflejarse en las respuestas generadas.
## (No MVP) Feature 10: Meri-cli-Loggins. Trazabilidad y Auditoría
> **Objetivo**
Establecer un sistema robusto de trazabilidad que permita registrar, supervisar y analizar todas las operaciones técnicas y administrativas del sistema Meri-Bot, garantizando transparencia, control y capacidad de diagnóstico ante incidencias o mejoras.
Todos los procesos (scraping, ingesta, errores) quedan registrados en logs para facilitar el debugging, la auditoría y la trazabilidad.
> **Definición**
> Como administrador,
> Quiero que todas las interacciones y procesos relevantes queden registrados en logs
> Para facilitar el diagnóstico de errores y la mejora continua.
**Funcionalidades Clave** 
- Registro
Operaciones registradas incluyen:
Ingesta de documentos (manual o automática).
Eliminación de documentos o fragmentos.
Actualizaciones selectivas o por lotes.
Simulaciones (dry-run) y operaciones de mantenimiento.
Cada entrada de registro debe contener:
Fecha y hora.
Usuario o proceso que ejecutó la acción.
Tipo de operación.
Identificador del documento afectado.
Resultado (éxito, error, advertencia).
- Auditoría de Interacciones Conversacionales
Se registrarán las consultas del usuario, dónde los datos registrados deberían ser:
Texto de la consulta.
Fragmentos documentales utilizados.
Fuente de los documentos.
Tiempo de respuesta.
Registro de inputs rechazados, respuestas conflictivas y fallos de validación. Alertas o validaciones aplicadas (ej. incoherencias, toxicidad).
- Mejora Continua
Posibilidad de incorporar feedback humano para refinar las reglas.
Revisión periódica del system prompt y de los mecanismos de validación.
- Trazabilidad de Documentos
Cada documento debe tener un identificador único que permita:
Rastrear su origen (fuente, URL, dominio).
Verificar su fecha de ingesta y versión.
Auditar los fragmentos generados y su uso en respuestas.
Detectar duplicidades o inconsistencias.
- Control de Acceso a Registros
Solo usuarios con permisos administrativos pueden acceder a los registros completos.
Se debe implementar autenticación básica en meri-cli para proteger el acceso.
Los registros deben estar protegidos contra modificaciones no autorizadas.
- Exportación y Visualización de los datos.
Posibilidad de exportar los registros en formatos estándar (CSV, JSON).
Visualización resumida mediante comandos como:
meri-cli db list --show-chunks
meri-cli db show --id <DOCUMENT_ID>
meri-cli db count
- Alertas y Seguimiento
El sistema puede generar alertas ante:
Fallos en la ingesta o actualización.
Documentos duplicados o contaminados.
Consultas sin respuesta o fuera de contexto.
(Fuera de Scope) Respuestas incoherentes (si se activa validación de outputs).
- Gobernanza y Buenas Prácticas
Todas las acciones deben quedar registradas para trazabilidad.
Se recomienda revisión periódica de los registros para detectar patrones de uso, errores frecuentes o necesidades de mejora.
(Fuera de Scope) El sistema debe permitir incorporar feedback humano para refinar reglas y validaciones.
### (No MVP) USF010-001: Registro de operaciones técnicas
> **Definición**
> Como auditor,
> Quiero que se registren todas las operaciones técnicas realizadas y procesos
> Para garantizar trazabilidad y control.
### (No MVP) USF010-002: Registro de consultas y respuestas
> **Definición**
> Como auditor,
> Quiero que se registren todas las preguntas y respuestas, así como qué documentos fueron usados en cada respuesta,
> Para garantizar la veracidad de las respuestas.
**Criterios de Aceptación**
- ✅ Cada interacción debe quedar registrada en un log con timestamp.
- ✅ El log debe incluir la pregunta y la respuesta, así como los metadatos relevantes (como es el dominio, la URL del documento usado en la respuesta, etc)
- ✅Se deben registrar logs de errores, eventos críticos y fallos de generación de respuesta.
### (No MVP) USF010-003: Visualización en log: Procesos backend
> **Definición**
> Como administrador,
> Quiero que todos los procesos queden registrados en logs anonimizados,
> Para poder detectar errores y mejorar el sistema.
### (No MVP)USF010-004: Visualización en log: Métricas
> **Definición**
> Como administrador,
> Quiero ver métricas básicas (latencia, tasa de aciertos, documentos indexados, throughput, errores),
> Para operar el servicio y monitorear el rendimiento
### (No MVP) USF010-005: Visualización en log: Alertas
> **Definición**
> Como administrador,
> Quiero alertas ante errores de scraping/ingesta,
> Para reaccionar rápido
(Fuera de Scope) Feature 11: Meri-cli-Control de acceso a dominios
Es necesario controlar qué usuarios pueden acceder a qué dominios de información para proteger contenidos sensibles
(Fuera de scope) porque en la actualidad la página web C&CA que aloja Meri-bot no autentica usuarios
