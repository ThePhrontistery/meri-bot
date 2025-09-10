# MeriBot Widget UI - Prototipo de Asistente Virtual Conversacional

## 📋 Descripción del Proyecto

Este repositorio contiene el prototipo del **Widget MeriBot**, un asistente virtual conversacional desarrollado para la intranet corporativa de **Cloud & Custom Applications (C&CA)** de Capgemini.

El prototipo demuestra la integración de un chatbot de IA en la página principal de CCA, manteniendo la identidad visual corporativa y ofreciendo una experiencia de usuario fluida y profesional.

## 🎯 Objetivo

Crear un prototipo funcional del Widget-ChatBot conversacional MeriBot para presentar al cliente, mostrando:

- Integración natural en la aplicación CCA existente
- Interfaz conversacional intuitiva y accesible
- Respuestas contextuales sobre la práctica C&CA
- Diseño que respeta la identidad visual corporativa
- Experiencia de usuario optimizada para profesionales

## 🚀 Características Principales

### 🎨 Diseño y UX
- **Widget flotante** posicionado discretamente en la esquina inferior derecha
- **Identidad visual coherente** con los colores y tipografías de Capgemini/CCA
- **Animaciones suaves** para transiciones y interacciones
- **Diseño responsivo** que se adapta a dispositivos móviles
- **Indicadores visuales** de estado (en línea, escribiendo, notificaciones)

### 💬 Funcionalidades Conversacionales
- **Chat interactivo** con interfaz tipo messenger
- **Sugerencias rápidas** contextuales para guiar la conversación
- **Respuestas inteligentes** sobre temas relevantes de C&CA
- **Indicador de escritura** que simula la respuesta en tiempo real
- **Historial de conversación** durante la sesión

### 🧠 Conocimiento Especializado
- Información sobre la práctica Cloud & Custom Applications
- Detalles de formaciones disponibles (AC&CAdemy, Mandatory, etc.)
- Contactos corporativos relevantes (RRHH, Group IT, Formación)
- Guías de carrera profesional y competencias
- Información sobre iniciativas como IDEAS4ALL

### 🔧 Características Técnicas
- **HTML5/CSS3/JavaScript** vanilla para máxima compatibilidad
- **Arquitectura modular** fácilmente integrable
- **Gestión de estado** del widget y conversaciones
- **Sistema de respuestas** configurable y extensible
- **Optimización de rendimiento** con lazy loading

## 📁 Estructura del Proyecto

```
MeriBot_Widget_UI/
├── widget-chatbot.html          # Widget standalone para demostración
├── cca-with-meribot-widget.html # Página CCA completa con widget integrado
├── CCA Home Page/               # Recursos originales de la aplicación CCA
│   ├── Cloud & Custom Applications.html
│   └── Cloud & Custom Applications_files/
│       ├── *.png, *.svg         # Imágenes y logos corporativos
│       ├── *.css                # Estilos originales
│       └── *.js                 # Scripts originales
└── README.md                    # Este archivo de documentación
```

## 🛠️ Instalación y Uso

### Opción 1: Visualización Directa
1. Abrir `cca-with-meribot-widget.html` en un navegador web moderno
2. El prototipo se carga inmediatamente mostrando la integración completa

### Opción 2: Servidor Local
```bash
# Navegar al directorio del proyecto
cd MeriBot_Widget_UI

# Iniciar servidor local (Python 3)
python -m http.server 8000

# O usar Node.js
npx http-server

# Acceder a http://localhost:8000/cca-with-meribot-widget.html
```

## 🎮 Guía de Uso del Prototipo

### 1. Activación del Widget
- **Clic en el botón flotante azul** en la esquina inferior derecha
- El widget se expande con una animación suave
- Aparece la interfaz de chat con mensaje de bienvenida

### 2. Interacción Conversacional
- **Escribir preguntas** en el campo de texto
- **Usar sugerencias rápidas** haciendo clic en los chips
- **Enviar mensajes** con Enter o el botón de envío
- Observar las **respuestas contextuales** del asistente

### 3. Navegación y Funciones
- **Cerrar el widget** haciendo clic en el botón flotante nuevamente
- **Scroll automático** para seguir la conversación
- **Notificaciones** visuales para nuevos mensajes

## 🎯 Casos de Uso Demostrados

### Información Corporativa
- "¿Qué es C&CA?"
- "Ver organigrama"
- "Servicios que ofrecemos"

### Formaciones y Desarrollo
- "Formaciones disponibles"
- "AC&CAdemy"
- "Carrera profesional"

### Contactos y Soporte
- "Contactos de RRHH"
- "Group IT"
- "Formación interna"

### Iniciativas Especiales
- "IDEAS4ALL"
- "Proponer idea"
- "Cátedra UV"

## 🎨 Paleta de Colores Corporativa

```css
--capgemini-blue: #0070ad        /* Azul corporativo principal */
--capgemini-vibrant-blue: #12abdb /* Azul vibrante para acentos */
--capgemini-dark-grey: #272936    /* Gris oscuro para textos */
--capgemini-cool-grey: #f6f6f6    /* Gris claro para fondos */
--capgemini-white: #ffffff        /* Blanco corporativo */
```

## ⚡ Características Técnicas Destacadas

### Responsive Design
- Adaptación automática a pantallas móviles
- Reposicionamiento del widget en dispositivos pequeños
- Tipografías escalables y legibles

### Accesibilidad
- Contrastes apropiados según estándares WCAG
- Navegación por teclado habilitada
- Indicadores visuales claros para el estado del sistema

### Performance
- Carga diferida de recursos no críticos
- Animaciones optimizadas con CSS3
- Gestión eficiente del DOM y eventos

### Extensibilidad
- Sistema de respuestas fácilmente configurable
- Arquitectura modular para nuevas funcionalidades
- API de integración preparada para servicios backend

## 🚀 Siguientes Pasos Recomendados

### Fase 1: Validación del Prototipo
- [ ] Presentación al cliente y stakeholders
- [ ] Recopilación de feedback y ajustes
- [ ] Validación de la experiencia de usuario

### Fase 2: Desarrollo Backend
- [ ] Integración con servicios de IA conversacional
- [ ] Conexión con bases de datos corporativas
- [ ] Sistema de autenticación y personalización

### Fase 3: Funcionalidades Avanzadas
- [ ] Búsqueda semántica en documentación
- [ ] Integración con calendarios y reservas
- [ ] Notificaciones push y seguimiento

### Fase 4: Despliegue y Monitorización
- [ ] Integración en la intranet de producción
- [ ] Analytics y métricas de uso
- [ ] Mejora continua basada en datos

## 🤝 Contribuciones y Colaboración

Este prototipo ha sido desarrollado como demostración para el proyecto MeriBot Widget UI. Para contribuciones o consultas sobre el desarrollo:

- **Contacto técnico**: Equipo de desarrollo C&CA
- **Repositorio**: Espacio de trabajo colaborativo
- **Documentación**: Disponible en el directorio del proyecto

## 📄 Licencia y Derechos

© 2025 Capgemini - Cloud & Custom Applications
Proyecto interno de desarrollo y prototipado para cliente corporativo.

---

**MeriBot Widget UI** - Transformando la experiencia de usuario en la intranet corporativa con IA conversacional.
