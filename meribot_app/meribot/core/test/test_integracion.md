# 🔗 Tests de Integración - MeriBot Core Component

## 🎯 Propósito

Este documento describe la suite completa de **tests de integración** generados para el **componente core de MeriBot**. Los tests validan la correcta comunicación y coordinación entre el módulo core y el resto de módulos de la aplicación (crawler, web, services, utils), así como workflows completos end-to-end.

---

## 📁 Estructura de Tests de Integración

```
meribot/core/test/integracion/
├── __init__.py                              # Inicialización del paquete
├── test_core_crawler_integration.py         # Integración Core ↔ Crawler
├── test_core_web_integration.py            # Integración Core ↔ Web
├── test_core_services_integration.py       # Integración Core ↔ Services
├── test_core_utils_integration.py          # Integración Core ↔ Utils
└── test_end_to_end_integration.py          # Tests End-to-End completos
```

---

## 🎯 Cobertura de Integración por Módulos

### **1. Core ↔ Crawler Integration (test_core_crawler_integration.py)**

#### **Funcionalidades Validadas:**
- ✅ **Configuración compartida** - Core usa config YAML del crawler
- ✅ **Validación de dominios** - Core valida usando dominios del crawler
- ✅ **ChromaDB connector** - Core accede a datos indexados por crawler
- ✅ **Búsquedas vectoriales** - Core busca contenido procesado por crawler
- ✅ **Metadatos de documentos** - Core maneja metadatos del crawler
- ✅ **Filtrado por dominios** - Core filtra usando configuración crawler
- ✅ **Manejo de errores** - Core maneja fallos del crawler gracefully

#### **Escenarios de Test:**
- Carga de configuración desde `crawler_config.yaml`
- Rechazo de dominios no permitidos por crawler
- Búsqueda de contenido indexado por crawler
- Procesamiento de metadatos completos del crawler
- Integración de estrategias de chunking
- Manejo de errores de conexión con ChromaDB

#### **Markers de Pytest:**
```python
@pytest.mark.integration
@pytest.mark.crawler
@pytest.mark.external  # Para tests que requieren servicios reales
```

---

### **2. Core ↔ Web Integration (test_core_web_integration.py)**

#### **Funcionalidades Validadas:**
- ✅ **API endpoints** - Disponibilidad de endpoints para web
- ✅ **Formato de requests** - Core procesa requests del widget web
- ✅ **Formato de responses** - Core genera responses compatibles con web
- ✅ **CORS handling** - Configuración CORS para widget web
- ✅ **Streaming responses** - Core provee streaming para web
- ✅ **Gestión de sesiones** - Persistencia de sesiones web en core
- ✅ **Archivos estáticos** - Servir CSS/JS del widget
- ✅ **Validación de requests** - Core valida inputs desde web

#### **Escenarios de Test:**
- Request/response flow completo desde widget
- Configuración CORS para cross-origin requests
- Streaming de respuestas en tiempo real
- Gestión de múltiples sesiones web concurrentes
- Manejo de errores en formato web-friendly
- Validación de requests malformados desde web

#### **Markers de Pytest:**
```python
@pytest.mark.integration
@pytest.mark.web
@pytest.mark.api
```

---

### **3. Core ↔ Services Integration (test_core_services_integration.py)**

#### **Funcionalidades Validadas:**
- ✅ **ChromaDB Integration Service** - Core usa servicios de ChromaDB
- ✅ **Crawler Endpoint Service** - Core coordina con servicios de crawler
- ✅ **Process Docs Service** - Core integra con procesamiento de docs
- ✅ **Orquestación de servicios** - Core coordina múltiples servicios
- ✅ **Flujo de datos** - Datos fluyen desde services hacia core
- ✅ **Configuración compartida** - Core y services usan misma config
- ✅ **Manejo de errores** - Core maneja fallos de servicios
- ✅ **Autenticación** - Propagación de auth entre módulos

#### **Escenarios de Test:**
- Integración con `chroma_integration.py` service
- Coordinación con endpoints de crawler service
- Uso de servicios de procesamiento de documentos
- Flujo de datos desde services hacia core
- Manejo de errores cuando services no están disponibles
- Integración de cache y monitoreo con services

#### **Markers de Pytest:**
```python
@pytest.mark.integration
@pytest.mark.services
@pytest.mark.external  # Para servicios reales
```

---

### **4. Core ↔ Utils Integration (test_core_utils_integration.py)**

