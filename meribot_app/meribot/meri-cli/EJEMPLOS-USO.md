# meri-cli - Ejemplos de Uso Prácticos

## Casos de Uso Frecuentes

### 1. Primer uso - Configurar y verificar sistema
```bash
# Verificar estado inicial de la base de datos
meri-cli db count

# Si no hay documentos, hacer crawling inicial
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --max-depth 2

# Verificar que se cargaron los documentos
meri-cli db count
meri-cli db list --show-chunks
```

### 2. Mantenimiento rutinario
```bash
# Listar documentos por dominio para auditoría
meri-cli db list --filter dominio:cca

# Actualizar documentos (solo nuevos o modificados)
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --update-only

# Verificar cambios
meri-cli db count
```

### 3. Limpiar documentos obsoletos
```bash
# Listar documentos para identificar obsoletos
meri-cli db list --filter dominio:cca

# Ver detalles de un documento específico
meri-cli db show --id "doc_12345"

# Eliminar documento obsoleto por URL
meri-cli db delete --url "https://cca.capgemini.com/old-page"

# Verificar que se eliminó
meri-cli db count
```

### 4. Procesamiento de URLs específicas
```bash
# Procesar solo páginas específicas sin crawling completo
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --manual "https://cca.capgemini.com/important-page1,https://cca.capgemini.com/important-page2"

# Verificar que se procesaron
meri-cli db list --filter dominio:cca --show-chunks
```

### 5. Crawling con filtros avanzados
```bash
# Crawling excluyendo páginas de login/logout
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --exclude ".*logout.*|.*login.*" \
  --max-depth 3

# Crawling solo de documentos PDF y HTML
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --formats "html,pdf" \
  --max-pages 50
```

### 6. Simulación antes de ejecutar
```bash
# Simular crawling para ver qué se haría
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --dry-run \
  --max-depth 2

# Si todo se ve bien, ejecutar sin --dry-run
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --max-depth 2
```

### 7. Depuración y análisis
```bash
# Ver estado general de la base de datos
meri-cli db count

# Listar todos los documentos con sus chunks
meri-cli db list --show-chunks

# Inspeccionar un documento específico para debugging
meri-cli db show --id "doc_12345"

# Eliminar documento problemático
meri-cli db delete --id "doc_12345"
```

### 8. Migración o limpieza completa
```bash
# Listar todos los documentos de un dominio
meri-cli db list --filter dominio:old_domain

# Eliminar documentos uno por uno si es necesario
# (Para limpieza completa, usar reset en la API directamente)

# Recargar con nueva configuración
meri-cli crawl --url "https://newdomain.com" --dominio "new_domain"
```

## Mejores Prácticas

### Antes de crawling importante:
1. Siempre usar `--dry-run` primero
2. Verificar estado con `db count`
3. Usar filtros `--exclude` para evitar páginas innecesarias

### Para mantenimiento:
1. Usar `--update-only` para actualizaciones incrementales
2. Monitorear regularmente con `db list --show-chunks`
3. Limpiar documentos obsoletos regularmente

### Para debugging:
1. Usar `db show --id` para inspeccionar documentos específicos
2. Verificar logs del servidor FastAPI en paralelo
3. Usar `db count` antes y después de operaciones

## Comandos de emergencia

### Si el sistema no responde:
```bash
# Verificar conectividad básica
meri-cli db count

# Si falla, verificar que el servidor esté ejecutándose
# python start_server_direct.py
```

### Si hay problemas de rendimiento:
```bash
# Limitar profundidad y páginas
meri-cli crawl --url "https://example.com" --dominio "example" \
  --max-depth 1 \
  --max-pages 10
```

### Si hay documentos corruptos:
```bash
# Identificar y eliminar documentos problemáticos
meri-cli db list
meri-cli db show --id "problematic_doc_id"
meri-cli db delete --id "problematic_doc_id"
```