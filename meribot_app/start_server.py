#!/usr/bin/env python3
"""
Script de arranque para el servidor MeriBot API
Resuelve los problemas de imports configurando el PYTHONPATH correctamente
"""
import os
import sys

# Obtener el directorio actual (meribot_app)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Agregar el directorio al Python path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configurar variables de entorno
os.environ['PYTHONPATH'] = current_dir

# Importar y ejecutar
try:
    import uvicorn
    from meribot.core.api.app import app
    
    print("🚀 Iniciando servidor MeriBot API...")
    print(f"📁 Directorio de trabajo: {current_dir}")
    print(f"🐍 Python path: {sys.path[0]}")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📚 Documentación en: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[current_dir]
    )
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Asegúrate de que todas las dependencias estén instaladas")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error al iniciar servidor: {e}")
    sys.exit(1)