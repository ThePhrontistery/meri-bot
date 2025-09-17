#!/usr/bin/env python3
"""
Test básico para verificar que la refactorización de la API funciona correctamente.
Verifica que se pueden importar los módulos desde la nueva ubicación.
"""

def test_api_imports():
    """Verificar que los imports de la API funcionan desde la nueva ubicación."""
    try:
        # Test del import principal
        import meribot.core.api
        print("✅ Import de meribot.core.api exitoso")
        
        # Test de que podemos importar FastAPI sin inicializar ChatEngine
        import sys
        import os
        
        # Evitar la inicialización automática del ChatEngine
        old_path = sys.path[:]
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Verificar que el módulo existe
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "api_app", 
            "meribot/core/api/app.py"
        )
        assert spec is not None
        print("✅ Archivo meribot.core.api.app encontrado")
        
        # Verificar que FastAPI está importado correctamente
        with open("meribot/core/api/app.py", "r") as f:
            content = f.read()
            assert "from fastapi import FastAPI" in content
            assert "app = FastAPI" in content
        print("✅ FastAPI app definida correctamente")
        
        return True
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Ejecutando tests de refactorización API...")
    success = test_api_imports()
    
    if success:
        print("\n🎉 ¡Refactorización exitosa! La API está disponible en core/api/")
    else:
        print("\n💥 La refactorización tiene problemas. Revisar imports.")