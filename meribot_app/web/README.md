# Capa de Interacción del Usuario

## Descripción
Este módulo implementa la interfaz de usuario del chatbot MeriBot, que se integra en la intranet de CECA. Es un widget web ligero y responsivo que se comunica con el backend a través de la API REST.

## Características Principales
- Interfaz de chat moderna y responsiva
- Diseño adaptable a diferentes tamaños de pantalla
- Indicadores de escritura en tiempo real
- Soporte para historial de conversación
- Fácil integración en cualquier página web

## Estructura del Módulo
```
web/
├── static/
│   ├── css/
│   │   └── styles.css     # Estilos del widget
│   ├── js/
│   │   └── chat.js       # Lógica del cliente
│   └── index.html        # Plantilla HTML del widget
└── nginx/                # Configuración de Nginx para producción
    └── default.conf
```

## Integración
Para integrar el widget en una página web, añade el siguiente código:

```html
<!-- Widget de MeriBot -->
<div id="meribot-widget"></div>
<script src="/static/js/chat.js"></script>
<link rel="stylesheet" href="/static/css/styles.css">
```

## Personalización
### Variables CSS
Puedes personalizar la apariencia modificando estas variables en `styles.css`:

```css
:root {
    --primary-color: #2c3e50;      /* Color principal */
    --secondary-color: #3498db;    /* Color de acento */
    --background-color: #f5f7fa;   /* Color de fondo */
    --text-color: #2c3e50;        /* Color de texto principal */
    --bot-message-bg: #e3f2fd;    /* Fondo de mensajes del bot */
    --user-message-bg: #e8f5e9;   /* Fondo de mensajes del usuario */
}
```

## Configuración
El widget se puede configurar mediante atributos de datos:

```html
<div id="meribot-widget" 
     data-api-url="https://api.ejemplo.com/chatbot/query"
     data-theme="light"
     data-welcome-message="¡Hola! ¿En qué puedo ayudarte hoy?">
</div>
```

## Desarrollo
Para desarrollo local:

```bash
# Instalar dependencias (si es necesario)
npm install

# Iniciar servidor de desarrollo
python -m http.server 3000
```

## Despliegue
El widget está diseñado para ser servido estáticamente. Para producción, se recomienda usar Nginx o un CDN.

## Compatibilidad
- Navegadores modernos (Chrome, Firefox, Safari, Edge)
- Soporte para móviles y tablets
- Compatible con Internet Explorer 11 (requiere polyfills)
