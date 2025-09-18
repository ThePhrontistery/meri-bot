# 📋 Tests Unitarios - MeriBot Core Component

## 🎯 Propósito

Este documento describe la suite completa de tests unitarios generados para el **componente core de MeriBot**. Los tests fueron diseñados con **pytest** para validar el correcto funcionamiento de todos los módulos principales del sistema, asegurando la calidad, escalabilidad y mantenibilidad del código.

---

## 📁 Estructura de Tests Creada

```
meribot/core/test/
├── conftest.py                         # Configuración central y fixtures compartidas
├── pytest.ini                         # Configuración de pytest y markers
└── unitarios/
    ├── test_api_app.py                # Tests para API FastAPI
    ├── test_conversation_context.py    # Tests para contexto de conversación
    ├── test_conversation_manager.py    # Tests para gestor de conversaciones
    ├── test_chromadb_connector.py     # Tests para vector database
    ├── test_llm_provider.py           # Tests para proveedor Azure OpenAI
    ├── test_llm_engine.py             # Tests para motor LLM
    ├── test_plugin_manager.py         # Tests para gestor de plugins
    ├── test_base_plugin.py            # Tests para clase base de plugins
    ├── test_validation.py             # Tests para validación Pydantic
    └── test_chatengine.py             # Tests para orquestador principal
```

---

## 🎯 Cobertura Funcional Completa

### **1. API Layer (test_api_app.py)**
- ✅ **Endpoints `/generate` y `/stream`** - Validación de endpoints principales
- ✅ **Validación de requests y responses** - Esquemas Pydantic y formato JSON
- ✅ **Manejo de errores y CORS** - Respuestas HTTP correctas y políticas CORS
- ✅ **Timeouts y casos edge** - Comportamiento bajo estrés y límites

### **2. Conversation Management**
- ✅ **Gestión de sesiones y contexto** - Creación, recuperación y manejo de sesiones
- ✅ **Historial de mensajes** - Almacenamiento y recuperación del historial
- ✅ **Cleanup de sesiones** - Limpieza apropiada de recursos

### **3. Vector Database (test_chromadb_connector.py)**
- ✅ **Búsquedas de similaridad** - Queries vectoriales y ranking de resultados
- ✅ **Filtrado por dominios** - Segmentación de contenido por dominio
- ✅ **Manejo de embeddings** - Generación y procesamiento de vectores

### **4. LLM Integration**
- ✅ **Integración Azure OpenAI** - Comunicación con API de Azure
- ✅ **Streaming de respuestas** - Generación de tokens en tiempo real
- ✅ **Manejo de errores y timeouts** - Resiliencia ante fallos de red

### **5. Plugin System**
- ✅ **Registro y activación de plugins** - Ciclo de vida de plugins
- ✅ **Interfaz abstracta** - Cumplimiento del contrato BasePlugin
- ✅ **Manejo de errores en plugins** - Aislamiento de fallos

### **6. Validation Layer**
- ✅ **Validación Pydantic** - Esquemas de datos y tipos
- ✅ **Sanitización de inputs** - Limpieza y normalización
- ✅ **Detección de patrones peligrosos** - Seguridad en inputs

### **7. Core Orchestrator (test_chatengine.py)**
- ✅ **Flujo completo de procesamiento** - Integración end-to-end
- ✅ **Integración de todos los componentes** - Orquestación de módulos
- ✅ **Manejo de citaciones** - Generación y deduplicación de referencias
- ✅ **Streaming y procesamiento concurrente** - Rendimiento asíncrono

---

## 🚀 Características Técnicas

### **Mocking Avanzado**
- **Mock completo de dependencias externas** - Azure OpenAI, ChromaDB, archivos
- **Fixtures reutilizables** - Configuración compartida entre tests
- **Async/await testing** - Soporte completo para código asíncrono

### **Pytest Features**
- **Markers personalizados** - `@pytest.mark.unit`, `@pytest.mark.llm`, `@pytest.mark.asyncio`
- **Parametrización de tests** - Ejecución con múltiples casos de datos
- **Fixtures compartidas** - Configuración centralizada en `conftest.py`

