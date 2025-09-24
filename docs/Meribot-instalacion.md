# 🚀 Guía de Instalación de MeriBot

## 📋 Tabla de Contenidos

1. [Información General](#información-general)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Configuración](#configuración)
5. [Verificación de la Instalación](#verificación-de-la-instalación)
6. [Ejecución del Sistema](#ejecución-del-sistema)
7. [Solución de Problemas](#solución-de-problemas)
8. [Configuración Avanzada](#configuración-avanzada)

---

## 📖 Información General

MeriBot es un **asistente conversacional empresarial** desarrollado para C&CA que utiliza tecnologías de inteligencia artificial para proporcionar respuestas contextuales basadas en documentación corporativa. Este documento proporciona instrucciones detalladas para la instalación y configuración del sistema.

### 🎯 Componentes Principales
- **Backend API**: FastAPI con integración a Azure OpenAI
- **Base de Datos Vectorial**: ChromaDB para búsqueda semántica
- **Crawler de Documentos**: Sistema de extracción y procesamiento
- **Widget Web**: Interfaz de usuario embebible
- **CLI de Administración**: Herramientas de gestión (meri-cli)

---

## 💻 Requisitos del Sistema

### 📋 Requisitos Mínimos

#### **Sistema Operativo**
- Windows 10/11 (recomendado)
- macOS 10.15+ 
- Linux Ubuntu 20.04+ / CentOS 8+

#### **Hardware**
- **CPU**: 2+ cores, 2.0+ GHz
- **RAM**: 4GB mínimo, 8GB recomendado
- **Almacenamiento**: 5GB espacio libre
- **Red**: Conexión a internet para Azure OpenAI

#### **Software Base**
- **Python**: 3.12 o superior (OBLIGATORIO)
- **Git**: Para clonado del repositorio
- **PowerShell**: Para scripts de Windows (incluido en Windows)

#### **Opcional (Desarrollo)**
- **Node.js**: 16+ (solo para desarrollo del widget)
- **Docker**: Para despliegue en contenedores
- **Visual Studio Code**: IDE recomendado

### 🔑 Servicios Externos Requeridos

#### **Azure OpenAI** (OBLIGATORIO)
- Acceso a Azure OpenAI Service
- Deployment de GPT-4 configurado
- Deployment de embeddings text-embedding-3-large
- API Key válida

#### **Credenciales Necesarias**
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT`

---

## 🛠️ Instalación Paso a Paso

### **Paso 1: Preparación del Entorno**

#### **1.1 Verificar Python**
```powershell
# Verificar versión de Python (debe ser 3.12+)
python --version

# Si no tienes Python 3.12+, descarga desde:
# https://www.python.org/downloads/
```

#### **1.2 Instalar Git** (si no está instalado)
```powershell
# Windows: Descargar desde https://git-scm.com/download/win
# macOS: xcode-select --install
# Linux: sudo apt install git
git --version
```

#### **1.3 Crear Directorio de Trabajo**
```powershell
# Crear directorio para el proyecto
mkdir C:\MeriBot
cd C:\MeriBot
```

### **Paso 2: Clonado del Repositorio**

```powershell
# Clonar el repositorio
git clone https://github.com/ThePhrontistery/meri-bot.git

# Navegar al directorio de la aplicación
cd meri-bot\meribot_app

# Verificar estructura del proyecto
dir
```

**Estructura esperada:**
```
meribot_app/
├── meribot/                 # Código fuente principal
├── requirements.txt         # Dependencias Python
├── crawler_config.yaml      # Configuración del crawler
├── pytest.ini             # Configuración de tests
└── ...
```

### **Paso 3: Configuración del Entorno Virtual**

#### **Opción A: Usando pip (Tradicional)**
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
# venv\Scripts\activate.bat

# macOS/Linux:
# source venv/bin/activate

# Verificar activación (debe mostrar (venv) al inicio)
```

#### **Opción B: Usando uv (Recomendado)**
```powershell
# Instalar uv (solo la primera vez)
pip install uv

# Crear y activar entorno automáticamente
uv sync

# uv creará automáticamente el entorno y instalará todas las dependencias
```

### **Paso 4: Instalación de Dependencias**

#### **Si usas pip:**
```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

#### **Si usas uv:**
```powershell
# Las dependencias ya se instalaron con 'uv sync'
# Para añadir nuevas dependencias:
uv add nombre_paquete

# Para actualizar dependencias:
uv sync --upgrade
```

### **Paso 5: Verificación de Instalación Base**

```powershell
# Verificar que las dependencias principales están instaladas
python -c "import fastapi, chromadb, langchain; print('✅ Dependencias principales OK')"

# Verificar estructura del módulo
python -c "import meribot; print('✅ Módulo MeriBot importado correctamente')"
```

---

## ⚙️ Configuración

### **Paso 1: Configurar Variables de Entorno**

#### **1.1 Crear archivo .env**
```powershell
# Crear archivo .env en la raíz del proyecto (meribot_app/)
New-Item -Name ".env" -ItemType File
```

#### **1.2 Configurar variables obligatorias**
Edita el archivo `.env` con un editor de texto y añade:

```env
# ===== CONFIGURACIÓN AZURE OPENAI (OBLIGATORIO) =====
AZURE_OPENAI_API_KEY=tu_api_key_aqui
AZURE_OPENAI_ENDPOINT=https://tu-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-large
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# ===== CONFIGURACIÓN DE LA APLICACIÓN =====
MERIBOT_LOG_LEVEL=INFO
MERIBOT_LOG_FILE=logs/meribot_core.log
MERIBOT_LOG_MAX_BYTES=1048576
MERIBOT_LOG_BACKUP_COUNT=5

# ===== CONFIGURACIÓN CHROMADB =====
CHROMA_PERSIST_DIRECTORY=chroma_data
CHROMA_COLLECTION_NAME=meri_chunks

# ===== CONFIGURACIÓN LLM =====
LLM_MODEL=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=1000

# ===== CONFIGURACIÓN CRAWLER =====
MERIBOT_CRAWLER_URL=http://localhost:8000
CRAWLER_MAX_DEPTH=4
CRAWLER_DELAY=1
CRAWLER_USER_AGENT=MeriBot/1.0

# ===== OTROS =====
TESTING=false
```

### **Paso 2: Configurar Crawler**

El archivo `crawler_config.yaml` debe estar presente. Verificar y ajustar:

```powershell
# Verificar que existe el archivo de configuración
Get-Content crawler_config.yaml
```

**Contenido esperado de `crawler_config.yaml`:**
```yaml
seeds:
  - "https://cca.capgemini.com/web/home"

allowed_domains:
  - "cca"
  - "onboarding"
  - "training"

max_depth: 4
delay_between_requests: 1

file_types:
  - "html"
  - "pdf"
  - "docx"
  - "xlsx"

chunk_size: 800
chunk_overlap: 50
min_chunk_length: 20

exclude_patterns:
  - "*.js"
  - "*.css"
  - "**/admin/**"

user_agent: "MeriBot/1.0 (+https://cca.capgemini.com/meribot)"
```

### **Paso 3: Crear Directorios Necesarios**

```powershell
# Crear directorios para datos y logs
New-Item -ItemType Directory -Path "logs" -Force
New-Item -ItemType Directory -Path "chroma_data" -Force
New-Item -ItemType Directory -Path "data\scraped" -Force

# Verificar estructura
Get-ChildItem -Directory
```

---

## ✅ Verificación de la Instalación

### **Prueba 1: Verificar Importaciones**
```powershell
python -c "
import sys
print('Python:', sys.version)

try:
    import meribot
    print('✅ MeriBot module: OK')
except ImportError as e:
    print('❌ MeriBot module:', e)

try:
    import fastapi
    print('✅ FastAPI:', fastapi.__version__)
except ImportError as e:
    print('❌ FastAPI:', e)

try:
    import chromadb
    print('✅ ChromaDB:', chromadb.__version__)
except ImportError as e:
    print('❌ ChromaDB:', e)

try:
    import langchain
    print('✅ LangChain: OK')
except ImportError as e:
    print('❌ LangChain:', e)
"
```

### **Prueba 2: Verificar Configuración**
```powershell
# Verificar que las variables de entorno se cargan correctamente
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'AZURE_OPENAI_API_KEY',
    'AZURE_OPENAI_ENDPOINT',
    'AZURE_OPENAI_DEPLOYMENT_NAME',
]

print('Verificando variables de entorno...')
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f'✅ {var}: Configurada')
    else:
        print(f'❌ {var}: NO CONFIGURADA')
"
```

### **Prueba 3: Test de Conectividad Azure OpenAI**
```powershell
# Test básico de conectividad (requiere API key válida)
python -c "
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_key = os.getenv('AZURE_OPENAI_API_KEY')

if endpoint and api_key:
    try:
        # Test simple de conectividad
        response = httpx.get(f'{endpoint.rstrip(\"/\")}/openai/deployments?api-version=2024-02-01', headers={'api-key': api_key}, timeout=10)
        if response.status_code == 200:
            print('✅ Conectividad Azure OpenAI: OK')
        else:
            print(f'⚠️  Azure OpenAI responde pero con código: {response.status_code}')
    except Exception as e:
        print(f'❌ Error conectividad Azure OpenAI: {e}')
else:
    print('❌ Credenciales de Azure OpenAI no configuradas')
"
```

### **Prueba 4: Verificar CLI**
```powershell
# Verificar que meri-cli funciona
python -m meribot.meri-cli --help
```

---

## 🚦 Ejecución del Sistema

### **Opción 1: Desarrollo (Recomendado para Testing)**

#### **1.1 Iniciar el Backend API**
```powershell
# Terminal 1: Iniciar servidor FastAPI con recarga automática
uvicorn meribot.core.api.app:app --reload --host 0.0.0.0 --port 8000

# El servidor estará disponible en:
# - API: http://localhost:8000
# - Documentación: http://localhost:8000/docs
# - Health check: http://localhost:8000/chatbot/health
```

#### **1.2 Verificar que la API está funcionando**
```powershell
# En otro terminal, verificar endpoint de salud
curl http://localhost:8000/chatbot/health

# O usando PowerShell:
Invoke-RestMethod -Uri "http://localhost:8000/chatbot/health" -Method Get
```

#### **1.3 Iniciar el Widget Web (Opcional)**
```powershell
# Terminal 2: Servir archivos estáticos del widget
cd web
python -m http.server 3000

# Widget disponible en: http://localhost:3000
```

### **Opción 2: Producción**

```powershell
# Servidor de producción con múltiples workers
uvicorn meribot.core.api.app:app --host 0.0.0.0 --port 8000 --workers 4

# O usando Gunicorn (en Linux/macOS):
# gunicorn meribot.core.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Prueba de Funcionamiento Completo**

#### **Test 1: Endpoint de Salud**
```powershell
# Verificar que la API responde
curl http://localhost:8000/chatbot/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "meribot-chatbot",
  "version": "1.0.0"
}
```

#### **Test 2: Test de Query** (requiere datos)
```powershell
# Hacer una consulta de prueba
curl -X POST "http://localhost:8000/chatbot/query" ^
     -H "Content-Type: application/json" ^
     -d "{\"message\":\"Hola\",\"conversation_id\":\"test-123\"}"
```

#### **Test 3: CLI de Administración**
```powershell
# Verificar comandos del CLI
python -m meribot.meri-cli db count
python -m meribot.meri-cli --help
```

---

## 🔧 Solución de Problemas

### **Problema 1: Error de Importación de Módulos**

**Error:** `ModuleNotFoundError: No module named 'meribot'`

**Solución:**
```powershell
# Verificar que estás en el directorio correcto
pwd
# Debe mostrar: .../meri-bot/meribot_app

# Verificar que el entorno virtual está activado
python -c "import sys; print(sys.prefix)"

# Reinstalar en modo desarrollo
pip install -e .
```

### **Problema 2: Error de Permisos en PowerShell**

**Error:** `execution of scripts is disabled on this system`

**Solución:**
```powershell
# Cambiar política de ejecución temporalmente (como administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# O activar el entorno de otra forma:
venv\Scripts\activate.bat
```

### **Problema 3: Error de Conexión Azure OpenAI**

**Error:** `Azure OpenAI connection failed`

**Soluciones:**
1. **Verificar credenciales:**
   ```powershell
   # Mostrar variables (sin mostrar la clave completa)
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Endpoint:', os.getenv('AZURE_OPENAI_ENDPOINT')); print('Key starts with:', os.getenv('AZURE_OPENAI_API_KEY', '')[:10] + '...' if os.getenv('AZURE_OPENAI_API_KEY') else 'NOT SET')"
   ```

2. **Verificar conectividad de red:**
   ```powershell
   # Test de conectividad básica
   Test-NetConnection tu-endpoint.openai.azure.com -Port 443
   ```

3. **Verificar formato del endpoint:**
   - Debe terminar con `/` o sin `/`
   - Formato: `https://tu-recurso.openai.azure.com/`

### **Problema 4: ChromaDB Issues**

**Error:** `ChromaDB connection issues`

**Solución:**
```powershell
# Limpiar datos de ChromaDB
Remove-Item -Recurse -Force chroma_data -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "chroma_data" -Force

# Reiniciar la aplicación
```

### **Problema 5: Puerto en Uso**

**Error:** `Address already in use`

**Solución:**
```powershell
# Encontrar proceso usando puerto 8000
netstat -ano | findstr :8000

# Terminar proceso (reemplazar PID)
taskkill /PID <PID> /F

# O usar otro puerto
uvicorn meribot.core.api.app:app --port 8001
```

### **Problema 6: Dependencias Desactualizadas**

**Solución:**
```powershell
# Con pip:
pip install --upgrade -r requirements.txt

# Con uv:
uv sync --upgrade
```

---

## 🔧 Configuración Avanzada

### **Configuración para Desarrollo**

#### **Setup IDE (Visual Studio Code)**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "100"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/chroma_data": true
    }
}
```

#### **Pre-commit Hooks**
```powershell
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

### **Configuración Docker (Opcional)**

#### **Dockerfile**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "meribot.core.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **docker-compose.yml**
```yaml
version: '3.8'
services:
  meribot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
    volumes:
      - ./chroma_data:/app/chroma_data
      - ./logs:/app/logs
    restart: unless-stopped
```

#### **Comandos Docker:**
```powershell
# Construir imagen
docker build -t meribot .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env meribot

# Usando docker-compose
docker-compose up -d
```

### **Configuración de Logging Avanzado**

```env
# Variables adicionales para logging
MERIBOT_LOG_FORMAT=json
MERIBOT_LOG_ROTATION=daily
MERIBOT_LOG_RETENTION_DAYS=30
MERIBOT_LOG_INCLUDE_SENSITIVE=false
```

### **Configuración de Rendimiento**

```env
# Configuración de rendimiento
UVICORN_WORKERS=4
UVICORN_MAX_REQUESTS=1000
CHROMADB_POOL_SIZE=10
AZURE_OPENAI_TIMEOUT=30
CONVERSATION_TIMEOUT=3600
```

### **Configuración de Seguridad**

```env
# Variables de seguridad
CORS_ORIGINS=https://cca.capgemini.com,https://localhost:3000
RATE_LIMIT_PER_MINUTE=60
MAX_MESSAGE_LENGTH=2000
ENABLE_API_DOCS=false  # Para producción
```

---

## 📞 Soporte y Recursos

### **Enlaces Útiles**
- **Repositorio**: https://github.com/ThePhrontistery/meri-bot
- **Documentación**: [docs/](../docs/)
- **Issues**: https://github.com/ThePhrontistery/meri-bot/issues

### **Comandos de Referencia Rápida**

```powershell
# Verificar instalación
python --version
python -c "import meribot; print('OK')"

# Activar entorno
.\venv\Scripts\Activate.ps1

# Iniciar desarrollo
uvicorn meribot.core.api.app:app --reload

# CLI administrativo
python -m meribot.meri-cli --help

# Tests
pytest

# Logs
Get-Content logs\meribot_core.log -Tail 20
```

### **Lista de Verificación Post-Instalación**

- [ ] Python 3.12+ instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Azure OpenAI credentials válidas
- [ ] Directorios de datos creados
- [ ] API iniciada correctamente (puerto 8000)
- [ ] Health check responde OK
- [ ] CLI funciona correctamente
- [ ] Widget web accesible (opcional)

