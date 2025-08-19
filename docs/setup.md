# 📘 Propósito del documento
Este documento proporciona una guía completa para la instalación, configuración y ejecución del proyecto **MeriBot**, el asistente conversacional empresarial desarrollado para C&CA. 
Está dirigido a desarrolladores, DevOps, administradores técnicos, analistas funcionales, Product Owners y Product Managers que deseen implementar, personalizar o mantener el sistema. Incluye detalles sobre la estructura del proyecto, requisitos previos, comandos de desarrollo y despliegue, así como enlaces útiles.

## 📁 Estructura de carpetas de la aplicación
============================================================
```
📁 raíz del proyecto
│       ├──.github/                         # Módulo de GitHub
│           ├── copilot-instructions.md     # Instrucciones para GitHub Copilot
│       ├── docs/                           # Documentation (Markdown files)
│       ├── Local_C&CA_host_web/            # Web del portal anfitrión en local
│       ├── meribot_app/
│         ├── meribot/  
│             ├── api/                        # Módulo de la API FastAPI
│             │   ├── __init__.py
│             │   └── app.py                  # Aplicación principal de FastAPI
│             │
│             ├── meri-cli/                   # Herramientas de línea de comandos
│             │   ├── __init__.py
│             │   └── main.py                 # Comandos CLI principales
│             │
│             ├── core/                       # Lógica principal del chatbot
│             │   └── __init__.py
│             │
│             ├── crawler/                    # Módulo de web scraping
│             │   └── __init__.py
│             │
│             ├── models/                     # Modelos de datos
│             │   └── __init__.py
│             │
│             ├── services/                   # Servicios de negocio
│             │   └── __init__.py
│             │
│             ├── utils/                      # Utilidades y helpers
│             │   └── __init__.py
│             │
│             ├── __init__.py
│             ├── __main__.py                 # Punto de entrada principal
│             │
│         ├── web/                          # Interfaz web del widget
│             ├── static/
│             │   ├── css/
│             │   │   └── styles.css
│             │   ├── js/#
│             │   │   └── chat.js
│             │   └── index.html
│         ├── requirements.txt          # Dependencias de Python
│       ├──.env                      # Variables de entorno
│       ├──.gitignore                # indica a Git qué archivos/carpetas deben ser ignorados
│       ├── README.md                 # Estructura de Carpetas y enlaces a Documentos/instrucciones
│       ├── tests/                    # Unit and integration tests
│       ├── logs/                     # Server and application logs
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

#### 1. Clona el repositorio y entra en la carpeta del proyecto

   ```bash
   git clone [URL_DEL_REPOSITORIO]
        siendo [URL_DEL_REPOSITORIO]:
        para meri-bot: https://github.com/ThePhrontistery/meri-bot
        para mari-bot: https://github.com/ThePhrontistery/mari-bot
   cd meribot_app
   ```
#### 2. Configura las Variables de entorno
Las variables de entorno (por ejemplo, puertos, modo desarrollo/producción, etc.) se gestionan en un archivo `.env`.

Copia el archivo de variables de entorno de ejemplo y edítalo según tus necesidades:

   ```bash
   cp .env.example .env
   ```

Estas variables se cargarán automáticamente al arrancar la app, gracias a `python-dotenv` (ver `app/__init__.py`).
#### 3. Instala dependencias

- Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```
   
- Instala automáticamente todas las dependencias, crea el entorno virtual y el archivo de lock.

    ```bash
    uv sync
    ```
El comando `uv sync` lee el archivo **pyproject.toml**, instala todas las dependencias necesarias, crea un entorno virtual aislado, y guarda el estado en **uv.lock**

- Cómo añadir o actualizar dependencias
Cuando necesites nuevas librerías o quieras actualizar alguna existente, utiliza:

    ```bash
    uv add nombre_paquete@latest    # Añade y bloquea la versión más reciente
    uv sync                        # Sincroniza el entorno con el lockfile
    ```

Esto asegura que todo el equipo utilice exactamente las mismas versiones.

## 📚 Ejecución en desarrollo
============================================================
### Frontend (Widget)

  ```bash
  cd web
  python -m http.server 3000
```

Abre tu navegador y navega a:
- Interfaz del widget: http://localhost:3000
- Documentación de la API: http://localhost:8000/docs


(NO VALE):
- Inicia el servidor con recarga automática (hot reload)
  ```bash
  uv run -- uvicorn app.__main__:app --reload
    ```

### Frontend (C&CA en local con Widget embebido)- Interfaz Web

  ```bash
  
  ```

### Backend (FastAPI)

  ```bash
  # Instalar dependencias
  pip install -r requirements.txt

  # Ejecutar el servidor de desarrollo
  uvicorn meribot.api.app:app --reload
  ```

### CLI de Administración

```bash
# Ver ayuda
python -m meribot --help

# Ejecutar scraping manual
python -m meribot scrape --url [URL]

# Gestionar la base de datos
python -m meribot db [--reset]
```

## Instrucciones personalizadas para GitHub Copilot

En el archivo `.github/copilot-instructions.md` encontrarás detalles sobre la arquitectura y recomendaciones de uso, para que GitHub Copilot genere código siguiendo las convenciones y tecnologías del proyecto.

## Licencia

Este proyecto está bajo la licencia [LICENSE].