### **Error Scenarios**
- **Timeouts y conexiones fallidas** - Resiliencia de red
- **Errores de validación** - Manejo de inputs incorrectos
- **Excepciones del LLM** - Recuperación ante fallos de IA
- **Fallos de la base de datos** - Continuidad ante problemas de persistencia

### **Edge Cases**
- **Mensajes vacíos** - Validación de inputs mínimos
- **Dominios None** - Manejo de filtros opcionales
- **Resultados vacíos** - Comportamiento sin datos
- **Caracteres unicode** - Soporte internacional completo

---

## 💻 Cómo Ejecutar los Tests

### **Comandos Básicos**

```powershell
# Desde el directorio meribot/core/
cd meribot_app/meribot/core

# Ejecutar todos los tests unitarios
pytest test/unitarios/ -v

# Ejecutar un archivo específico
pytest test/unitarios/test_chatengine.py -v

# Ejecutar tests con output detallado
pytest test/unitarios/ -v -s
```

### **Ejecución por Categorías**

```powershell
# Tests de unidad general
pytest test/unitarios/ -m "unit" -v

# Tests específicos de LLM
pytest test/unitarios/ -m "llm" -v

# Tests asíncronos
pytest test/unitarios/ -m "asyncio" -v

# Tests de API
pytest test/unitarios/ -m "api" -v
```

### **Con Coverage**

```powershell
# Instalar coverage si no está disponible
pip install pytest-cov

# Ejecutar con reporte de cobertura
pytest test/unitarios/ --cov=. --cov-report=html

# Ver reporte en consola
pytest test/unitarios/ --cov=. --cov-report=term-missing
```

### **Ejecución Paralela**

```powershell
# Instalar pytest-xdist para paralelización
pip install pytest-xdist

# Ejecutar tests en paralelo
pytest test/unitarios/ -n auto -v
```

---

## 📊 Métricas del Test Suite

| Métrica | Valor |
|---------|-------|
| **Total de archivos de test** | 10 archivos |
| **Total de métodos de test** | ~150+ métodos |
| **Cobertura de módulos** | Todos los módulos del core |
| **Soporte async** | Completo |
| **Estrategia de mocking** | Comprehensive |
| **Markers personalizados** | 4 markers |
| **Fixtures compartidas** | 15+ fixtures |

---

## 🗂️ Descripción Detallada por Archivo

### **conftest.py**
- **Propósito**: Configuración central de pytest y fixtures compartidas
- **Fixtures principales**: `mock_azure_openai`, `mock_chroma_client`, `mock_conversation_session`
- **Configuración**: Logging, async support, environment setup

### **pytest.ini**
- **Propósito**: Configuración de pytest, markers y opciones de ejecución
- **Markers definidos**: `unit`, `integration`, `llm`, `api`, `asyncio`
- **Configuración**: Test discovery, async mode, warning filters

### **test_api_app.py**
- **Módulo objetivo**: `meribot.core.api.app`
- **Tests principales**: Endpoints FastAPI, CORS, validación de requests
- **Cobertura**: 25+ test methods, manejo de errores HTTP

### **test_conversation_context.py**
- **Módulo objetivo**: `meribot.core.conversation.conversation_context`
- **Tests principales**: Gestión de historial, adición de mensajes
- **Cobertura**: 15+ test methods, persistencia de contexto

### **test_conversation_manager.py**
- **Módulo objetivo**: `meribot.core.conversation.conversation_manager`
- **Tests principales**: Sesiones, cleanup, concurrencia
- **Cobertura**: 20+ test methods, gestión de recursos

### **test_chromadb_connector.py**
- **Módulo objetivo**: `meribot.core.db.chromadb_connector`
- **Tests principales**: Búsquedas vectoriales, filtrado, embeddings
- **Cobertura**: 20+ test methods, operaciones de base de datos

### **test_llm_provider.py**
- **Módulo objetivo**: `meribot.core.llm.llm_provider`
- **Tests principales**: Integración Azure OpenAI, streaming, manejo de errores
- **Cobertura**: 25+ test methods, comunicación con API

### **test_llm_engine.py**
- **Módulo objetivo**: `meribot.core.llm.llm_engine`
- **Tests principales**: Orquestación LLM, construcción de prompts
- **Cobertura**: 20+ test methods, lógica de negocio

