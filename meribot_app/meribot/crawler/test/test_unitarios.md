# 🧪 Tests Unitarios del Módulo Crawler - MeriBot

## 📋 Descripción General

Este documento describe el sistema completo de tests unitarios implementado para el módulo **crawler** de MeriBot. Los tests han sido desarrollados usando **pytest** y proporcionan una cobertura exhaustiva de todos los componentes del crawler, asegurando la calidad, robustez y mantenibilidad del código.

## 🎯 Objetivos

- **Validar funcionalidad**: Asegurar que cada componente del crawler funciona correctamente
- **Detectar regresiones**: Identificar rápidamente cambios que rompen funcionalidad existente
- **Facilitar refactoring**: Permitir modificaciones seguras del código con confianza
- **Documentar comportamiento**: Servir como documentación viva del comportamiento esperado
- **Mejorar calidad**: Mantener altos estándares de calidad del código

## 📁 Estructura del Sistema de Tests

```
meribot/crawler/test/
├── conftest.py                     # 🔧 Fixtures centralizadas y configuración
├── pytest.ini                     # ⚙️ Configuración de pytest 
├── unitarios/                     # 📦 Tests unitarios principales
│   ├── __init__.py                # 📄 Inicialización del paquete
│   ├── test_config.py             # 🔧 Tests de configuración
│   ├── test_document_loader.py    # 📄 Tests de carga de documentos
│   ├── test_scraper.py            # 🕷️ Tests de web scraping
│   ├── test_logger.py             # 📊 Tests de logging
│   └── test_utilities.py          # 🛠️ Tests de utilidades
└── test_unitarios.md              # 📚 Esta documentación
```

## 🔧 Componentes del Sistema

### **1. conftest.py - Centro de Fixtures**

Proporciona todas las fixtures necesarias para los tests:

#### **Fixtures de Configuración**
- `valid_crawler_config`: Configuración válida completa
- `minimal_crawler_config`: Configuración mínima válida  
- `invalid_crawler_config`: Configuración inválida para tests de validación
- `temp_config_file`: Archivo YAML temporal con configuración válida
- `temp_invalid_config_file`: Archivo YAML inválido para tests de error

#### **Fixtures de Archivos y Directorios**
- `temp_output_dir`: Directorio temporal para output del crawler
- `temp_log_dir`: Directorio temporal para logs
- `sample_html_file`: Archivo HTML de ejemplo para parsing
- `sample_text_file`: Archivo de texto para tests de procesamiento

#### **Fixtures de Mocks y Datos**
- `mock_logger`: Logger mock para tests
- `mock_requests_response`: Response mock para HTTP requests
- `sample_document_metadata`: Metadata de ejemplo para documentos
- `sample_chunks`: Chunks de texto para tests de chunking
- `mock_embeddings`: Embeddings mock para tests de Azure OpenAI
- `mock_azure_openai_response`: Response mock de Azure OpenAI API

#### **Fixtures de Servicios**
- `mock_chroma_collection`: Colección ChromaDB mock
- `mock_chroma_db`: Base de datos ChromaDB mock
- `mock_hash_db`: Base de datos de hashes mock

#### **Fixtures de Entorno**
- `mock_env_variables`: Variables de entorno para tests
- `mock_env_azure_missing`: Simula variables Azure faltantes

#### **Fixtures de Web Scraping**
- `sample_urls`: URLs de ejemplo para tests
- `sample_html_with_links`: HTML con múltiples tipos de enlaces

#### **Utilidades Helper**
- `capture_logs`: Captura logs durante tests
- `clean_test_environment`: Limpia entorno entre tests
- `create_test_file()`: Helper para crear archivos temporales
- `assert_valid_config()`: Validador de configuración
- `assert_valid_document_result()`: Validador de parsing

### **2. pytest.ini - Configuración de Pytest**

