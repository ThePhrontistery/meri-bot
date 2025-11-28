# MeriBot Widget Web

## 📋 Descripción

Este módulo contiene el **widget conversacional MeriBot** para la práctica Cloud & Custom Applications (C&CA) de Capgemini. Permite integrar un asistente virtual accesible, moderno y personalizable en cualquier web corporativa, siguiendo la identidad visual y los estándares de accesibilidad de la compañía.

## 🚀 Características principales

- **Widget flotante**: Acceso rápido desde cualquier página, con animaciones suaves y diseño responsivo.
- **Interfaz conversacional**: Chat tipo messenger, historial de sesión, indicador de escritura y notificaciones.
- **Sistema de filtros**: Permite filtrar dominios temáticos para personalizar las respuestas.
- **Indicadores de fuente**: Muestra la procedencia de la información con tooltips accesibles y enlaces directos.
- **Accesibilidad**: Navegación por teclado, roles ARIA, contraste adecuado y soporte móvil.
- **Integración backend**: Comunicación asíncrona con la API de MeriBot.
- **Extensible y modular**: Fácil de adaptar a nuevos dominios, fuentes y estilos.

## 🗂️ Estructura de carpetas

```text
meribot_app/
└── meribot/
    └── web/
        ├── css/
        │   └── widget-chatbot.css      # Estilos principales del widget
        ├── js/
        │   └── widget-chatbot.js       # Lógica y eventos del widget
        ├── img/
        │   └── Icono_Widget.png        # Icono corporativo del widget
        ├── widget-chatbot.html         # Demo standalone del widget
        ├── marked-cdn.html             # Integración de marked.js para Markdown
        ├── FUENTES_INFO.md             # Documentación de indicadores de fuente
        └── README.md                   # Este archivo
```

## ⚙️ Instalación y uso

### 1. Visualización directa (demo)

Abre `widget-chatbot.html` en tu navegador. El widget se carga automáticamente y puedes probar todas sus funcionalidades.

### 2. Integración en tu web

1. Copia los archivos de `css/`, `js/`, `img/` y el snippet de HTML del widget a tu proyecto.
2. Incluye en tu HTML principal:

   ```html
   <link rel="stylesheet" href="css/widget-chatbot.css">
   <script src="js/widget-chatbot.js" defer></script>
   ```

3. Añade el contenedor del widget donde desees (ver ejemplo en `widget-chatbot.html`).

### 3. Servidor local para pruebas

Desde la carpeta `web/`:

```powershell
python -m http.server 3000
```

Accede a [http://localhost:3000/widget-chatbot.html](http://localhost:3000/widget-chatbot.html)

## 🎨 Personalización

- **Colores y fuentes**: Edita las variables CSS en `widget-chatbot.css` para adaptar la identidad visual.
- **Iconos**: Sustituye `img/Icono_Widget.png` por tu logotipo si lo deseas.
- **Fuentes de información**: Consulta y amplía la lógica de indicadores en el JS y la documentación en `FUENTES_INFO.md`.

## 🧑‍💻 Desarrollo

- **JS moderno**: Código en ES2020+, sin frameworks, modular y documentado con JSDoc.
- **Accesibilidad**: Cumple WCAG 2.1 AA, roles ARIA y navegación por teclado.
- **Estilo**: Sigue BEM y buenas prácticas CSS, con soporte para dark mode y responsive.
- **Extensión**: Añade nuevos filtros, fuentes o eventos editando `widget-chatbot.js` y los assets relacionados.

## 🛡️ Seguridad

- Sanitización de entradas de usuario.
- Manejo robusto de errores y mensajes amigables.
- No almacena datos sensibles en el frontend.

## 📚 Documentación adicional

- [FUENTES_INFO.md](./FUENTES_INFO.md): Detalles sobre el sistema de indicadores de fuente.
- [../docs/setup.md](../../docs/setup.md): Guía de instalación y estructura global del proyecto.
- [../.github/copilot-instructions.md](../../.github/copilot-instructions.md): Convenciones de desarrollo y estándares.

## 📝 Licencia

© 2025 Capgemini - Cloud & Custom Applications. Proyecto interno para demostración y desarrollo corporativo.

---

**MeriBot Widget Web** - Transformando la experiencia de usuario en la web corporativa con IA conversacional.
