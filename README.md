# MeriBot – Chatbot conversacional Empresarial

Este repositorio contiene el proyecto **MeriBot**, el asistente conversacional empresarial desarrollado para la intranet de C&CA. Está diseñado con una arquitectura distribuida y escalable, utilizando FastAPI, LangChain, ChromaDB y un widget web embebido.

## 🚀 Inicio Rápido

```bash
# Clonar repositorio
git clone https://github.com/ThePhrontistery/meri-bot
cd meri-bot

# Navegar a la aplicación principal
cd meribot_app

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
python -m meribot
```

## 📁 Estructura del Proyecto
```
📁 raíz del proyecto
├── .github/                         # Configuración de GitHub
│   └── copilot-instructions.md      # Instrucciones para GitHub Copilot
├── docs/                           # Documentación del proyecto
│   ├── Functional_requirements/    # Requisitos funcionales y User Stories
│   │   ├── Features_US_AC_NFR-Requirements.md
│   │   └── Features_User_Stories.md
│   ├── Guides/                     # Guías y buenas prácticas
│   │   └── Guia_Adaptacion_e_incrustacion_Prototipo.md
│   ├── Handover/                   # Documentación de traspaso
│   │   └── Situacion_y_Actividades_realizadas.md
│   ├── Manual_Usuario/             # Manuales de usuario
│   │   ├── Manual_Usuario_Chatbot_MeriBot.md
│   │   ├── Manual_Usuario_Comando_Crawler.md
│   │   └── Manual_Usuario_meri-cli.md
│   ├── Prompts/                    # Prompts y gestión de tareas
│   │   ├── crear-prd.md
│   │   ├── generar-tareas.md
│   │   └── procesar-lista-tareas.md
│   ├── RFP/                        # Requisitos del cliente
│   │   ├── RFP-MeriBot-Grouped_Requirements.md
│   │   ├── RFP-MeriBot-Sketch-Widget.png
│   │   └── RFP-MeriBot-Sketch-Panel_de_conversacion.png
│   ├── Technical summary/          # Resúmenes técnicos
│   │   └── Resumen_Tecnico_MeriBot.md
│   ├── architecture.md             # Arquitectura del sistema
│   ├── deployment.md               # Guía de despliegue
│   ├── setup.md                    # Instalación y configuración
│   ├── tech-stack.md               # Stack tecnológico
│   └── ui-design.md                # Diseño de interfaz
├── logs/                           # Logs del sistema
│   └── meribot_core.log
├── meribot_app/                    # Aplicación principal
│   ├── meribot/                    # Módulos core del chatbot
│   │   ├── core/                   # Lógica principal y API
│   │   │   ├── api/                # FastAPI endpoints
│   │   │   ├── conversation/       # Gestión de conversaciones
│   │   │   ├── db/                 # Acceso a base de datos
│   │   │   ├── llm/               # Integración con LLM
│   │   │   └── templates/          # Plantillas de respuesta
│   │   ├── crawler/                # Web scraping y extracción
│   │   │   ├── api/                # API del crawler
│   │   │   └── storage/            # Almacenamiento de datos
│   │   ├── meri-cli/              # Herramientas CLI
│   │   ├── utils/                  # Utilidades comunes
│   │   └── web/                    # Interfaz web
│   ├── chroma_data/               # Base de datos vectorial
│   ├── data/                      # Datos extraídos
│   │   └── scraped/
│   ├── logs/                      # Logs de la aplicación
│   └── requirements.txt           # Dependencias Python
├── requirements.txt               # Dependencias del proyecto
└── README.md                      # Este documento
```


## 📚 Documentación e Instrucciones

### 🔧 Configuración y Desarrollo
- [**Instalación y Configuración**](docs/setup.md) - Guía completa de setup
- [**Arquitectura**](docs/architecture.md) - Diseño del sistema
- [**Stack Tecnológico**](docs/tech-stack.md) - Tecnologías utilizadas
- [**Despliegue**](docs/deployment.md) - Guía de producción
- [**Copilot Instructions**](.github/copilot-instructions.md) - Guías para desarrollo con IA

### 📋 Requisitos y Especificaciones
- [**RFP - Requisitos del Cliente**](docs/RFP/RFP-MeriBot-Grouped_Requirements.md)
- [**Requisitos Funcionales**](docs/Functional_requirements/Features_US_AC_NFR-Requirements.md)
- [**User Stories**](docs/Functional_requirements/Features_User_Stories.md)
- [**Diseño de Interfaz**](docs/ui-design.md) - Especificaciones UX/UI

### 📖 Manuales de Usuario
- [**Manual del Chatbot**](docs/Manual_Usuario/Manual_Usuario_Chatbot_MeriBot.md)
- [**Manual del Crawler**](docs/Manual_Usuario/Manual_Usuario_Comando_Crawler.md)
- [**Manual de meri-cli**](docs/Manual_Usuario/Manual_Usuario_meri-cli.md)

### 🛠️ Guías Técnicas
- [**Guía de Adaptación**](docs/Guides/Guia_Adaptacion_e_incrustacion_Prototipo.md)
- [**Resumen Técnico**](docs/Technical%20summary/Resumen_Tecnico_MeriBot.md)
- [**Situación del Proyecto**](docs/Handover/Situacion_y_Actividades_realizadas.md)

## 🏗️ Componentes Principales

### 🤖 Core del Chatbot (`meribot/core/`)
- **API FastAPI**: Endpoints REST para comunicación
- **Motor de Conversación**: Gestión de diálogos y contexto
- **Integración LLM**: Conexión con modelos de lenguaje
- **Base de Datos**: Almacenamiento de conversaciones y datos

### 🕷️ Web Crawler (`meribot/crawler/`)
- **Extractor de Contenido**: Scraping automatizado de intranets
- **Procesamiento de Datos**: Limpieza y estructuración
- **API del Crawler**: Endpoints para gestión de scraping
- **Almacenamiento**: Persistencia de datos extraídos

### ⚙️ CLI de Administración (`meribot/meri-cli/`)
- **Gestión del Sistema**: Comandos administrativos
- **Control del Crawler**: Ejecución manual y programada
- **Mantenimiento BD**: Limpieza y optimización de datos
- **Monitoreo**: Logs y estado del sistema

### 🌐 Interfaz Web (`meribot/web/`)
- **Widget Embebido**: Componente JavaScript para intranets
- **Panel de Conversación**: Interfaz de usuario del chat
- **Integración**: APIs para comunicación con backend

## 🚀 Tecnologías Utilizadas

- **Backend**: Python 3.12+, FastAPI, LangChain
- **Base de Datos**: ChromaDB (vectorial), SQLite
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Scraping**: BeautifulSoup, Selenium, Requests
- **Contenedores**: Docker, Docker Compose
- **IA/ML**: OpenAI API, Embeddings, RAG (Retrieval-Augmented Generation)
