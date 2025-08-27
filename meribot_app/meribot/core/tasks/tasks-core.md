## Archivos relevantes

- `meribot_app/meribot/core/__init__.py` – Inicialización y configuración del módulo CORE.
- `meribot_app/meribot/core/conversation.py` – Lógica de gestión de conversaciones y contexto.
- `meribot_app/meribot/core/plugin_manager.py` – Gestión y registro de plugins.
- `meribot_app/meribot/core/vector_search.py` – Integración y consultas a la base vectorial (ChromaDB).
- `meribot_app/meribot/core/cache.py` – Gestión de caché de respuestas.
- `meribot_app/meribot/core/logging.py` – Logging y auditoría de eventos.
- `meribot_app/meribot/core/config.py` – Configuración del motor de chat y parámetros clave.
- `meribot_app/meribot/core/guardrails.py` – Validación, sanitización y control de seguridad.
- `meribot_app/meribot/core/tests/` – Pruebas unitarias para cada uno de los módulos anteriores.
- `meribot_app/meribot/api/app.py` – Exposición de endpoints REST para integración con frontend.

### Notas

- Las pruebas unitarias deben ubicarse en `meribot_app/meribot/core/tests/` siguiendo la convención del proyecto.
- Los nombres de los archivos pueden ajustarse según la estructura final y convenciones internas.

## Tareas

- [X] 1.0 Implementar la gestión de conversaciones y contexto.
  - [X] 1.1 Definir la estructura de datos para el contexto conversacional.
  - [X] 1.2 Implementar la creación y cierre de sesiones de conversación.
  - [X] 1.3 Mantener el historial de mensajes durante la sesión activa.
  - [X] 1.4 Eliminar el historial al cerrar el panel de conversación.
  - [X] 1.5 Añadir identificadores únicos para cada conversación.
  - [x] 1.6 Realizar pruebas unitarias de la gestión de conversaciones y contexto.
- [x] 2.0 Desarrollar el sistema de plugins y su integración con el CORE.
  - [x] 2.1 Diseñar la clase base para plugins.
  - [x] 2.2 Implementar el registro y activación/desactivación de plugins.
  - [x] 2.3 Permitir que los plugins accedan al contexto y metadatos de la consulta.
  - [x] 2.4 Documentar el proceso de creación de nuevos plugins.
  - [x] 2.5 Realizar pruebas unitarias del sistema de plugins.
- [x] 3.0 Integrar la base vectorial para búsquedas semánticas y citación de fuentes.
  - [x] 3.1 Implementar la conexión con ChromaDB.
  - [x] 3.2 Desarrollar la función de búsqueda semántica de fragmentos relevantes.
  - [x] 3.3 Permitir filtrar resultados por dominio y otros metadatos.
  - [x] 3.4 Citar las fuentes utilizadas en las respuestas.
  - [x] 3.5 Realizar pruebas unitarias de la integración de la base vectorial.
- [ ] 4.0 Implementar la gestión de caché de respuestas frecuentes.
  - [ ] 4.1 Diseñar la estructura de la caché y su integración con el CORE.
  - [ ] 4.2 Configurar el tiempo de vida de la caché.
  - [ ] 4.3 Implementar la invalidación automática al actualizar documentos fuente.
  - [ ] 4.4 Optimizar la recuperación de respuestas frecuentes.
  - [ ] 4.5 Realizar pruebas unitarias de la gestión de caché.
- [ ] 5.0 Configurar y exponer parámetros clave del motor de chat.
  - [ ] 5.1 Permitir la configuración mediante variables de entorno o archivo.
  - [ ] 5.2 Habilitar la selección dinámica del modelo de IA.
  - [ ] 5.3 Configurar el system prompt y parámetros como temperatura y tokens.
  - [ ] 5.4 Documentar las opciones de configuración disponibles.
  - [ ] 5.5 Realizar pruebas unitarias de la configuración del motor de chat.
- [ ] 6.0 Implementar logging y auditoría de eventos y errores.
  - [ ] 6.1 Registrar errores y eventos críticos.
  - [ ] 6.2 Registrar inputs rechazados por guardrails y fallos de generación.
  - [ ] 6.3 Garantizar que los logs permitan auditoría técnica sin exponer datos sensibles.
  - [ ] 6.4 Configurar niveles de logging y rotación de logs.
  - [ ] 6.5 Realizar pruebas unitarias de logging y auditoría.
- [ ] 7.0 Desarrollar validaciones, sanitización y guardrails de seguridad.
  - [ ] 7.1 Implementar validación y sanitización de entradas del usuario.
  - [ ] 7.2 Añadir guardrails para evitar respuestas inadecuadas o peligrosas.
  - [ ] 7.3 Garantizar cumplimiento de estándares de seguridad y accesibilidad.
  - [ ] 7.4 Probar casos extremos y edge cases de seguridad.
  - [ ] 7.5 Realizar pruebas unitarias de validaciones y guardrails.
- [ ] 8.0 Exponer endpoints REST para integración con el widget web y panel de administración.
  - [ ] 8.1 Definir los endpoints necesarios para la comunicación frontend-backend.
  - [ ] 8.2 Implementar los endpoints en `api/app.py`.
  - [ ] 8.3 Documentar la API REST y sus parámetros.
  - [ ] 8.4 Asegurar la autenticación y autorización donde aplique.
  - [ ] 8.5 Realizar pruebas unitarias de los endpoints REST.
- [ ] 9.0 Crear pruebas unitarias y de cobertura para las funciones principales.
  - [ ] 9.1 Escribir tests unitarios para cada módulo del CORE.
  - [ ] 9.2 Cubrir casos de error y edge cases.
  - [ ] 9.3 Configurar la ejecución automática de tests y generación de informes de cobertura.
  - [ ] 9.4 Revisar y mantener la cobertura superior al 80%.
  - [ ] 9.5 Realizar pruebas unitarias de cobertura general.
