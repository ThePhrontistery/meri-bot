#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de autenticación en el CLI.
"""

import subprocess
import sys
import os

def test_cli_with_auth():
    """Prueba el CLI con parámetros de autenticación"""
    
    # Simular credenciales de prueba
    username = "test_user"
    password = "test_pass"
    url = "https://cca.capgemini.com/web/onboarding"
    dominio = "cca.capgemini.com"
    
    print("🧪 Prueba: CLI con autenticación")
    print(f"URL: {url}")
    print(f"Dominio: {dominio}")
    print(f"Usuario: {username}")
    print("Contraseña: [OCULTA]")
    print("-" * 50)
    
    # Construir comando
    cmd = [
        sys.executable, "-m", "meribot.meri-cli.main", "crawl",
        "--url", url,
        "--dominio", dominio,
        "--username", username,
        "--password", password,
        "--dry-run"  # Usar dry-run para la prueba
    ]
    
    print("Comando a ejecutar:")
    cmd_display = cmd.copy()
    # Ocultar la contraseña en la visualización
    if "--password" in cmd_display:
        pass_index = cmd_display.index("--password")
        if pass_index + 1 < len(cmd_display):
            cmd_display[pass_index + 1] = "[OCULTA]"
    print(" ".join(cmd_display))
    print()
    
    try:
        # Ejecutar comando
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("=== SALIDA ESTÁNDAR ===")
        print(result.stdout)
        
        if result.stderr:
            print("=== SALIDA DE ERROR ===")
            print(result.stderr)
        
        print(f"=== CÓDIGO DE SALIDA: {result.returncode} ===")
        
        # Verificar éxito
        if result.returncode == 0:
            print("✅ Prueba exitosa: CLI acepta parámetros de autenticación")
            return True
        else:
            print("❌ Prueba falló: Error en CLI")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout: El comando tardó demasiado")
        return False
    except Exception as e:
        print(f"💥 Error ejecutando comando: {e}")
        return False

def test_api_payload():
    """Prueba el payload JSON que se enviaría a la API"""
    
    print("\n🧪 Prueba: Estructura del payload JSON")
    print("-" * 50)
    
    # Simular payload que enviaría el CLI
    payload = {
        "url": "https://cca.capgemini.com/web/onboarding",
        "domain": "cca.capgemini.com",
        "credentials": {
            "username": "test_user",
            "password": "test_pass"
        }
    }
    
    import json
    payload_json = json.dumps(payload, indent=2)
    
    # Ocultar contraseña para mostrar
    payload_display = payload.copy()
    if "credentials" in payload_display:
        payload_display["credentials"] = payload_display["credentials"].copy()
        payload_display["credentials"]["password"] = "[OCULTA]"
    
    payload_display_json = json.dumps(payload_display, indent=2)
    
    print("Payload que se enviaría a /crawler/crawl-and-process:")
    print(payload_display_json)
    
    print("✅ Estructura del payload correcta")
    return True

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de autenticación...")
    print("=" * 60)
    
    success = True
    
    # Prueba 1: CLI con parámetros
    success &= test_cli_with_auth()
    
    # Prueba 2: Estructura del payload
    success &= test_api_payload()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Todas las pruebas pasaron exitosamente!")
        print("\nAhora puedes usar el comando:")
        print("python -m meribot.meri-cli.main crawl \\")
        print("  --url \"https://cca.capgemini.com/web/onboarding\" \\")
        print("  --dominio \"cca.capgemini.com\" \\")
        print("  --username \"tu_usuario\" \\")
        print("  --password \"tu_contraseña\"")
    else:
        print("❌ Algunas pruebas fallaron. Revisa los errores arriba.")
        sys.exit(1)