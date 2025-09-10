## Archivos relevantes

- `meribot/meri-cli/main.py` - Punto de entrada principal de la CLI.
- `meribot/meri-cli/db_commands.py` - Lógica de los subcomandos `db`.
- `meribot/meri-cli/tests/test_db_commands.py` - Pruebas unitarias para los subcomandos `db`.

### Notas

- Toda la lógica debe implementarse en la capa CLI, reutilizando únicamente las interfaces públicas del core, sin modificar ni extender su código.

## Tareas

- [x] 1.0 Definir e implementar el subcomando `db` en la CLI, usando solo interfaces públicas del core
  - [x] 1.1 Crear el archivo `db_commands.py` y definir la estructura base para el subcomando `db`
  - [x] 1.2 Registrar el subcomando `db` en `main.py` usando el framework CLI existente (por ejemplo, Click, Typer, argparse)
- [ ] 2.0 Implementar la opción `list` para mostrar documentos almacenados y sus filtros, usando funciones públicas existentes
  - [x] 2.1 Implementar la función `list` en `db_commands.py` que obtenga y muestre la lista de documentos
  - [x] 2.2 Añadir soporte para filtros solo si están disponibles en las interfaces públicas del core
  - [ ] 2.3 Mostrar los chunks asociados si la opción es soportada
- [ ] 3.0 Implementar la opción `delete --id <DOCUMENT_ID>` para eliminar documentos y sus fragmentos, usando funciones públicas existentes
  - [ ] 3.1 Implementar la función `delete` en `db_commands.py` que elimine el documento por ID
  - [ ] 3.2 Validar y mostrar mensajes de éxito o error según el resultado
- [ ] 4.0 Implementar la opción `show --id <DOCUMENT_ID>` para mostrar información detallada y metadatos, usando funciones públicas existentes
  - [ ] 4.1 Implementar la función `show` en `db_commands.py` que obtenga y muestre los detalles del documento
  - [ ] 4.2 Validar la existencia del documento y mostrar mensajes adecuados
- [ ] 5.0 Implementar la opción `count` para devolver el número total de documentos y/o fragmentos, usando funciones públicas existentes
  - [ ] 5.1 Implementar la función `count` en `db_commands.py` que obtenga y muestre el conteo
  - [ ] 5.2 Mostrar el resultado de forma clara y legible
- [ ] 6.0 Añadir y documentar filtros por dominio, fecha, tipo, etc., solo si son soportados por el core
  - [ ] 6.1 Documentar en la ayuda de la CLI qué filtros están disponibles y cómo usarlos
- [ ] 7.0 Escribir pruebas unitarias para cada subcomando y opción
  - [ ] 7.1 Crear el archivo de pruebas `test_db_commands.py`
  - [ ] 7.2 Escribir pruebas para `list`, `delete`, `show` y `count`
  - [ ] 7.3 Incluir casos de éxito, error y uso de filtros
