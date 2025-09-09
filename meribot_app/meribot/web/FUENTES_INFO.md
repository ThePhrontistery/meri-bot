# 📋 Funcionalidad de Indicadores de Fuente - MeriBot Widget

## ✨ Nueva Funcionalidad Implementada

Se ha añadido un **sistema de indicadores de fuente** que muestra de forma sutil cuándo una respuesta del bot proviene de una fuente específica de información.

## 🎯 Características Implementadas

### ✅ **Indicador Visual**
- **Icono minimalista**: Círculo pequeño con ícono de enlace en la esquina superior derecha del mensaje
- **Colores corporativos**: Azul CCA (#12abdb) con transparencias
- **Hover effects**: Animación sutil al pasar el cursor
- **No invasivo**: Solo aparece cuando hay fuente asociada

### ✅ **Tooltip Informativo**
- **Panel flotante**: Se abre al hacer clic en el indicador
- **Información clara**: 
  - "Fuente consultada"
  - Título del documento/página
  - Enlace directo al recurso original
- **Diseño coherente**: Mismo estilo que el dropdown de filtros

### ✅ **Responsive y Accesible**
- **Mobile-friendly**: Adaptado para dispositivos móviles
- **Accesibilidad**: Soporte para navegación por teclado (Escape para cerrar)
- **Enlaces externos**: Se abren en nueva pestaña

## 🔧 Respuestas con Fuente Configuradas

### **Talent**
- **Carrera profesional** → `https://intranet.capgemini.com/cca/carrera-profesional`
- **Contactos de RRHH** → `https://intranet.capgemini.com/cca/directorio-contactos`

### **Onboarding**
- **Primeros pasos** → `https://intranet.capgemini.com/cca/onboarding-checklist`
- **Formaciones mandatory** → `https://learning.capgemini.com/mandatory-training`

### **Formación**
- **AC&CAdemy** → `https://academy.capgemini.com/cca/programs`
- **Certificaciones** → `https://intranet.capgemini.com/cca/certification-program`

## 🎮 Cómo Probar la Funcionalidad

1. **Abrir el widget** haciendo clic en "Ask MeriBot"
2. **Escribir consultas específicas** como:
   - "carrera profesional"
   - "contactos de rrhh"
   - "primeros pasos"
   - "ac&cademy"
   - "certificaciones"
   - "formaciones mandatory"

3. **Observar el indicador** en la esquina superior derecha de la respuesta
4. **Hacer clic en el indicador** para ver el tooltip con la fuente
5. **Hacer clic en el enlace** para ir al documento original

## 💡 Funcionalidades Técnicas

### **Gestión de Estado**
- Los tooltips se cierran automáticamente al hacer clic fuera
- Solo un tooltip puede estar abierto a la vez
- Se limpian al cerrar el widget

### **Estructura de Datos**
```javascript
source: {
    url: "https://ejemplo.com/documento",
    title: "Título del Documento",
    type: "document" // document, page, platform
}
```

### **CSS Responsivo**
- Tooltip ajustado en pantallas móviles
- Iconos con tamaño mínimo táctil (20px)
- Animaciones sutiles y profesionales

## 🔄 Extensibilidad

El sistema está diseñado para ser fácilmente extensible:

1. **Añadir nuevas fuentes**: Solo agregar el objeto `source` a cualquier respuesta
2. **Diferentes tipos**: document, page, platform, database, etc.
3. **Personalización**: Colores y estilos pueden adaptarse por tipo de fuente

## 🎨 Integración Visual

- **Colores**: Azul corporativo CCA (#12abdb)
- **Tipografía**: Ubuntu (coherente con el resto del widget)
- **Animaciones**: fadeInUp suave (0.2s)
- **Posicionamiento**: Absoluto, no afecta el layout

La funcionalidad está completamente integrada y respeta todos los requisitos:
- ✅ No invasiva
- ✅ Sutil y elegante  
- ✅ Sin espacio adicional cuando no hay fuente
- ✅ Accesible en móvil y escritorio
- ✅ Componente reutilizable

¡La funcionalidad está lista para usar! 🚀
