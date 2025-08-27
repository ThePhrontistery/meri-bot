# Regla: Generación de una lista de tareas a partir de un PRD

## Objetivo

Guiar a un asistente de IA en la creación de una lista de tareas detallada, paso a paso, en formato Markdown, basada en un Documento de Requisitos del Producto (PRD) existente. La lista de tareas debe guiar al desarrollador durante la implementación.

## Resultado

- **Formato:** Markdown (`.md`)
- **Ubicación:** `core/tasks/`
- **Nombre de archivo:** `tasks-core.md` 

## Proceso

1. **Recibir referencia del PRD:** El usuario dirige a la IA a un archivo PRD específico.
2. **Analizar el PRD:** La IA lee y analiza los requisitos funcionales, las historias de usuario y otras secciones del PRD especificado.
3. **Evaluar el estado actual:** Revisar el código base existente para comprender la infraestructura, los patrones arquitectónicos y las convenciones existentes. Además, identifique cualquier componente o característica existente que pueda ser relevante para los requisitos del PRD. Luego, identifique los archivos, componentes y utilidades relacionados que se puedan aprovechar o que requieran modificaciones.
4. **Fase 1: Generar Tareas Principales:** Con base en el análisis del PRD y la evaluación del estado actual, cree el archivo y genere las tareas principales de alto nivel necesarias para implementar la característica. Use su criterio para determinar cuántas tareas de alto nivel utilizar. Es probable que sean aproximadamente...
5. **Informar al usuario:** Presente estas tareas al usuario en el formato especificado (sin subtareas todavía). Por ejemplo, diga: "He generado las tareas de alto nivel basadas en el PRD. ¿Listo para generar las subtareas? Responda con 'Ir' para continuar".
6. **Esperar Confirmación:** Haga una pausa y espere a que el usuario responda con 'Ir'. 7. **Fase 2: Generar subtareas:** Una vez que el usuario confirme, divida cada tarea principal en subtareas más pequeñas y prácticas, necesarias para completarla. Asegúrese de que las subtareas se deriven lógicamente de la tarea principal, cubran los detalles de implementación implícitos en el PRD y consideren los patrones de código base existentes cuando sea relevante, sin limitarse a ellos.

8. **Identificar archivos relevantes:** Con base en las tareas y el PRD, identifique los posibles archivos que deban crearse o modificarse. Enumérelos en la sección "Archivos relevantes", incluyendo los archivos de prueba correspondientes, si corresponde.

9. **Generar resultado final:** Combine las tareas principales, las subtareas, los archivos relevantes y las notas en la estructura final de Markdown. 

10. **Guardar lista de tareas:** Guarde el documento generado en el directorio `core/tasks/` con el nombre `tasks-core.md`

## Formato de salida

La lista de tareas generada _debe_ seguir esta estructura:

```markdown
## Archivos relevantes

- `path/to/potential/file1.ts` - Breve descripción de la relevancia de este archivo (p. ej., contiene el componente principal para esta función).
- `path/to/file1.test.ts` - Pruebas unitarias para `file1.ts`. - `path/to/another/file.tsx` - Breve descripción (p. ej., controlador de ruta de la API para el envío de datos).
- `path/to/another/file.test.tsx` - Pruebas unitarias para `another/file.tsx`.
- `lib/utils/helpers.ts` - Breve descripción (p. ej., funciones de utilidad necesarias para los cálculos).
- `lib/utils/helpers.test.ts` - Pruebas unitarias para `helpers.ts`.

### Notas

- Las pruebas unitarias suelen colocarse junto con los archivos de código que se están probando (p. ej., `MyComponent.tsx` y `MyComponent.test.tsx` en el mismo directorio).
- Use `npx jest [opcional/path/to/test/file]` para ejecutar las pruebas. Si se ejecuta sin una ruta, se ejecutan todas las pruebas encontradas por la configuración de Jest.

## Tareas

- [ ] 1.0 Título de la tarea principal
- [ ] 1.1 [Descripción de la subtarea 1.1]
- [ ] 1.2 [Descripción de la subtarea 1.2]
- [ ] 2.0 Título de la tarea principal
- [ ] 2.1 [Descripción de la subtarea 2.1]
- [ ] 3.0 Título de la tarea principal (puede que no requiera subtareas si es puramente estructural o de configuración)
```

## Modelo de interacción

El proceso requiere explícitamente una pausa después de generar las tareas principales para obtener la confirmación del usuario ("Ir") antes de proceder a generar las subtareas detalladas. Esto garantiza que el plan general se ajuste a las expectativas del usuario antes de profundizar en los detalles.

## Público objetivo

Suponga que el lector principal de la lista de tareas es un **desarrollador júnior** que implementará la función teniendo en cuenta el contexto del código base existente.