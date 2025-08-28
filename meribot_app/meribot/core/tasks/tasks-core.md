# Tareas para el Módulo CORE de MeriBot (v2)

## Archivos relevantes

- `meribot_app/meribot/core/__init__.py` – Inicialización y configuración del módulo CORE.
- `meribot_app/meribot/core/conversation.py` – Lógica de gestión de conversaciones y contexto.
- `meribot_app/meribot/core/plugin_manager.py` – Gestión y registro de plugins.
- `meribot_app/meribot/core/vector_search.py` – Integración y consultas a la base vectorial (ChromaDB).
- `meribot_app/meribot/core/cache.py` – Gestión de caché de respuestas.
- `meribot_app/meribot/core/logging.py` – Logging y auditoría de eventos.
- `meribot_app/meribot/core/config.py` – Configuración del motor de chat y parámetros clave.
- `meribot_app/meribot/core/guardrails.py` – Validación, sanitización y control de seguridad.
- `meribot_app/meribot/core/llm_engine.py` – Motor de generación de respuestas con LLM y Langchain.
- `meribot_app/meribot/core/chatengine.py` – Coordinador principal del CORE e interfaz programática para el módulo API.
- `meribot_app/meribot/core/tests/` – Pruebas unitarias para cada uno de los módulos anteriores.

### Notas

- Las pruebas unitarias deben ubicarse en `meribot_app/meribot/core/tests/` siguiendo la convención del proyecto.
- Los nombres de los archivos pueden ajustarse según la estructura final y convenciones internas.
- El ChatEngine debe proporcionar una interfaz asíncrona limpia para la integración con el módulo API.

## Tareas

- [x] 1.0 Implementar la gestión de conversaciones y contexto.
  - [x] 1.1 Definir la estructura de datos para el contexto conversacional.
  - [x] 1.2 Implementar la creación y cierre de sesiones de conversación.
  - [x] 1.3 Mantener el historial de mensajes durante la sesión activa.
  - [x] 1.4 Eliminar el historial al cerrar el panel de conversación.
  - [x] 1.5 Añadir identificadores únicos para cada conversación.
  - [x] 1.6 Realizar pruebas unitarias del conjunto de la tarea.
- [x] 2.0 Desarrollar el sistema de plugins y su integración con el CORE.
  - [x] 2.1 Diseñar la clase base para plugins.
  - [x] 2.2 Implementar el registro y activación/desactivación de plugins.
  - [x] 2.3 Permitir que los plugins accedan al contexto y metadatos de la consulta.
  - [x] 2.4 Documentar el proceso de creación de nuevos plugins.
  - [x] 2.5 Realizar pruebas unitarias del conjunto de la tarea.
- [x] 3.0 Integrar la base vectorial para búsquedas semánticas y citación de fuentes.
  - [x] 3.1 Implementar la conexión con ChromaDB.
  - [x] 3.2 Desarrollar la función de búsqueda semántica de fragmentos relevantes.
  - [x] 3.3 Incluir metadatos (dominio, fecha, fuente) en los fragmentos almacenados.
  - [x] 3.4 Permitir filtrar resultados por dominio y otros metadatos.
  - [x] 3.5 Citar las fuentes utilizadas en las respuestas.
  - [x] 3.6 Realizar pruebas unitarias del conjunto de la tarea.
- [x] 4.0 Implementar la gestión de caché de respuestas frecuentes.
  - [x] 4.1 Diseñar la estructura de la caché y su integración con el CORE.
  - [x] 4.2 Configurar el tiempo de vida de la caché.
  - [x] 4.3 Implementar la invalidación automática al actualizar documentos fuente.
  - [x] 4.4 Optimizar la recuperación de respuestas frecuentes.
  - [x] 4.5 Realizar pruebas unitarias del conjunto de la tarea.
 [x] 5.0 Configurar y exponer parámetros clave del motor de chat.
  - [x] 5.1 Permitir la configuración mediante variables de entorno o archivo.
  - [x] 5.2 Habilitar la selección dinámica del modelo de IA.
  - [x] 5.3 Configurar el system prompt y parámetros como temperatura y tokens.
  - [x] 5.4 Documentar las opciones de configuración disponibles.
  - [x] 5.5 Realizar pruebas unitarias del conjunto de la tarea.
- [x] 6.0 Implementar logging y auditoría de eventos y errores.
  - [x] 6.1 Registrar errores y eventos críticos.
  - [x] 6.2 Registrar inputs rechazados por guardrails y fallos de generación.
  - [x] 6.3 Garantizar que los logs permitan auditoría técnica sin exponer datos sensibles.
  - [x] 6.4 Configurar niveles de logging y rotación de logs.
  - [x] 6.5 Realizar pruebas unitarias del conjunto de la tarea.
- [x] 7.0 Desarrollar validaciones, sanitización y guardrails de seguridad.
  - [x] 7.1 Implementar validación y sanitización de entradas del usuario.
  - [x] 7.2 Añadir guardrails para evitar respuestas inadecuadas o peligrosas.
  - [x] 7.3 Garantizar cumplimiento de estándares de seguridad y accesibilidad.
  - [x] 7.4 Probar casos extremos y edge cases de seguridad.
  - [x] 7.5 Realizar pruebas unitarias del conjunto de la tarea.
- [x] 8.0 Implementar el motor de generación de respuestas con LLM.
  - [x] 8.1 Integrar Langchain para la comunicación con modelos de IA.
  - [x] 8.2 Implementar la lógica de generación de respuestas en modo streaming.
  - [x] 8.3 Configurar el system prompt persistente y parámetros del modelo.
  - [x] 8.4 Gestionar el contexto conversacional en las llamadas al LLM.
  - [x] 8.5 Implementar la citación automática de fuentes en las respuestas.
  - [x] 8.6 Manejar errores de conectividad y fallos del modelo de IA.
  - [x] 8.7 Realizar pruebas unitarias del conjunto de la tarea.
- [ ] 9.0 Desarrollar el ChatEngine como interfaz de coordinación del CORE.
  - [ ] 9.1 Diseñar la clase ChatEngine como punto de entrada principal del CORE.
  - [ ] 9.2 Coordinar la interacción entre plugins, vector search, caché y LLM.
  - [ ] 9.3 Implementar la lógica de flujo conversacional completa.
  - [ ] 9.4 Gestionar el filtrado por dominio y metadatos de consultas.
  - [ ] 9.5 Proporcionar una interfaz programática asíncrona limpia para el módulo API.
  - [ ] 9.6 Realizar pruebas unitarias del conjunto de la tarea.
- [ ] 10.0 Crear pruebas unitarias y de cobertura para las funciones principales.
  - [ ] 10.1 Escribir tests unitarios para cada módulo del CORE.
  - [ ] 10.2 Cubrir casos de error y edge cases.
  - [ ] 10.3 Configurar la ejecución automática de tests y generación de informes de cobertura.
  - [ ] 10.4 Revisar y mantener la cobertura superior al 80%.