```ini
[tool:pytest]
testpaths = test/unitarios
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Marcadores para categorizar tests
markers =
    unit: Unit tests
    config: Configuration tests  
    document: Document processing tests
    scraper: Web scraping tests
    logger: Logging tests
    utilities: Utility functions tests
    slow: Slow running tests
    network: Tests requiring network access
    file_io: Tests involving file operations
    azure: Tests requiring Azure services
    chroma: Tests involving ChromaDB

# Configuración de cobertura
addopts = 
    --strict-markers
    --tb=short
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80

# Variables de entorno para tests
env =
    TESTING=true
    CRAWLER_LOG_LEVEL=DEBUG
    CRAWLER_LOG_FORMAT=STANDARD
```

## 📋 Descripción Detallada de Tests

### **test_config.py - Tests de Configuración**

**Funcionalidad Cubierta:**
- ✅ Carga de configuración desde archivos YAML
- ✅ Validación de campos requeridos y tipos
- ✅ Aplicación de valores por defecto
- ✅ Override con variables de entorno
- ✅ Manejo de errores de configuración inválida
- ✅ Validación de URLs en seeds y dominios
- ✅ Validación de rutas de archivos y directorios

**Tests Principales:**
```python
# Carga exitosa de configuración
test_load_valid_config()
test_load_config_with_defaults() 
test_load_minimal_config()

# Validación de campos
test_validate_required_fields()
test_validate_field_types()
test_validate_urls_format()

# Variables de entorno
test_environment_overrides()
test_environment_priority()

# Manejo de errores
test_invalid_yaml_format()
test_missing_required_fields()
test_invalid_field_types()
test_file_not_found()
```

### **test_document_loader.py - Tests de Carga de Documentos**

**Funcionalidad Cubierta:**
- ✅ Parsing de documentos HTML, PDF, DOCX, XLSX
- ✅ Extracción de texto y metadata
- ✅ Chunking de texto con LangChain
- ✅ Generación de embeddings con Azure OpenAI
- ✅ Clasificación de chunks con hashing
- ✅ Manejo de errores de parsing
- ✅ Validación de formatos de archivo

**Tests Principales:**
```python
# Parsing por tipo de documento
test_parse_html_document()
test_parse_pdf_document()  
test_parse_docx_document()
test_parse_xlsx_document()

# Procesamiento de texto
test_text_chunking()
test_chunk_metadata_generation()
test_text_normalization()

# Embeddings
test_generate_embeddings_success()
test_generate_embeddings_api_error()
test_embedding_dimension_validation()

# Hash y clasificación
test_chunk_hash_generation()
test_duplicate_chunk_detection()

# Manejo de errores
test_unsupported_file_format()
test_corrupted_file_handling()
test_empty_file_processing()
```

### **test_scraper.py - Tests de Web Scraping**

**Funcionalidad Cubierta:**
- ✅ Inicialización del scraper con configuración
- ✅ Crawling de URLs con respeto a robots.txt
- ✅ Extracción de enlaces de páginas HTML
- ✅ Filtrado por dominios permitidos
- ✅ Descarga de archivos (PDF, DOCX, XLSX)
- ✅ Manejo de rate limiting y delays
- ✅ Gestión de errores HTTP y timeouts

**Tests Principales:**
```python
# Inicialización y configuración
test_scraper_initialization()
test_scraper_config_validation()

# Crawling de URLs
test_crawl_single_url()
test_crawl_multiple_urls()
test_respect_max_depth()

# Extracción de enlaces
test_extract_links_from_html()
test_filter_allowed_domains()
test_handle_relative_urls()
test_handle_url_fragments()

# Descarga de archivos
test_download_pdf_file()
test_download_docx_file()
test_download_xlsx_file()

# Rate limiting
test_respect_delay_between_requests()
test_handle_rate_limiting()

# Manejo de errores
test_handle_404_errors()
test_handle_connection_timeout()
test_handle_invalid_domains()
```

### **test_logger.py - Tests de Logging**