### **test_plugin_manager.py**
- **Módulo objetivo**: `meribot.core.plugins.plugin_manager`
- **Tests principales**: Registro de plugins, ejecución, manejo de errores
- **Cobertura**: 15+ test methods, sistema de plugins

### **test_base_plugin.py**
- **Módulo objetivo**: `meribot.core.plugins.base_plugin`
- **Tests principales**: Interfaz abstracta, implementación de contrato
- **Cobertura**: 10+ test methods, validación de interfaz

### **test_validation.py**
- **Módulo objetivo**: `meribot.core.validation`
- **Tests principales**: Validación Pydantic, sanitización, seguridad
- **Cobertura**: 25+ test methods, casos edge y seguridad

### **test_chatengine.py**
- **Módulo objetivo**: `meribot.core.chatengine`
- **Tests principales**: Orquestación completa, integración de componentes
- **Cobertura**: 30+ test methods, flujo end-to-end

---

## 🔧 Configuración de Desarrollo

### **Dependencias de Testing**

```bash
# Dependencias principales
pip install pytest>=8.0.0
pip install pytest-asyncio>=0.21.0
pip install pytest-cov>=4.0.0
pip install pytest-xdist>=3.0.0

# Para mocking avanzado
pip install pytest-mock>=3.10.0
```

### **Variables de Entorno para Tests**

```env
# Configuración de test
TESTING=true
LOG_LEVEL=DEBUG
ENVIRONMENT=test

# Mocks de servicios externos
AZURE_OPENAI_ENDPOINT=mock://localhost
AZURE_OPENAI_API_KEY=mock_key
CHROMA_PERSIST_DIRECTORY=./test_chroma_data
```

---

## 🛠️ Mantenimiento y Extensión

### **Añadir Nuevos Tests**

1. **Crear archivo de test** en `test/unitarios/`
2. **Importar fixtures** necesarias desde `conftest.py`
3. **Usar markers apropiados** (`@pytest.mark.unit`, etc.)
4. **Seguir convenciones de naming** (`test_*`)

### **Actualizar Fixtures**

1. **Modificar `conftest.py`** para nuevas dependencias
2. **Mantener retrocompatibilidad** con tests existentes
3. **Documentar cambios** en fixtures compartidas

### **Integración Continua**

```yaml
# Ejemplo de configuración CI/CD
- name: Run Unit Tests
  run: |
    cd meribot_app/meribot/core
    pytest test/unitarios/ --cov=. --cov-report=xml -v
```

---

## 📈 Resultados y Beneficios

### **Calidad del Código**
- ✅ **Detección temprana de errores** - Tests automáticos en cada cambio
- ✅ **Refactoring seguro** - Confianza para modificar código
- ✅ **Documentación viva** - Tests como especificación

### **Productividad del Equipo**
- ✅ **Onboarding rápido** - Tests como guía de funcionalidad
- ✅ **Debugging eficiente** - Aislamiento de problemas
- ✅ **Deploy confiable** - Validación antes de producción

### **Mantenibilidad**
- ✅ **Cobertura completa** - Todos los módulos testeados
- ✅ **Casos edge cubiertos** - Comportamiento en límites
- ✅ **Mocking profesional** - Aislamiento de dependencias

---

## 🎯 Conclusión

El test suite generado para el **componente core de MeriBot** proporciona una **cobertura completa y profesional** de toda la funcionalidad del sistema. Con **más de 150 tests** organizados en **10 archivos especializados**, el sistema está preparado para:

- **Desarrollo confiable** con detección temprana de errores
- **Refactoring seguro** con validación automática
- **Escalabilidad futura** con arquitectura de tests extensible
- **Calidad empresarial** con estándares profesionales de testing

Los tests están **listos para ejecutarse** y pueden integrarse inmediatamente en cualquier pipeline de CI/CD para asegurar la calidad continua del código.

---

**📝 Generado el:** 18 de Septiembre, 2025  
**🤖 Framework:** pytest 8.4.1+ con soporte asyncio  
**📦 Componente:** MeriBot Core Component  
**✅ Estado:** Completo y listo para producción