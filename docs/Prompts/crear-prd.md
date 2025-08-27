# Regla: Generación de un Documento de Requisitos del Producto (PRD)

## Objetivo

Guiar a un asistente de IA en la creación de un Documento de Requisitos del Producto (PRD) detallado en formato Markdown, basado en una solicitud inicial del usuario. El PRD debe ser claro, práctico y adecuado para que un desarrollador junior lo comprenda e implemente.

## Proceso

1. **Recibir la solicitud inicial:** El módulo CORE de MeriBot es el núcleo de lógica conversacional y procesamiento de lenguaje natural del asistente empresarial para la intranet de C&CA. Su objetivo es gestionar el flujo de conversación, integrar servicios de IA y ofrecer respuestas útiles y seguras a empleados y administradores.
2. **Hacer preguntas aclaratorias:** Antes de escribir el PRD, la IA *debe* hacer preguntas aclaratorias para obtener suficientes detalles. El objetivo es comprender el "qué" y el "por qué" de la característica, no necesariamente el "cómo" (que el desarrollador descubrirá). Asegúrese de proporcionar opciones en listas de letras/números para que pueda responder fácilmente con mis selecciones.
3. **Generar el PRD:** Con base en la solicitud inicial y las respuestas del usuario a las preguntas aclaratorias, genere un PRD utilizando la estructura que se describe a continuación. 4. **Guardar PRD:** Guarde el documento generado como `prd-core.md` dentro del directorio `core/tasks`.

## Preguntas aclaratorias (ejemplos)

La IA debe adaptar sus preguntas según la solicitud, pero aquí hay algunas áreas comunes para explorar:

* **Problema/Objetivo:** Permitir a empleados y administradores acceder de forma sencilla, segura y centralizada a información interna, políticas, documentación y servicios automatizados, optimizando la experiencia de consulta y reduciendo la carga de soporte.
* **Usuario objetivo:** 
* Empleados de C\&CA que requieren información o asistencia sobre procesos internos.
* Administradores encargados de gestionar el conocimiento y la base de datos de respuestas.
* **Funcionalidad principal:** * Procesar mensajes en lenguaje natural y mantener el contexto conversacional.
* Consultar políticas y documentación interna.
* Acceso seguro a datos y respuestas.
* Integración con plugins para extender funcionalidades (FAQ, búsqueda documental, scraping, etc.).
* Gestión de conversaciones y caché de respuestas frecuentes
* **Historias de usuario y criterios de aceptacion** ## US-01: Procesamiento de Mensajes de Usuario

**Como** usuario del chatbot  
**Quiero** enviar preguntas en lenguaje natural  
**Para** recibir respuestas claras y relevantes sobre la información interna de la empresa.

**Criterios de aceptación:**
- El sistema recibe [una estructura de datos/objeto] con el mensaje del usuario.
- El sistema procesa el mensaje y devuelve una respuesta generada por IA.
- Si no hay información relevante, el sistema informa al usuario de forma clara y no inventa respuestas.
- La respuesta puede contener enlaces a los documentos fuente utilizados.
- La respuesta debe generarse en el idioma de la consulta del usuario, aunque los documentos estén en otro idioma. 
- La respuesta debe mostrarse en modo streaming, es decir, el usuario ve la respuesta mientras se genera.

---

## US-02: Gestión de Conversaciones

**Como** usuario  
**Quiero** que el sistema mantenga el contexto de la conversación  
**Para** poder realizar preguntas de seguimiento y obtener respuestas coherentes.

**Criterios de aceptación:**
- Cada conversación tiene un identificador único.
- El contexto se mantiene durante la sesión activa.
- Al cerrar el panel de conversación, el historial se pierde (MVP).
- No existe un máximo de preguntas/respuestas por conversación en el panel.

---

## US-03: Configuración del Motor de Chat

**Como** administrador o desarrollador  
**Quiero** poder configurar parámetros clave del motor de chat (modelo, temperatura, tokens, caché)  
**Para** adaptar el comportamiento del chatbot a las necesidades del negocio.

**Criterios de aceptación:**
- Los parámetros se pueden definir mediante variables de entorno o archivo de configuración.
- El sistema lee y aplica la configuración al inicializarse.
- El modelo de IA utilizado debe poder ser cambiado fácilmente (por ejemplo, GPT-4.1, nano, etc.).
- El system prompt debe ser configurable para establecer el rol, estilo y límites del comportamiento de la IA.