**Funcionalidad Cubierta:**
- ✅ Configuración de loggers con diferentes niveles
- ✅ Formatters JSON y Rich para diferentes outputs
- ✅ Handlers para archivos con rotación
- ✅ Handlers para consola con colores
- ✅ Filtrado de logs por niveles y módulos
- ✅ Configuración desde variables de entorno

**Tests Principales:**
```python
# Configuración de logger
test_create_logger()
test_logger_level_configuration()
test_logger_from_environment()

# Formatters
test_json_formatter()
test_rich_formatter()
test_standard_formatter()

# Handlers
test_file_handler_creation()
test_console_handler_creation()
test_rotating_file_handler()

# Funcionalidad de logging
test_log_different_levels()
test_log_with_metadata()
test_log_filtering()

# Configuración avanzada
test_multiple_handlers()
test_custom_log_format()
test_log_file_rotation()
```

### **test_utilities.py - Tests de Utilidades**

**Funcionalidad Cubierta:**
- ✅ CLI de búsqueda semántica (check_embeddings.py)
- ✅ Explorador de ChromaDB (chroma_explorer.py)
- ✅ Parsing de argumentos de línea de comandos
- ✅ Interacción con base de datos vectorial
- ✅ Formateo de resultados para consola

**Tests Principales:**
```python
# SemanticSearchCLI
test_semantic_search_cli_initialization()
test_parse_search_arguments()
test_execute_search_query()
test_format_search_results()

# ChromaExplorer  
test_chroma_explorer_initialization()
test_explore_collections()
test_query_collection_stats()
test_export_collection_data()

# Utilidades comunes
test_argument_parsing()
test_error_handling()
test_output_formatting()
```

## 🚀 Ejecución de Tests

### **Comandos Básicos**

```bash
# Navegar al directorio del crawler
cd meribot_app/meribot/crawler

# Ejecutar todos los tests unitarios
pytest test/unitarios/ -v

# Ejecutar tests con output detallado
pytest test/unitarios/ -v -s

# Ejecutar tests con cobertura
pytest test/unitarios/ --cov=. --cov-report=html

# Ejecutar tests en modo silencioso
pytest test/unitarios/ -q
```

### **Ejecución por Categorías**

```bash
# Tests de configuración únicamente
pytest -m "config" -v

# Tests de procesamiento de documentos
pytest -m "document" -v

# Tests de web scraping
pytest -m "scraper" -v  

# Tests de logging
pytest -m "logger" -v

# Tests de utilidades
pytest -m "utilities" -v
```

### **Filtrado Avanzado**

```bash
# Excluir tests que requieren red
pytest -m "not network" -v

# Excluir tests que requieren Azure
pytest -m "not azure" -v

# Solo tests rápidos (sin slow, network, azure)
pytest -m "not slow and not network and not azure" -v

# Tests específicos de ChromaDB
pytest -m "chroma" -v

# Tests que involucran operaciones de archivo
pytest -m "file_io" -v
```

### **Ejecución de Tests Específicos**

```bash
# Test específico por nombre
pytest test/unitarios/test_config.py::test_load_valid_config -v

# Tests de una clase específica
pytest test/unitarios/test_scraper.py::TestWebScraper -v

# Tests que coincidan con patrón
pytest -k "test_config" -v

# Tests que contengan una palabra
pytest -k "validation" -v
```

## 📊 Cobertura de Tests

### **Métricas de Cobertura**

El sistema está configurado para:
- **Objetivo mínimo**: 80% de cobertura de código
- **Reportes**: HTML y terminal con líneas faltantes
- **Exclusiones**: Archivos de configuración y tests

### **Generar Reportes de Cobertura**

```bash
# Reporte en terminal
pytest test/unitarios/ --cov=. --cov-report=term-missing

# Reporte HTML detallado
pytest test/unitarios/ --cov=. --cov-report=html

# Reporte XML para CI/CD
pytest test/unitarios/ --cov=. --cov-report=xml

# Reporte combinado
pytest test/unitarios/ --cov=. --cov-report=term --cov-report=html --cov-report=xml
```

