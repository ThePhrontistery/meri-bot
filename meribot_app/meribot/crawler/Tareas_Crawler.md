# Lista de Tareas – Crawler de Meri-bot

## 1. Configuración Inicial y Acceso
1.1. Analizar la estructura de la página corporativa y mapear rutas de acceso a HTML y documentos.  

## 2. Extracción de Fuentes de Información (Prioridad P0)
2.1. Implementar extracción de contenido HTML de la página corporativa.  
2.2. Implementar extracción y parsing de documentos Word (.docx).  
2.3. Implementar extracción y parsing de documentos Excel (.xlsx).  
2.4. Implementar extracción y parsing de documentos PDF.

## 3. Procesamiento y Filtrado (Prioridad P0)
3.1. Extraer texto principal y metadatos relevantes de cada fuente (título, fecha, autor, versión, etc.).  
3.2. Estructurar los datos extraídos en formato compatible con ChromaDB (vectorial).  
3.3. Excluir duplicados y validar integridad de los datos extraídos.

## 4. Almacenamiento en ChromaDB (Prioridad P0)
4.1. Configurar conexión y esquema de almacenamiento en ChromaDB.  
4.2. Insertar los datos procesados en la base de datos vectorial.

## 5. Frecuencia y Disparadores (Prioridad P0)
5.1. Programar ejecución automática semanal del Crawler.  
5.2. Implementar lógica para detectar cambios en la fecha de versión de documentos y páginas.  
5.3. Implementar disparador manual de ejecución desde Meri-Cli.

## 6. Gestión de Errores y Edge Cases (Prioridad P0)
6.1. Implementar manejo de errores para fuentes inaccesibles o formatos no soportados.  
6.2. Definir y mostrar mensajes estándar para “no answer found” y “acceso restringido”.  
6.3. Registrar todos los errores y eventos relevantes en logs accesibles desde Meri-Cli.

## 7. Integración y Administración (Prioridad P0)
7.1. Integrar el Crawler con la herramienta Meri-Cli para administración y monitoreo.  
7.2. Exponer comandos en Meri-Cli para:  
  - Ejecutar el Crawler manualmente  
  - Consultar logs y métricas básicas  
  - Verificar estado y última ejecución