---

## US-04: Sistema de Plugins

**Como** desarrollador  
**Quiero** poder extender la funcionalidad del chatbot mediante plugins  
**Para** añadir nuevas capacidades sin modificar el núcleo del sistema.

**Criterios de aceptación:**
- Existe una clase base para plugins.
- Los plugins pueden procesar mensajes y devolver respuestas.
- Los plugins se pueden registrar y activar/desactivar fácilmente.
- Los plugins pueden acceder al contexto de la conversación y a los metadatos de la consulta.

---

## US-05: Integración con Bases de Datos Vectoriales

**Como** usuario  
**Quiero** que el chatbot recupere información relevante usando búsquedas semánticas  
**Para** obtener respuestas precisas basadas en la documentación interna.

**Criterios de aceptación:**
- El sistema utiliza una base vectorial (ChromaDB) para buscar fragmentos relevantes.
- La respuesta cita las fuentes utilizadas.
- Los fragmentos almacenados deben incluir metadatos como dominio, fecha, fuente, etc.
- El sistema debe permitir filtrar por dominio y otros metadatos en la consulta.

---

## US-06: Gestión de Caché de Respuestas

**Como** usuario frecuente  
**Quiero** que las respuestas a preguntas comunes se sirvan rápidamente  
**Para** mejorar la experiencia y reducir la latencia.

**Criterios de aceptación:**
- El sistema almacena en caché las respuestas frecuentes.
- El tiempo de vida de la caché es configurable.
- El sistema debe invalidar la caché cuando se actualicen los documentos fuente relevantes.

---

## US-07: Logging y Auditoría

**Como** administrador  
**Quiero** que todas las interacciones y procesos relevantes queden registrados en logs  
**Para** facilitar el diagnóstico de errores y la mejora continua.

**Criterios de aceptación:**
- Los errores y eventos críticos quedan reflejados en los logs.
- El sistema debe registrar también los inputs rechazados por guardrails y los fallos de generación de respuesta.
- Los logs deben permitir auditoría de procesos técnicos (no de usuarios).

---

## US-08: Pruebas Unitarias y Cobertura

**Como** desarrollador  
**Quiero** contar con pruebas unitarias y de cobertura  
**Para** asegurar la calidad y robustez del módulo core.

**Criterios de aceptación:**
- Existen tests unitarios para las funciones principales.
- Se puede ejecutar la batería de tests y obtener un informe de cobertura.
- Las pruebas deben cubrir casos de error, edge cases y validaciones de guardrails.
---

## US-09: Accesibilidad y Seguridad

**Como** usuario  
**Quiero** que el sistema sea accesible y seguro  
**Para** garantizar el cumplimiento de estándares y la protección de la información.

**Criterios de aceptación:**
- El sistema valida y sanitiza las entradas del usuario.
- Se cumplen las recomendaciones de seguridad y accesibilidad del proyecto.
- El sistema debe implementar guardrails para evitar respuestas inadecuadas o peligrosas.
- No se exponen datos personales ni información sensible en las respuestas ni en los logs.

---

## US-10: Filtros por Dominio (Plugins y Core)

**Como** usuario  
**Quiero** poder filtrar mis consultas por dominio o categoría  
**Para** obtener respuestas más relevantes y acotadas.

**Criterios de aceptación:**
- La consulta puede incluir uno o varios dominios por los cuales filtrar.
- El sistema limita la búsqueda a los dominios seleccionados.
- La lista de dominios disponibles se obtiene dinámicamente desde la configuración o la base de datos vectorial.
- Si un dominio deja de existir, no debe aparecer como opción de filtro.

---

## US-11: Generación de respuestas. System prompt

**Como** desarrollador  
**Quiero** configurar el system prompt  
**Para** definir el estilo y límites de las respuestas de la IA y garantizar que las respuestas sean rápidas, claras, útiles, que se basen únicamente en el contexto proporcionado y en el idioma de la pregunta del usuario.

**Criterios de aceptación:**

