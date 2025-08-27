# Gestión de listas de tareas

Directrices para gestionar listas de tareas en archivos Markdown y seguir el progreso de un PRD

## Implementación de tareas
- **Una subtarea a la vez:** **NO** comience la siguiente subtarea hasta que solicite permiso al usuario y este responda "sí" o "sí".
- **Protocolo de finalización:**
1. Al finalizar una **subtarea**, márquela inmediatamente como completada cambiando `[ ]` por `[x]`.
2. Si **todas** las subtareas de una tarea principal son ahora `[x]`, siga esta secuencia:
- **Primero**: Ejecute el conjunto de pruebas completo (`pytest`, `npm test`, `bin/rails test`, etc.)
- **Solo si todas las pruebas superan**: Prepare los cambios (`git add .`)
- **Limpieza**: Elimine los archivos y el código temporales antes de confirmar.
- **Confirmación**: Use un mensaje de confirmación descriptivo que:
- Use el formato de confirmación convencional (`feat:`, `fix:`, `refactor:`, etc.)
- Resuma lo logrado en la tarea principal.
- Enumere los cambios y adiciones clave.
- Haga referencia al número de tarea y al contexto PRD.
- **Formatee el mensaje como un comando de una sola línea usando indicadores `-m`**, p. ej.:

```
git commit -m "feat: añadir lógica de validación de pago" -m "- Valida el tipo y la fecha de caducidad de la tarjeta" -m "- Añade la unidad Pruebas para casos extremos" -m "Relacionado con T123 en PRD"
```
3. Una vez que todas las subtareas estén marcadas como completadas y los cambios se hayan confirmado, marque la **tarea principal** como completada.
- Deténgase después de cada subtarea y espere la autorización del usuario.

## Mantenimiento de la lista de tareas

1. **Actualice la lista de tareas a medida que trabaja:**
- Marque las tareas y subtareas como completadas (`[x]`) según el protocolo anterior.
- Agregue nuevas tareas a medida que surjan.

2. **Mantenga la sección "Archivos relevantes":**
- Enumere todos los archivos creados o modificados.
- Describa su propósito en una línea para cada archivo.

## Instrucciones de la IA

Al trabajar con listas de tareas, la IA debe:

1. Actualizar regularmente el archivo de la lista de tareas después de finalizar cualquier trabajo significativo.
2. Siga el protocolo de finalización:
- Marque cada **subtarea** terminada como `[x]`. - Marca la **tarea principal** con `[x]` una vez que **todas** sus subtareas sean `[x]`.
3. Agrega las tareas recién descubiertas.
4. Mantén los "Archivos relevantes" precisos y actualizados.
5. Antes de empezar a trabajar, comprueba cuál es la siguiente subtarea.
6. Después de implementar una subtarea, actualiza el archivo y espera la aprobación del usuario.
Enviar comentarios