#### **Funcionalidades Validadas:**
- ✅ **Cargador de configuración** - Core usa `load_config_from_yaml` de utils
- ✅ **Sistema de logging** - Core usa logger centralizado de utils
- ✅ **System prompt loading** - Core carga prompts usando utils
- ✅ **Validación compartida** - Core usa validación de utils
- ✅ **Hash utilities** - Core usa funciones de hash de utils
- ✅ **JSON formatting** - Core usa formateadores de utils
- ✅ **Variables de entorno** - Core accede a env vars via utils
- ✅ **Manejo de errores** - Core usa error handling de utils

#### **Escenarios de Test:**
- Carga de configuración YAML usando utils
- Logging centralizado y rotación de logs
- Carga de system prompts desde archivos
- Uso de utilidades de hash para contenido
- Integración de formateadores JSON
- Acceso a variables de entorno via utils

#### **Markers de Pytest:**
```python
@pytest.mark.integration
@pytest.mark.utils
@pytest.mark.external  # Para archivos reales
```

---

### **5. End-to-End Integration (test_end_to_end_integration.py)**

#### **Workflows Completos Validados:**
- ✅ **Workflow de Onboarding** - Desde pregunta web hasta respuesta con citaciones
- ✅ **Flujo Web → Core** - Request completo desde widget hasta respuesta
- ✅ **Flujo Crawler → Core** - Desde indexing hasta búsqueda
- ✅ **Orquestación de Services** - Coordinación completa de todos los servicios
- ✅ **Streaming E2E** - Streaming completo desde core hasta web
- ✅ **Sesiones concurrentes** - Múltiples usuarios simultáneos
- ✅ **Recuperación de errores** - Sistema funcionando con fallos parciales
- ✅ **Performance E2E** - Rendimiento del sistema completo

#### **Escenarios de Test:**
- Usuario pregunta sobre onboarding desde widget web
- Sistema encuentra documentos indexados por crawler
- Core procesa usando configuración de utils
- LLM genera respuesta con citaciones
- Response streaming hacia widget web
- Múltiples sesiones concurrentes
- Sistema funciona con servicios parcialmente disponibles

#### **Markers de Pytest:**
```python
@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.slow        # Tests que tardan más tiempo
@pytest.mark.external    # Requieren servicios externos
@pytest.mark.docker      # Requieren entorno Docker
@pytest.mark.performance # Tests de rendimiento
```

---

## 💻 Cómo Ejecutar los Tests de Integración

### **Comandos Básicos**

```powershell
# Desde el directorio meribot/core/
cd meribot_app/meribot/core

# Ejecutar todos los tests de integración
pytest test/integracion/ -v

# Ejecutar un archivo específico
pytest test/integracion/test_core_crawler_integration.py -v

# Ejecutar con output detallado
pytest test/integracion/ -v -s
```

### **Ejecución por Categorías**

```powershell
# Tests de integración general
pytest test/integracion/ -m "integration" -v

# Tests específicos por módulo
pytest test/integracion/ -m "integration and crawler" -v
pytest test/integracion/ -m "integration and web" -v
pytest test/integracion/ -m "integration and services" -v
pytest test/integracion/ -m "integration and utils" -v

# Tests end-to-end
pytest test/integracion/ -m "integration and e2e" -v

# Tests que requieren servicios externos
pytest test/integracion/ -m "integration and external" -v

# Tests lentos (excluir para desarrollo rápido)
pytest test/integracion/ -m "integration and not slow" -v
```

### **Ejecución Combinada (Unitarios + Integración)**

```powershell
# Ejecutar todos los tests (unitarios + integración)
pytest test/ -v

# Con coverage completo
pytest test/ --cov=. --cov-report=html -v

# Solo integración con coverage
pytest test/integracion/ --cov=. --cov-report=term-missing -v
```

### **Ejecución Paralela**

```powershell
# Instalar pytest-xdist para paralelización
pip install pytest-xdist

# Ejecutar tests de integración en paralelo
pytest test/integracion/ -n auto -v
```

---

## 🔧 Configuración Específica para Integración

### **Markers Adicionales en pytest.ini**

```ini
markers =
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end integration tests
    crawler: marks tests as crawler integration related
    web: marks tests as web module integration related
    services: marks tests as services module integration related
    utils: marks tests as utils module integration related
    external: marks tests that require external services
    docker: marks tests that require Docker environment
    slow: marks tests as slow (deselect with '-m "not slow"')
    performance: marks tests as performance related
```

