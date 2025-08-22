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

### CLI de Administración

```bash
# Ver ayuda
python -m meribot --help

# Ejecutar scraping manual
python -m meribot scrape --url [URL]

# Gestionar la base de datos
python -m meribot db [--reset]
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