### **Interpretar Reportes**

El reporte HTML (`htmlcov/index.html`) proporciona:
- **Vista general**: Porcentaje de cobertura por archivo
- **Detalles por archivo**: Líneas cubiertas vs no cubiertas
- **Ramas no cubiertas**: Condicionales no testeados
- **Funciones faltantes**: Funciones sin tests

## 🎭 Estrategia de Mocking

### **Servicios Externos Mockeados**

#### **Azure OpenAI API**
```python
# Mock de respuesta de embeddings
@pytest.fixture
def mock_azure_openai_response():
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0, 
                "embedding": [0.1, 0.2, ...] # 1536 dimensiones
            }
        ],
        "model": "text-embedding-ada-002"
    }
```

#### **ChromaDB**
```python
# Mock de colección ChromaDB
@pytest.fixture  
def mock_chroma_collection():
    collection = MagicMock()
    collection.name = "test_collection"
    collection.count.return_value = 100
    return collection
```

#### **HTTP Requests**
```python
# Mock de response HTTP
@pytest.fixture
def mock_requests_response():
    response = MagicMock()
    response.status_code = 200
    response.headers = {"Content-Type": "text/html; charset=utf-8"}
    response.text = "<html><body>Test content</body></html>"
    return response
```

### **Aislamiento de Tests**

- **File System**: Uso de archivos temporales que se limpian automáticamente
- **Network**: Todos los requests HTTP son mockeados
- **Database**: ChromaDB completamente mockeado sin persistencia
- **Environment**: Variables de entorno controladas por test
- **Logging**: Captura de logs sin impacto en sistema

## ⚡ Optimización y Performance

### **Tests Paralelos**

```bash
# Ejecutar tests en paralelo (requiere pytest-xdist)
pip install pytest-xdist

# Ejecutar con 4 workers
pytest test/unitarios/ -n 4

# Auto-detectar número de CPUs
pytest test/unitarios/ -n auto
```

### **Cache de Tests**

```bash
# Usar cache para tests que no han cambiado
pytest test/unitarios/ --cache-clear  # Limpiar cache
pytest test/unitarios/ --lf           # Solo tests fallidos
pytest test/unitarios/ --ff           # Tests fallidos primero
```

### **Configuración de Performance**

```python
# En conftest.py - optimizaciones automáticas
def pytest_configure(config):
    """Optimizaciones de configuración."""
    # Configurar logging para tests
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Configurar warnings
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
```

## 🔍 Debugging y Troubleshooting

### **Debugging Tests Fallidos**

```bash
# Ejecutar con debug verbose
pytest test/unitarios/ -vvv

# Parar en primer fallo
pytest test/unitarios/ -x

# Mostrar traceback completo
pytest test/unitarios/ --tb=long

# Entrar en debugger en fallos
pytest test/unitarios/ --pdb
```

### **Logs durante Tests**

```bash
# Mostrar prints y logs
pytest test/unitarios/ -s

# Capturar logs a nivel específico
pytest test/unitarios/ --log-level=DEBUG

# Mostrar logs solo en fallos
pytest test/unitarios/ --log-on-failure
```

### **Problemas Comunes**

#### **ImportError en Tests**
```bash
# Asegurar que el módulo está en PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest test/unitarios/

# O usar instalación en modo desarrollo
pip install -e .
```

#### **Fixtures No Encontradas**
```python
# Verificar que conftest.py está en lugar correcto
test/
├── conftest.py        # ✅ Aquí
└── unitarios/
    ├── conftest.py    # ❌ No necesario
    └── test_*.py
```

#### **Marcadores No Reconocidos**
```bash
# Verificar pytest.ini o añadir marcador
pytest.ini:
markers =
    custom_marker: descripción del marcador
```

## 📈 Métricas y Reportes

### **Reportes Avanzados**

