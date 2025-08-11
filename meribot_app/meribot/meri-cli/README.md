# Capa Administrativa

## Descripción
Este módulo proporciona herramientas de línea de comandos (CLI) para la administración y mantenimiento del sistema MeriBot. Permite gestionar el scraper, la base de datos vectorial y realizar tareas administrativas sin necesidad de acceder directamente a la API o la base de datos.

## Características Principales
- Interfaz de línea de comandos intuitiva
- Gestión del servicio de scraping
- Administración de la base de datos vectorial
- Herramientas de diagnóstico y monitoreo
- Generación de informes

## Comandos Principales

### Gestión del Scraper
```bash
# Ejecutar scraping manual
meribot scrape --url https://cca.capgemini.com/web/home

# Ver logs del scraper
meribot logs scraper --tail 100

# Forzar reindexación completa
meribot scrape --reindex
```

### Gestión de la Base de Datos
```bash
# Ver estado de la base de datos
meribot db status

# Realizar respaldo
meribot db backup --output backups/

# Restaurar desde respaldo
meribot db restore --input backups/backup_20230808.zip

# Limpiar documentos obsoletos
meribot db cleanup --older-than 30d
```

### Herramientas de Diagnóstico
```bash
# Verificar conectividad con servicios
meribot diagnose connectivity

# Verificar estado de la base vectorial
meribot diagnose vector-db

# Probar consultas de ejemplo
meribot test queries --count 10
```

## Estructura del Módulo
```
cli/
├── __init__.py
├── main.py              # Punto de entrada principal
├── commands/            # Comandos CLI
│   ├── scrape.py        # Comandos de scraping
│   ├── db.py           # Comandos de base de datos
│   └── diagnose.py     # Herramientas de diagnóstico
└── utils/              # Utilidades
    ├── output.py       # Formateo de salida
    └── validators.py   # Validación de parámetros
```

## Configuración
La CLI puede configurarse mediante:
1. Archivo de configuración (`~/.meribot/config.ini`)
2. Variables de entorno
3. Argumentos de línea de comandos

### Ejemplo de Configuración
```ini
[cli]
# Nivel de verbosidad (DEBUG, INFO, WARNING, ERROR)
log_level = INFO

# Formato de salida (json, table, csv)
output_format = table

[scraper]
# Directorio de salida por defecto
output_dir = ./data/scraped

# Usuario y contraseña para autenticación
username = admin
# password =  # Se recomienda usar variables de entorno
```

## Variables de Entorno
```bash
# Nivel de log (DEBUG, INFO, WARNING, ERROR)
export MERIBOT_LOG_LEVEL=INFO

# Formato de salida (json, table, csv)
export MERIBOT_OUTPUT_FORMAT=table

# Configuración de ChromaDB
export CHROMADB_HOST=localhost
export CHROMADB_PORT=8000
```

## Ejemplos de Uso Avanzado

### Programar Tareas con Cron
```bash
# Ejecutar scraping automaticamente a las 2 AM cada viernes
0 2 * * * /usr/local/bin/meribot scrape --url https://cca.capgemini.com/web/home --output /data/scraped/$(date +\%Y\%m\%d)

# Respaldar la base de datos cada domingos a las 3 AM
0 3 * * 0 /usr/local/bin/meribot db backup --output /backups/
```

### Generar Informes
```bash
# Generar informe de uso
meribot report usage --start 2023-01-01 --end 2023-12-31 --format pdf

# Exportar datos de consultas
meribot report queries --output queries.csv --format csv
```

## Seguridad
- Las credenciales sensibles deben manejarse mediante variables de entorno
- Se recomienda usar cuentas con privilegios limitados
- Todas las operaciones sensibles requieren confirmación
- Los logs no incluyen información sensible

## Dependencias
- Click (para la interfaz de comandos)
- Rich (para salida formateada)
- PyYAML (para manejo de configuración)
- python-dotenv (para variables de entorno)

## Notas de Implementación
- Los comandos deben ser atómicos y tener una única responsabilidad
- Proporcionar siempre retroalimentación clara al usuario
- Incluir validación de parámetros
- Manejar adecuadamente los errores y proporcionar mensajes útiles
- Documentar todos los comandos con ejemplos de uso
