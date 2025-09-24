# 📘 Propósito del documento
Este documento proporciona una guía completa para la instalación, configuración y ejecución del proyecto **MeriBot**, el asistente conversacional empresarial desarrollado para C&CA. 
Está dirigido a desarrolladores, DevOps, administradores técnicos, analistas funcionales, Product Owners y Product Managers que deseen implementar, personalizar o mantener el sistema. Incluye detalles sobre la estructura del proyecto, requisitos previos, comandos de desarrollo y despliegue, así como enlaces útiles.

## 📁 Estructura de carpetas de la aplicación
============================================================
```
📁 raíz del proyecto
├── .github/                         # Configuración de GitHub
│   └── copilot-instructions.md      # Instrucciones para GitHub Copilot
├── docs/                           # Documentación completa del proyecto
│   ├── Functional_requirements/    # Requisitos funcionales
│   ├── Guides/                     # Guías y buenas prácticas
│   ├── Manual_Usuario/             # Manuales de usuario
│   ├── RFP/                        # Requisitos del cliente
│   └── *.md                        # Documentos técnicos
├── logs/                           # Logs del sistema
│   └── meribot_core.log
├── meribot_app/                    # 🔸 APLICACIÓN PRINCIPAL
│   ├── meribot/                    # Módulos core del chatbot
│   │   ├── core/                   # 🧠 Lógica principal y API
│   │   │   ├── api/                # FastAPI endpoints
│   │   │   │   ├── app.py          # Aplicación FastAPI principal
│   │   │   │   └── endpoints/      # Endpoints organizados
│   │   │   ├── conversation/       # Gestión de conversaciones
│   │   │   ├── db/                 # Acceso a base de datos
│   │   │   ├── llm/               # Integración con LLM
│   │   │   ├── templates/          # Plantillas de respuesta
│   │   │   └── chatengine.py       # Motor de conversación
│   │   ├── crawler/                # 🕷️ Web scraping y extracción
│   │   │   ├── api/                # API del crawler
│   │   │   ├── storage/            # Almacenamiento de datos
│   │   │   └── scraper.py          # Motor de scraping
│   │   ├── meri-cli/              # ⚙️ Herramientas CLI
│   │   │   ├── main.py             # Comandos principales
│   │   │   └── db_commands.py      # Comandos de BD
│   │   ├── utils/                  # Utilidades comunes
│   │   ├── web/                    # 🌐 Interfaz web
│   │   │   ├── css/                # Estilos del widget
│   │   │   ├── js/                 # JavaScript del chatbot
│   │   │   └── *.html              # Páginas del widget
│   │   ├── __init__.py
│   │   └── __main__.py             # Punto de entrada principal
│   ├── chroma_data/               # 🗄️ Base de datos vectorial
│   ├── data/                      # Datos extraídos por el scraper
│   │   └── scraped/
│   ├── logs/                      # Logs de la aplicación
│   ├── requirements.txt           # Dependencias Python
│   └── *.py                       # Scripts auxiliares
├── requirements.txt               # Dependencias del proyecto
└── README.md                      # Documentación principal
```

## 📤 Instalación y Configuración
============================================================

### Requisitos Previos

- Node.js 16+ (solo para desarrollo frontend)
- **Python 3.12 o superior**
  Recomendamos usar siempre una versión reciente de Python para asegurar compatibilidad.
- **uv**
  Es una herramienta moderna de gestión de entornos y dependencias para Python.
  Instálala una vez con:

  ```bash
  pipx install uv
  ```

  Más información: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

---

### Pasos Iniciales

#### 1. Clona el repositorio y navega a la carpeta del proyecto

   ```bash
   # Clonar el repositorio
   git clone https://github.com/ThePhrontistery/meri-bot
   cd meri-bot

   # Navegar a la aplicación principal
   cd meribot_app
   ```

   **Nota**: La aplicación principal se encuentra en la carpeta `meribot_app/` dentro del repositorio.
#### 2. Configura las Variables de entorno
Las variables de entorno (por ejemplo, puertos, modo desarrollo/producción, etc.) se gestionan en un archivo `.env`.

Copia el archivo de variables de entorno de ejemplo y edítalo según tus necesidades:

   ```bash
   cp .env.example .env
   ```

Estas variables se cargarán automáticamente al arrancar la app, gracias a `python-dotenv`.

#### 3. Instala dependencias

**Opción A: Con pip (método tradicional)**
```bash
pip install -r requirements.txt
```

**Opción B: Con uv (recomendado para desarrollo moderno)**

uv es una herramienta moderna que gestiona entornos y dependencias de forma más eficiente:

```bash
# Instala todas las dependencias y crea entorno virtual
uv sync
```

El comando `uv sync` lee el archivo **pyproject.toml** (si existe) o **requirements.txt**, instala todas las dependencias necesarias, crea un entorno virtual aislado, y guarda el estado en **uv.lock**.

**Gestión de dependencias con uv:**
```bash
# Añadir nueva dependencia
uv add nombre_paquete@latest    # Añade y bloquea la versión más reciente

# Actualizar dependencias
uv sync                        # Sincroniza el entorno con el lockfile

# Ejecutar comandos en el entorno virtual
uv run python -m meribot       # Ejecuta directamente en el entorno uv
```

Esto asegura que todo el equipo utilice exactamente las mismas versiones.

## � Ejecución en desarrollo
============================================================

### 🎯 Inicio Rápido - Servidor Completo

```bash
# Desde la carpeta meribot_app/
python -m meribot

# O alternativamente
uvicorn meribot.core.api.app:app --reload --host 0.0.0.0 --port 8000
```

**URLs disponibles:**
- **Widget del Chatbot**: http://localhost:8000/ o http://localhost:8000/widget
- **Documentación API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/chatbot/health

### 🌐 Frontend - Widget Independiente

Si quieres servir solo el frontend del widget:

```bash
# Desde meribot_app/meribot/web/
python -m http.server 3000
```

- **Interfaz del widget**: http://localhost:3000/widget-chatbot.html

### 🔧 Backend - Solo API FastAPI

Para ejecutar únicamente la API sin el frontend:

```bash
# Desde meribot_app/
uvicorn meribot.core.api.app:app --reload --port 8000
```

### ⚙️ CLI de Administración - meri-cli

```bash
# Ver todos los comandos disponibles
python -m meribot.meri-cli --help

# Ejecutar scraping manual de una URL específica
python -m meribot.meri-cli scrape --url https://ejemplo.com

# Gestionar la base de datos vectorial
python -m meribot.meri-cli db --reset    # Reiniciar BD
python -m meribot.meri-cli db --status   # Estado de la BD
python -m meribot.meri-cli db --optimize # Optimizar índices

# Ver logs del sistema
python -m meribot.meri-cli logs --tail 50
```

### 🕷️ Crawler - Extracción de Datos

```bash
# Ejecutar scraping programado
python -m meribot.crawler.api

# Scraping con configuración personalizada
python -m meribot.crawler.api --config custom_config.yaml
```

### 🐳 Ejecución con Docker (Opcional)

Si prefieres usar Docker:

```bash
# Construir la imagen
docker build -t meribot .

# Ejecutar el contenedor
docker run -p 8000:8000 meribot

# Con Docker Compose (si está disponible)
docker-compose up -d
```

## Instrucciones personalizadas para GitHub Copilot

En el archivo `.github/copilot-instructions.md` encontrarás detalles sobre la arquitectura y recomendaciones de uso, para que GitHub Copilot genere código siguiendo las convenciones y tecnologías del proyecto.

## Licencia

Este proyecto está bajo la licencia [LICENSE].


