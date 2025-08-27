# PRD – Módulo CORE de MeriBot

## 1. Introducción/Resumen

El módulo CORE de MeriBot es el núcleo de lógica conversacional y procesamiento de lenguaje natural del asistente empresarial para la intranet de C&CA. Su objetivo es gestionar el flujo de conversación, integrar servicios de IA y ofrecer respuestas útiles y seguras a empleados y administradores, centralizando el acceso a información interna, políticas, documentación y servicios automatizados. El CORE actúa como backend, exponiendo interfaces para integración con el widget web y el panel de administración.

## 2. Objetivos

- Permitir a empleados y administradores acceder de forma sencilla, segura y centralizada a información interna y servicios automatizados.
- Procesar mensajes en lenguaje natural y mantener el contexto conversacional.
- Integrar plugins para extender funcionalidades (FAQ, búsqueda documental, scraping, etc.).
- Consultar políticas y documentación interna mediante búsquedas semánticas.
- Garantizar la seguridad, accesibilidad y cumplimiento de estándares.
- Facilitar la configuración y personalización del motor de chat.
- Proveer mecanismos de logging, auditoría y pruebas unitarias.

## 3. Historias de usuario

- **US-01:** Como usuario del chatbot, quiero enviar preguntas en lenguaje natural para recibir respuestas claras y relevantes sobre la información interna de la empresa.
- **US-02:** Como usuario, quiero que el sistema mantenga el contexto de la conversación para poder realizar preguntas de seguimiento y obtener respuestas coherentes.
- **US-03:** Como administrador o desarrollador, quiero poder configurar parámetros clave del motor de chat para adaptar el comportamiento del chatbot a las necesidades del negocio.
- **US-04:** Como desarrollador, quiero poder extender la funcionalidad del chatbot mediante plugins para añadir nuevas capacidades sin modificar el núcleo del sistema.
- **US-05:** Como usuario, quiero que el chatbot recupere información relevante usando búsquedas semánticas para obtener respuestas precisas basadas en la documentación interna.
- **US-06:** Como usuario frecuente, quiero que las respuestas a preguntas comunes se sirvan rápidamente para mejorar la experiencia y reducir la latencia.
- **US-07:** Como administrador, quiero que todas las interacciones y procesos relevantes queden registrados en logs para facilitar el diagnóstico de errores y la mejora continua.
- **US-08:** Como desarrollador, quiero contar con pruebas unitarias y de cobertura para asegurar la calidad y robustez del módulo core.
- **US-09:** Como usuario, quiero que el sistema sea accesible y seguro para garantizar el cumplimiento de estándares y la protección de la información.
- **US-10:** Como usuario, quiero poder filtrar mis consultas por dominio o categoría para obtener respuestas más relevantes y acotadas.
- **US-11:** Como desarrollador, quiero configurar el system prompt para definir el estilo y límites de las respuestas de la IA y garantizar que las respuestas sean rápidas, claras, útiles y basadas únicamente en el contexto proporcionado.

## 4. Requisitos funcionales

- El sistema debe recibir mensajes en lenguaje natural y devolver respuestas generadas por IA.
- Debe mantener el contexto de la conversación durante la sesión activa.
- Debe permitir la configuración de parámetros clave (modelo, temperatura, tokens, caché) mediante variables de entorno o archivo de configuración.
- Debe contar con un sistema de plugins extensible y desacoplado.
- Debe integrar una base de datos vectorial (ChromaDB) para búsquedas semánticas y citar fuentes utilizadas.
- Debe gestionar una caché de respuestas frecuentes, con tiempo de vida configurable e invalidación automática.
- Debe registrar logs de errores, eventos críticos y fallos de generación de respuesta.
- Debe contar con pruebas unitarias y de cobertura para las funciones principales.
- Debe validar y sanitizar todas las entradas del usuario.
- Debe implementar guardrails para evitar respuestas inadecuadas o peligrosas.
- Debe permitir filtrar consultas por dominio o categoría, obteniendo la lista de dominios dinámicamente.
- El system prompt debe ser persistente y configurable, y las respuestas deben generarse en modo streaming, en el idioma de la consulta y citando las fuentes originales.

## 5. Objetivos no especificados (fuera del alcance)

- No realiza acciones fuera del ámbito de consulta, gestión de conocimiento y automatización de respuestas.
- No accede ni modifica datos personales sensibles sin autorización.
- No reemplaza sistemas de gestión documental externos, solo los consulta.
- No incluye interfaz de usuario propia (solo backend).
- No almacena datos personales ni información sensible en respuestas ni logs.

## 6. Consideraciones de diseño

- El CORE debe exponer interfaces REST claras para integración con el widget web y el panel de administración.
- Seguir las directrices de API REST y buenas prácticas de integración.
- No aplica diseño de UI/UX directamente, pero debe facilitar la integración frontend.

## 7. Consideraciones técnicas

- El sistema debe ser desacoplado y extensible mediante plugins.
- Debe integrarse con ChromaDB como base vectorial.
- Debe ser fácilmente integrable con el widget web existente.
- Debe permitir la configuración mediante variables de entorno o archivos.
- Debe manejar errores de servicios externos y notificar al usuario de forma clara.

## 8. Métricas de éxito

- Tiempo medio de respuesta inferior a X segundos.
- Porcentaje de respuestas satisfactorias (medido por feedback o métricas internas).
- Reducción de tickets de soporte relacionados con consultas internas.
- Cobertura de pruebas superior al 80%.
- Ausencia de incidentes de seguridad o filtrado de datos sensibles.

## 9. Preguntas abiertas

- ¿Qué modelos de IA serán soportados inicialmente y cuáles deben estar disponibles para configuración?
- ¿Cuál es el tiempo de vida recomendado para la caché de respuestas?
- ¿Qué criterios se usarán para determinar si una respuesta es “satisfactoria”?
- ¿Qué dominios o categorías deben estar disponibles por defecto para el filtrado?
- ¿Qué nivel de logging es necesario para auditoría sin comprometer la privacidad?
