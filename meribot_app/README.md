# MeriBot - Asistente Virtual para CECA

MeriBot es un chatbot empresarial desarrollado para CECA que permite a los empleados realizar consultas sobre políticas, procedimientos y documentación interna de la organización.

## Estructura del Proyecto

```
meribot/
├── api/                     # Módulo de la API FastAPI
│   ├── __init__.py
│   └── app.py              # Aplicación principal de FastAPI
│
├── meri-cli/               # Herramientas de línea de comandos
│   ├── __init__.py
│   └── main.py             # Comandos CLI principales
│
├── core/                   # Lógica principal del chatbot
│   └── __init__.py
│
├── crawler/                # Módulo de web scraping
│   └── __init__.py
│
├── models/                 # Modelos de datos
│   └── __init__.py
│
├── services/               # Servicios de negocio
│   └── __init__.py
│
├── utils/                  # Utilidades y helpers
│   └── __init__.py
│
├── __init__.py
├── __main__.py             # Punto de entrada principal
│
web/                       # Interfaz web del widget
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── chat.js
│   └── index.html
│
├── .env.example           # Variables de entorno de ejemplo
├── .gitignore
├── Dockerfile             # Dockerfile para la API
├── Dockerfile.web         # Dockerfile para la interfaz web
├── docker-compose.yml     # Configuración de Docker Compose
├── requirements.txt       # Dependencias de Python
└── README.md              # Este archivo
```

## Requisitos Previos

- Docker y Docker Compose
- Python 3.10 o superior
- Node.js 16+ (solo para desarrollo frontend)

## Configuración Inicial

1. Clona el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd meribot_app
   ```

2. Copia el archivo de variables de entorno de ejemplo y configúralo:
   ```bash
   cp .env.example .env
   # Edita el archivo .env según sea necesario
   ```

3. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución con Docker (Recomendado)

```bash
# Construir y ejecutar los contenedores
docker-compose up --build

# Para ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## Ejecución en Desarrollo

### Backend (FastAPI)

```bash
# Instalar dependencias
pip install -r requirements-dev.txt

# Ejecutar el servidor de desarrollo
uvicorn meribot.api.app:app --reload
```

### Frontend (Widget)

```bash
cd web
python -m http.server 3000
```

## Uso

### Interfaz Web

Abre tu navegador y navega a:
- Interfaz del widget: http://localhost:3000
- Documentación de la API: http://localhost:8000/docs

### CLI de Administración (meri-cli)

#### Ubicación
Los archivos de meri-cli se encuentran en: `meribot/meri-cli/`

#### Instalación para uso global (Windows)

Para poder usar `meri-cli` desde cualquier ubicación en la terminal:

```powershell
# Navegar al directorio meri-cli
cd meribot/meri-cli

# Ejecutar el instalador
.\install-meri-cli.ps1 -Install

# Reiniciar la terminal o ejecutar:
refreshenv
```

#### Uso directo (sin instalación)

```bash
# Desde el directorio meri-cli
cd meribot/meri-cli
.\meri-cli.bat [comando] [opciones]
# o
python meri-cli.py [comando] [opciones]
```

#### Comandos disponibles

```bash
# Ver ayuda general
meri-cli --help

# Ver ayuda del comando crawl
meri-cli crawl --help

# Ejecutar crawling completo (parámetros obligatorios)
meri-cli crawl --url [URL] --dominio [DOMINIO]

# Ejemplo de crawling básico
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"

# Ejecutar crawling con opciones avanzadas
meri-cli crawl --url [URL] --dominio [DOMINIO] --max-depth 3 --formats "html,pdf"

# Simular crawling sin ejecutar (dry-run)
meri-cli crawl --url [URL] --dominio [DOMINIO] --dry-run

# Comando obsoleto para compatibilidad (usar crawl en su lugar)
meri-cli scrape --url [URL]

# Gestionar la base de datos
meri-cli db [--reset]
```

#### Ejemplos de uso avanzado

```bash
# Desde el directorio meri-cli

# Crawling con profundidad limitada y filtros
.\meri-cli.bat crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --max-depth 2 --exclude ".*logout.*"

# Crawling solo de PDFs
.\meri-cli.bat crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --formats "pdf"

# Procesamiento manual de URLs específicas
.\meri-cli.bat crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --manual "https://cca.capgemini.com/page1,https://cca.capgemini.com/page2"

# Conectar a un API en otro host
.\meri-cli.bat crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" --api-host "http://meribot-api:8000"
```

#### Uso como módulo Python (alternativo)

```bash
# Ver ayuda general
python -m meribot.meri-cli.main --help

# Ejecutar crawling
python -m meribot.meri-cli.main crawl --url [URL] --dominio [DOMINIO]

# Usar como módulo del paquete meribot
python -m meribot --help
```

## Despliegue

1. Configura las variables de entorno en producción (`DATABASE_URL`, `SECRET_KEY`, etc.)
2. Construye las imágenes para producción:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```
3. Inicia los servicios:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Licencia

Este proyecto está bajo la licencia [LICENSE].
