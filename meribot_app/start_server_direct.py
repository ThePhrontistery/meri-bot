#!/usr/bin/env python3
"""
Script para arrancar el servidor MeriBot
"""
import sys
import os

# Agregar el directorio actual al Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Importar la aplicación FastAPI
    from meribot.core.api.app import app
    print("✅ Import successful - aplicación MeriBot cargada")
    
    # Importar uvicorn para ejecutar el servidor
    import uvicorn
    
    if __name__ == "__main__":
        print("🚀 Iniciando servidor MeriBot...")
        print("📍 URL: http://localhost:8000")
        print("📖 Documentación: http://localhost:8000/docs")
        print("🔗 Widget: http://localhost:8000/widget")
        print("🔧 API Crawler: http://localhost:8000/crawler/*")
        print("\n💡 Presiona Ctrl+C para detener el servidor")
        
        # Usar string import para que funcione el reload
        uvicorn.run(
            "meribot.core.api.app:app",
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info",
            reload_dirs=[current_dir]
        )
        
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print("🔍 Verificando estructura del proyecto...")
    
    # Diagnóstico básico
    print(f"📁 Directorio actual: {current_dir}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    if os.path.exists("meribot"):
        print("✅ Directorio 'meribot' encontrado")
        if os.path.exists("meribot/__init__.py"):
            print("✅ Archivo meribot/__init__.py encontrado")
        else:
            print("❌ Archivo meribot/__init__.py NO encontrado")
    else:
        print("❌ Directorio 'meribot' NO encontrado")
    
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)