### **Fixtures de Integración**

Definidas en `conftest.py`:
- `integration_config`: Configuración base para integración
- `mock_crawler_service`: Mock del servicio de crawler
- `mock_web_client`: Cliente web para tests
- `integration_test_documents`: Documentos de ejemplo
- `mock_services_integration`: Mock de todos los servicios
- `integration_chat_engine`: ChatEngine configurado para integración

### **Variables de Entorno para Tests de Integración**

```env
# Configuración de test de integración
TESTING=true
INTEGRATION_TEST=true
LOG_LEVEL=DEBUG
ENVIRONMENT=integration_test

# Servicios externos para tests
AZURE_OPENAI_ENDPOINT=mock://localhost
AZURE_OPENAI_API_KEY=mock_integration_key
CHROMA_PERSIST_DIRECTORY=./integration_test_chroma_data

# Configuración de timeouts para integración
REQUEST_TIMEOUT=30
LLM_TIMEOUT=60
```

---

## 📊 Métricas de Tests de Integración

| Métrica | Valor |
|---------|-------|
| **Archivos de integración** | 5 archivos especializados |
| **Tests de integración** | ~80+ métodos de test |
| **Módulos integrados** | Core + 4 módulos externos |
| **Workflows E2E** | 8 workflows completos |
| **Markers personalizados** | 9 markers específicos |
| **Fixtures de integración** | 6 fixtures especializadas |
| **Cobertura de módulos** | 100% de módulos MeriBot |

---

## 🗂️ Descripción Detallada por Archivo

### **test_core_crawler_integration.py**
- **Propósito**: Validar integración entre Core y módulo Crawler
- **Tests principales**: 15+ tests de configuración, validación, búsqueda
- **Cobertura**: Config YAML, validación dominios, ChromaDB, metadatos
- **Dependencias**: Crawler config, document loader, chroma integration

### **test_core_web_integration.py**
- **Propósito**: Validar integración entre Core y módulo Web
- **Tests principales**: 18+ tests de API, CORS, streaming, formato
- **Cobertura**: Endpoints, requests/responses, sesiones, archivos estáticos
- **Dependencias**: FastAPI TestClient, widget web, CORS middleware

### **test_core_services_integration.py**
- **Propósito**: Validar integración entre Core y módulo Services
- **Tests principales**: 16+ tests de servicios, orquestación, datos
- **Cobertura**: ChromaDB service, crawler service, process docs, monitoring
- **Dependencias**: Services endpoints, storage integration, auth

### **test_core_utils_integration.py**
- **Propósito**: Validar integración entre Core y módulo Utils
- **Tests principales**: 14+ tests de utilidades, config, logging
- **Cobertura**: Config loader, logger, system prompt, hash utils, env vars
- **Dependencias**: Utils functions, logging system, environment config

### **test_end_to_end_integration.py**
- **Propósito**: Validar workflows completos end-to-end
- **Tests principales**: 12+ tests de scenarios completos
- **Cobertura**: Workflows reales, performance, recuperación de errores
- **Dependencias**: Todos los módulos integrados

---

## 🛠️ Mantenimiento y Extensión

### **Añadir Nuevos Tests de Integración**

1. **Crear archivo de test** en `test/integracion/`
2. **Usar fixtures de integración** desde `conftest.py`
3. **Aplicar markers apropiados** (`@pytest.mark.integration`, etc.)
4. **Mockear servicios externos** apropiadamente
5. **Documentar escenarios** de integración

### **Actualizar Fixtures de Integración**

1. **Modificar `conftest.py`** para nuevas dependencias
2. **Mantener compatibilidad** con tests existentes
3. **Agregar configuración** para nuevos módulos
4. **Actualizar documentación** de fixtures

### **Debugging de Tests de Integración**

```powershell
# Ejecutar con debug verbose
pytest test/integracion/ -v -s --tb=long

# Ejecutar un test específico con debug
pytest test/integracion/test_core_crawler_integration.py::TestCoreCrawlerIntegration::test_core_uses_crawler_config_validation -v -s

# Ver logs durante ejecución
pytest test/integracion/ -v -s --log-cli-level=DEBUG
```

---

## 🚀 Integración Continua

### **Pipeline de CI/CD**

