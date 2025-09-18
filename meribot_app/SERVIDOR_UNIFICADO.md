# 🚀 MeriBot Server - Guía de Inicio

## ✅ Servidor Unificado Puerto 8000

El servidor MeriBot ahora funciona completamente en el **puerto 8000**, sirviendo tanto la API de FastAPI como el frontend web.

### 📡 URLs Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| 🏠 **Homepage** | `http://localhost:8000/` | Página principal del widget |
| 🤖 **Widget** | `http://localhost:8000/widget` | Interfaz del chatbot |
| 🔧 **API** | `http://localhost:8000/chatbot/query` | Endpoint principal del chatbot |
| 📚 **Docs** | `http://localhost:8000/docs` | Documentación interactiva de la API |
| 🗂️ **Archivos estáticos** | `http://localhost:8000/static/` | CSS, JS, imágenes del frontend |

### 🏃‍♂️ Cómo Iniciar el Servidor

#### Método 1: Comando directo (Recomendado - Funciona siempre)
```powershell
cd meribot_app
$env:PYTHONPATH = "C:\Users\cadiazga\Proyectos\VibeCoding\Meri-bot_refactor\meribot_app"
C:/Users/cadiazga/Proyectos/VibeCoding/Meri-bot_refactor/.venv/Scripts/python.exe -m uvicorn meribot.core.api.app:app --reload --host 127.0.0.1 --port 8000
```

#### Método 2: Script PowerShell (requiere permisos de ejecución)
```powershell
cd meribot_app
.\start_server.ps1
```
**Nota**: Si tienes problemas con caracteres Unicode en PowerShell, usa el Método 1.

#### Método 3: Script Python (alternativo)
```powershell
cd meribot_app
python start_server_fixed.py
```

### ⚙️ Configuración

#### Variables de Entorno Requeridas
Asegúrate de que el archivo `.env` contenga:
```env
AZURE_OPENAI_API_KEY=tu_clave_aqui
AZURE_OPENAI_ENDPOINT=tu_endpoint_aqui
AZURE_OPENAI_DEPLOYMENT_NAME=tu_deployment_aqui
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=tu_embedding_deployment_aqui
```

#### Archivos de Configuración
- `crawler_config.yaml` - Configuración del crawler y dominios permitidos
- `.env` - Variables de entorno para Azure OpenAI

### 🔍 Verificación

Una vez iniciado el servidor, verifica que funciona correctamente:

1. **API Health Check**: `http://localhost:8000/chatbot/health`
2. **Dominios permitidos**: `http://localhost:8000/chatbot/allowed_domains`
3. **Frontend funcional**: `http://localhost:8000/widget`
4. **Documentación**: `http://localhost:8000/docs`

### 🛠️ Resolución de Problemas

#### Error: "ModuleNotFoundError: No module named 'meribot'"
```powershell
# Asegúrate de estar en el directorio correcto y configurar PYTHONPATH
cd meribot_app
$env:PYTHONPATH = (Get-Location).Path
```

#### Error de credenciales Azure OpenAI
```powershell
# Verifica que el archivo .env existe y tiene las credenciales correctas
Get-Content .env | Where-Object { $_ -match "AZURE_OPENAI" }
```

#### Error en script PowerShell: "The string is missing the terminator"
```powershell
# Problema con caracteres Unicode. Usa el método directo:
cd meribot_app
$env:PYTHONPATH = "C:\Users\cadiazga\Proyectos\VibeCoding\Meri-bot_refactor\meribot_app"
C:/Users/cadiazga/Proyectos/VibeCoding/Meri-bot_refactor/.venv/Scripts/python.exe -m uvicorn meribot.core.api.app:app --reload --host 127.0.0.1 --port 8000
```

#### Error: "script file, or operable program"
```powershell
# PowerShell no puede ejecutar el script. Usa el comando directo o verifica permisos:
Get-ExecutionPolicy
# Si es muy restrictivo, usa el método 1 (comando directo)
```

#### Puerto 8000 ocupado
```powershell
# Cambiar a otro puerto (ej: 8001)
python -m uvicorn meribot.core.api.app:app --reload --host 127.0.0.1 --port 8001
```

### 📁 Estructura del Proyecto

```
meribot_app/
├── .env                    # Variables de entorno
├── crawler_config.yaml    # Configuración del crawler
├── start_server.py        # Script de inicio Python
├── start_server.ps1       # Script de inicio PowerShell
└── meribot/
    ├── core/
    │   └── api/
    │       └── app.py      # Aplicación FastAPI principal
    └── web/                # Frontend estático
        ├── css/
        ├── js/
        ├── img/
        └── widget-chatbot.html
```

### 🎯 Características

- **✅ Puerto unificado 8000**: API y frontend en el mismo puerto
- **✅ Recarga automática**: Cambios en código se reflejan automáticamente
- **✅ CORS configurado**: Frontend puede comunicarse con la API
- **✅ Archivos estáticos**: CSS, JS e imágenes servidos correctamente
- **✅ URLs relativas**: El frontend funciona independiente del puerto
- **✅ Montaje múltiple**: `/css/`, `/js/`, `/img/` y `/static/` disponibles

---

**¡El servidor MeriBot está listo para usar!** 🎉