```bash
# Reporte JUnit para CI/CD
pytest test/unitarios/ --junit-xml=reports/junit.xml

# Reporte detallado en JSON
pytest test/unitarios/ --json-report --json-report-file=reports/report.json

# Timing de tests
pytest test/unitarios/ --durations=10  # Top 10 tests más lentos
```

### **Análisis de Performance**

```python
# Profile específico de test
@pytest.mark.slow
def test_performance_critical_function():
    import cProfile
    pr = cProfile.Profile()
    pr.enable()
    
    # Código del test
    result = expensive_operation()
    
    pr.disable()
    pr.dump_stats('test_profile.prof')
    
    assert result is not None
```

## 🔄 Integración con CI/CD

### **GitHub Actions**

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run unit tests
      run: |
        cd meribot_app/meribot/crawler
        pytest test/unitarios/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### **Pre-commit Hooks**

```yaml
# .pre-commit-config.yaml
repos:
- repo: local
  hooks:
  - id: pytest-check
    name: pytest-check
    entry: pytest
    args: [test/unitarios/, -x]
    language: system
    pass_filenames: false
    always_run: true
```

## 📚 Mejores Prácticas

### **Escritura de Tests**

1. **Tests Atómicos**: Cada test verifica un solo comportamiento
2. **Nombres Descriptivos**: Nombres que explican qué se está probando
3. **AAA Pattern**: Arrange, Act, Assert bien definidos
4. **Mocks Apropiados**: Mockear dependencias externas, no lógica interna
5. **Datos de Test**: Usar fixtures para datos reutilizables

### **Mantenimiento**

1. **Refactoring**: Mantener tests actualizados con cambios de código
2. **Cobertura**: Revisar regularmente reportes de cobertura
3. **Performance**: Monitorear tiempo de ejecución de tests
4. **Documentación**: Mantener esta documentación actualizada

### **Debugging**

1. **Tests Incrementales**: Agregar tests antes de arreglar bugs
2. **Isolation**: Verificar que tests son independientes
3. **Reproducibilidad**: Asegurar que tests son determinísticos

## 🎯 Próximos Pasos

### **Expansión del Sistema**

- [ ] **Tests de Integración**: Tests que verifiqueRn interacción entre módulos
- [ ] **Tests End-to-End**: Tests completos del flujo de crawler
- [ ] **Tests de Performance**: Benchmarks y tests de carga
- [ ] **Tests de Seguridad**: Validación de inputs maliciosos

### **Mejoras Técnicas**

- [ ] **Property-Based Testing**: Usar Hypothesis para tests generativos
- [ ] **Mutation Testing**: Usar mutmut para verificar calidad de tests
- [ ] **Visual Testing**: Screenshots para tests de interfaces
- [ ] **API Contract Testing**: Validar contratos de API

### **Automatización**

- [ ] **Auto-generación**: Scripts para generar tests base
- [ ] **Reportes Automáticos**: Dashboard de métricas de tests
- [ ] **Notificaciones**: Alertas en fallos de tests críticos

## 📞 Soporte y Contacto

Para preguntas sobre los tests unitarios:

1. **Documentación**: Revisar este documento y comentarios en código
2. **Issues**: Crear issue en el repositorio con tag `testing`
3. **Debug**: Usar `pytest --pdb` para debugging interactivo
4. **Logs**: Revisar logs en modo verbose `pytest -v -s`

---

## 📄 Conclusión

Este sistema de tests unitarios proporciona una base sólida para el desarrollo y mantenimiento del módulo crawler de MeriBot. Con cobertura exhaustiva, mocking apropiado y documentación detallada, los tests aseguran la calidad y confiabilidad del código mientras facilitan el desarrollo futuro.

La implementación sigue las mejores prácticas de testing en Python y pytest, proporcionando un sistema mantenible, escalable y fácil de usar para todo el equipo de desarrollo.

**¡Los tests están listos para usar y validar el correcto funcionamiento del crawler!** 🚀