#!/usr/bin/env python3
"""
Script para arrancar el servidor MeriBot
Verifica e instala dependencias automáticamente antes de arrancar
"""
import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# Agregar el directorio actual al Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def check_critical_dependencies():
    """
    Verifica dependencias críticas que deben estar disponibles.
    """
    critical_deps = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'chromadb',
        'langchain',
        'dotenv'  # python-dotenv se importa como 'dotenv'
    ]
    
    print("🔍 Verificando dependencias críticas...")
    missing_critical = []
    
    for dep in critical_deps:
        try:
            spec = importlib.util.find_spec(dep)
            if spec is None:
                missing_critical.append(dep)
                print(f"❌ CRÍTICA falta: {dep}")
            else:
                print(f"✅ CRÍTICA OK: {dep}")
        except Exception as e:
            missing_critical.append(dep)
            print(f"❌ Error verificando {dep}: {e}")
    
    if missing_critical:
        print(f"\n⚠️  DEPENDENCIAS CRÍTICAS FALTANTES: {missing_critical}")
        return False
    
    print("✅ Todas las dependencias críticas están disponibles")
    return True


def check_and_install_dependencies():
    """
    Verifica si todas las dependencias de requirements.txt están instaladas
    y las instala automáticamente si faltan.
    """
    requirements_file = Path(current_dir) / "requirements.txt"
    
    if not requirements_file.exists():
        print("⚠️  Archivo requirements.txt no encontrado")
        return True
    
    print("🔍 Verificando dependencias...")
    
    missing_packages = []
    
    # Mapeo de nombres de paquetes a nombres de módulos
    package_to_module = {
        'python-dotenv': 'dotenv',
        'beautifulsoup4': 'bs4',
        'PyMuPDF': 'fitz',
        'Requests': 'requests',
        'PyYAML': 'yaml'
    }
    
    # Leer requirements.txt
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Verificar cada dependencia
    for requirement in requirements:
        if not requirement:
            continue
            
        # Extraer nombre del paquete (antes de >= o ==)
        package_name = requirement.split('>=')[0].split('==')[0].split('[')[0].strip()
        
        # Determinar el nombre del módulo a verificar
        module_name = package_to_module.get(package_name, package_name.replace('-', '_'))
        
        try:
            # Intentar importar el paquete
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                # Intentar con el nombre original si el mapeo falló
                spec = importlib.util.find_spec(package_name)
                
            if spec is None:
                missing_packages.append(requirement)
                print(f"❌ Falta: {package_name}")
            else:
                print(f"✅ OK: {package_name}")
                
        except Exception as e:
            missing_packages.append(requirement)
            print(f"❌ Error verificando {package_name}: {e}")
    
    # Instalar paquetes faltantes
    if missing_packages:
        print(f"\n📦 Instalando {len(missing_packages)} dependencias faltantes...")
        try:
            cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando dependencias: {e}")
            print(f"📄 Output: {e.stdout}")
            print(f"📄 Error: {e.stderr}")
            return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True


try:
    # Verificar e instalar dependencias antes de importar
    print("🔧 Iniciando verificación del entorno...")
    
    if not check_and_install_dependencies():
        print("❌ No se pudieron instalar todas las dependencias")
        sys.exit(1)
    
    if not check_critical_dependencies():
        print("❌ Faltan dependencias críticas para el funcionamiento")
        sys.exit(1)
    
    print("\n🔄 Cargando módulos MeriBot...")
    
    # Importar la aplicación FastAPI
    from meribot.core.api.app import app
    print("✅ Import successful - aplicación MeriBot cargada")
    
    # Importar uvicorn para ejecutar el servidor
    import uvicorn
    
    if __name__ == "__main__":
        print("\n🚀 Iniciando servidor MeriBot...")
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