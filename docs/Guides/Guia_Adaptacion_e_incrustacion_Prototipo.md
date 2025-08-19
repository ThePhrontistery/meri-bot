(WIP))
El prototipo con widget mediante Caja de Texto que se debe implementar en el repositorio meri-bot  debe adaptarse al CSS de esa web e incrustarlo de forma ligera en la home page de la página web C&CA bajada a local.

El propósito de este documento es disponer de la guía paso a paso para hacerlo correctamente.

Nota:

El css del portal anfitrión está disponible en /Cloud & Custom Applications_files/styles-2QPKW3UZ.css

La página web C&CA bajada a local es el archivo Cloud & Custom Applications.html

## 🧭 Guía paso a paso para adaptar e incrustar un prototipo FrontEnd en una aplicación Vibecoding

### 1. Revisión del prototipo

Asegúrate de que el prototipo esté limpio y modular: sin estilos globales invasivos, sin dependencias innecesarias.

Identifica los componentes clave que se van a incrustar.

### 2. Revisión del CSS de la web anfitriona

Analiza el CSS global de la web donde se va a incrustar el prototipo.

Identifica clases, variables, breakpoints y estilos que podrían conflictuar o que puedes reutilizar.

### 3. Adaptación del CSS del prototipo

Refactoriza el CSS del prototipo para:

Usar las variables y clases del CSS anfitrión.

Evitar estilos globales (body, h1, etc.) que puedan sobrescribir estilos existentes.

Usar scoping si es posible (por ejemplo, con CSS Modules, BEM, o prefijos únicos).

✅ Recomendación: Haz esta adaptación antes de incrustarlo en la aplicación, para evitar conflictos visuales y facilitar la integración.

### 4. Integración en el repositorio Vibecoding

Ubica el prototipo en la carpeta adecuada (por ejemplo, /components/PrototipoHome).

Divide el HTML en componentes si el stack lo permite (React, Vue, etc.).

Asegúrate de que los estilos estén correctamente importados y no afecten otras partes de la app.

### 5. Conexión con la arquitectura BackEnd (cuando esté lista)

Deja hooks o puntos de integración preparados para cuando el BackEnd esté implementado.

Puedes usar mocks o datos estáticos mientras tanto.

### 6. Testing visual y funcional

Verifica que el prototipo se vea bien en la home page.

Asegúrate de que no haya conflictos de estilos ni errores de JS.

Prueba en distintos navegadores y dispositivos.

### 🧾 Prompt para pedir esto correctamente a un colaborador o IA

Aquí tienes un prompt que puedes usar para pedir ayuda con esta tarea:

Prompt sugerido:

"Tengo un prototipo FrontEnd ya implementado en HTML, CSS y JS que debe incrustarse de forma ligera en la home page de una web. El prototipo debe adaptarse al CSS de la web anfitriona para evitar conflictos. La aplicación ya tiene definido el stack tecnológico y la estructura de carpetas, pero aún no tiene implementado el BackEnd. Necesito una guía paso a paso para adaptar el CSS del prototipo, integrarlo correctamente en el repositorio de la aplicación, y dejarlo listo para futuras conexiones con el BackEnd. ¿Me puedes ayudar con eso?"