- El system prompt es persistente y no puede ser alterado por el usuario.
- El prompt enviado al modelo debe incluir el system prompt y el user prompt.
- El user prompt debe incluir los dominios seleccionados por el usuario, la preferencia de idioma, y la propia pregunta.
- El system prompt debe incluir:
  - Tiempo de respuesta: Las respuestas deben generarse en segundos, gracias a la búsqueda semántica en la base vectorial.
  - La respuesta se entrega en modo streaming con fuente y filtros aplicados. Se debe mostrar la respuesta mientras se genera, sin esperar a que esté completa.
  - Preferencia de idioma en toda la conversación. La respuesta debe realizarse en el idioma de la primera consulta.
  - Si la pregunta tiene contenido tóxico o inadecuado, entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa]. Ejemplo de mensaje:
       “Tu pregunta está fuera del ámbito de la intranet.”
  - Si Meri-bot no puede generar una respuesta por error del sistema o porque no encuentra la información o no encuentra información suficiente, entonces como respuesta debe mostrarse un [mensaje de error o sugerencia alternativa] que invite al usuario a reformular la pregunta. Ejemplo de mensaje:
       “No encontré información relevante, ¿quieres reformular tu pregunta?”
  - Si Meri-bot puede generar una respuesta, la respuesta puede ser un resumen, pero no puede inventar, para que el usuario confíe en que la información proviene de fuentes reales.
  - Las respuestas deben estar basadas únicamente en fragmentos extraídos relevantes.
  - La respuesta debe incluir los enlaces (URL) de los documentos originales utilizados.

---


### Alcance/Límites

* No realiza acciones fuera del ámbito de consulta, gestión de conocimiento y automatización de respuestas.
* No accede ni modifica datos personales sensibles sin autorización.
* No reemplaza sistemas de gestión documental externos, solo los consulta.

### Requisitos de datos

* Acceso a bases de datos de políticas, documentación y FAQs.
* Almacenamiento temporal de contexto conversacional.
* Logs de interacción para auditoría y mejora continua.

### Diseño/IU

* No aplica directamente (el CORE es backend), pero debe exponer interfaces claras para integración con el widget web y panel de administración.
* Seguir las directrices de API REST y buenas prácticas de integración.

### Casos extremos

* Consultas ambiguas o fuera de alcance (el sistema debe responder de forma informativa y no comprometer datos).
* Fallos en servicios externos (debe manejar errores y notificar al usuario de forma clara).
* Solicitudes simultáneas de múltiples usuarios (debe mantener el contexto aislado por conversación).

## Estructura del PRD

El PRD generado debe incluir las siguientes secciones:

1. **Introducción/Resumen:** Describa brevemente la función y el problema que resuelve. Indique el objetivo.

2. **Objetivos:** Enumere los objetivos específicos y medibles de esta función.

3. **Historias de usuario:** Detalle las narrativas de los usuarios que describen el uso y los beneficios de la función.

4. **Requisitos funcionales:** Enumere las funcionalidades específicas que debe tener la función. Use un lenguaje claro y conciso (p. ej., "El sistema debe permitir a los usuarios subir una foto de perfil"). Enumere estos requisitos.
5. **Objetivos no especificados (fuera del alcance):** Indique claramente qué *no* incluirá esta función para gestionar el alcance.
6. **Consideraciones de diseño (opcional):** Enlace a maquetas, describa los requisitos de UI/UX o mencione los componentes/estilos relevantes, si corresponde.
7. **Consideraciones técnicas (opcional):** Mencione cualquier restricción técnica, dependencia o sugerencia conocida (p. ej., "Debería integrarse con el módulo de autenticación existente").
8. **Métricas de éxito:** ¿Cómo se medirá el éxito de esta función? (p. ej., "Aumentar la participación del usuario en un 10%", "Reducir los tickets de soporte relacionados con X").
9. **Preguntas abiertas:** Enumere cualquier pregunta pendiente o área que requiera mayor aclaración.

## Público objetivo

Suponga que el lector principal del PRD es un **desarrollador júnior**. Por lo tanto, los requisitos deben ser explícitos, inequívocos y evitar la jerga en la medida de lo posible. Proporcione suficientes detalles para que comprendan el propósito y la lógica central de la función.

## Salida

* **Formato:** Markdown (`.md`)
* **Ubicación:** `/tasks/`
* **Nombre de archivo:** `prd-[feature-name].md`

## Instrucciones finales

1. NO comience a implementar el PRD
2. Asegúrese de hacer preguntas aclaratorias al usuario
3. Tome las respuestas del usuario a las preguntas aclaratorias y mejore el PRD
Enviar comentarios