```yaml
# Ejemplo de configuración CI/CD para integración
- name: Run Integration Tests
  run: |
    cd meribot_app/meribot/core
    
    # Tests de integración básicos (sin servicios externos)
    pytest test/integracion/ -m "integration and not external" --cov=. --cov-report=xml -v
    
    # Tests con servicios (solo si están disponibles)
    pytest test/integracion/ -m "integration and external" -v || echo "External services not available"
    
    # Tests E2E (en entorno staging)
    pytest test/integracion/ -m "integration and e2e" -v
```

### **Tests en Entornos**

- **Desarrollo**: Tests de integración sin servicios externos
- **Staging**: Tests completos incluyendo servicios externos
- **Producción**: Tests E2E de smoke testing

---

## 📈 Resultados y Beneficios

### **Calidad de Integración**
- ✅ **Validación de interfaces** - Contratos entre módulos verificados
- ✅ **Detección de problemas** - Issues de integración detectados temprano
- ✅ **Workflows reales** - Escenarios de usuario validados
- ✅ **Regresión prevention** - Cambios no rompen integraciones

### **Confianza en Despliegues**
- ✅ **Deploy seguro** - Integración validada antes de producción
- ✅ **Rollback confiable** - Tests verifican funcionalidad después de rollback
- ✅ **Feature flags** - Nuevas features validadas en integración
- ✅ **Performance baseline** - Rendimiento de integración monitoreado

### **Productividad del Equipo**
- ✅ **Desarrollo paralelo** - Equipos pueden desarrollar módulos independientemente
- ✅ **Debugging eficiente** - Issues localizados a nivel de integración
- ✅ **Onboarding rápido** - Nuevos desarrolladores entienden integraciones
- ✅ **Documentación viva** - Tests como especificación de integración

---

## 🎯 Escenarios de Integración Cubiertos

### **Escenarios de Usuario Real**

1. **Nuevo Empleado Consulta Onboarding**
   - Usuario abre widget web
   - Pregunta sobre proceso de onboarding
   - Core busca en documentos indexados por crawler
   - Core genera respuesta usando utils y LLM
   - Widget muestra respuesta con citaciones

2. **Administrador Inicia Crawling**
   - Administrador usa API para iniciar crawling
   - Crawler procesa documentos nuevos
   - Services indexa contenido en ChromaDB
   - Core puede buscar nuevo contenido inmediatamente

3. **Usuario Múltiples Preguntas**
   - Usuario mantiene conversación en widget
   - Core mantiene contexto usando conversation manager
   - Cada respuesta usa información actualizada
   - Session persiste hasta que usuario cierra

4. **Sistema Bajo Carga**
   - Múltiples usuarios concurrentes
   - Core maneja sesiones independientes
   - Services procesan requests en paralelo
   - Performance se mantiene aceptable

### **Escenarios de Error y Recuperación**

1. **ChromaDB Temporalmente No Disponible**
   - Core detecta fallo de ChromaDB
   - Core continúa funcionando sin búsqueda vectorial
   - Core retorna respuesta basada solo en LLM
   - Sistema se recupera cuando ChromaDB vuelve

2. **LLM API Con Problemas**
   - Core detecta timeout del LLM
   - Core retorna mensaje de error apropiado
   - Core registra fallo para monitoreo
   - Usuario recibe respuesta informativa

3. **Configuración Corrupta**
   - Utils detecta configuración inválida
   - Core usa valores por defecto
   - Sistema registra warning
   - Funcionalidad básica se mantiene

---

## 🎉 Conclusión

La suite de **tests de integración** para MeriBot Core proporciona:

- **Cobertura completa** de integraciones entre módulos
- **Validación de workflows** reales de usuario
- **Detección temprana** de problemas de integración
- **Confianza en despliegues** con validación automatizada
- **Documentación viva** de cómo interactúan los módulos

Con **80+ tests de integración** organizados en **5 archivos especializados**, el sistema MeriBot está preparado para:

- **Desarrollo escalable** con múltiples equipos
- **Integración continua** con validación automática
- **Deploy confiable** en cualquier entorno
- **Mantenimiento eficiente** con detección proactiva de issues

Los tests están **listos para ejecutarse** y pueden integrarse inmediatamente en cualquier pipeline de CI/CD para asegurar la calidad continua de las integraciones.

---

**📝 Generado el:** 18 de Septiembre, 2025  
**🤖 Framework:** pytest 8.4.1+ con soporte integración  
**📦 Componente:** MeriBot Integration Testing Suite  
**✅ Estado:** Completo y listo para CI/CD