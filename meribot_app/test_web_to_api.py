#!/usr/bin/env python3
"""
Test específico para verificar la comunicación Web-to-API después de la refactorización.
Simula las llamadas exactas que hace el frontend JavaScript.
"""

import requests
import json
import time

def test_web_to_api_communication():
    """Test de comunicación web-to-API completo."""
    
    base_url = "http://localhost:8000"
    results = []
    
    print("🔗 Testing Web-to-API Communication after Refactoring")
    print("=" * 55)
    
    # Test 1: Simular la carga inicial de dominios (loadDomainsConfig)
    print("\n1️⃣ Test: Carga inicial de dominios (loadDomainsConfig)")
    try:
        response = requests.get(f"{base_url}/chatbot/allowed_domains")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dominios cargados: {data.get('allowed_domains', [])}")
            results.append(("Domain Loading", True, f"Found {len(data.get('allowed_domains', []))} domains"))
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            results.append(("Domain Loading", False, f"Status {response.status_code}"))
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        results.append(("Domain Loading", False, str(e)))
    
    # Test 2: Simular una consulta simple del chatbot (sendUserMessage)
    print("\n2️⃣ Test: Consulta simple del chatbot")
    try:
        payload = {
            "question": "¿Cómo está el clima hoy?",
            "conversation_id": None,
            "domains": None
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{base_url}/chatbot/query",
            json=payload,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta recibida: {len(data.get('response', ''))} chars")
            print(f"   📝 Conversation ID: {data.get('conversation_id', 'None')}")
            print(f"   🎯 Intent: {data.get('intent', 'None')}")
            results.append(("Simple Query", True, "Response received"))
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
            results.append(("Simple Query", False, f"Status {response.status_code}"))
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        results.append(("Simple Query", False, str(e)))
    
    # Test 3: Simular consulta con dominios seleccionados
    print("\n3️⃣ Test: Consulta con filtros de dominio")
    try:
        payload = {
            "question": "¿Qué información tienes sobre entrenamiento?",
            "conversation_id": "test-web-123",
            "domains": ["training", "cca"]  # Simular dominios seleccionados
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{base_url}/chatbot/query",
            json=payload,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta con filtros: {len(data.get('response', ''))} chars")
            print(f"   📝 Conversation ID: {data.get('conversation_id', 'None')}")
            results.append(("Filtered Query", True, "Response with domain filters"))
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            results.append(("Filtered Query", False, f"Status {response.status_code}"))
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        results.append(("Filtered Query", False, str(e)))
    
    # Test 4: Verificar manejo de CORS (OPTIONS preflight)
    print("\n4️⃣ Test: CORS Preflight (OPTIONS)")
    try:
        headers = {
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type',
            'Origin': 'http://localhost:3000'
        }
        
        response = requests.options(
            f"{base_url}/chatbot/query",
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        cors_ok = all(header in response.headers for header in cors_headers)
        
        if response.status_code == 200 and cors_ok:
            print(f"   ✅ CORS configurado correctamente")
            print(f"   🌐 Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'None')}")
            results.append(("CORS Preflight", True, "All CORS headers present"))
        else:
            print(f"   ❌ CORS incompleto: Status {response.status_code}")
            print(f"   Headers: {list(response.headers.keys())}")
            results.append(("CORS Preflight", False, "Missing CORS headers"))
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        results.append(("CORS Preflight", False, str(e)))
    
    # Test 5: Simular error de validación (payload inválido)
    print("\n5️⃣ Test: Manejo de errores de validación")
    try:
        payload = {}  # Payload vacío para forzar error de validación
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{base_url}/chatbot/query",
            json=payload,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [400, 422]:  # Bad Request o Unprocessable Entity
            print(f"   ✅ Error de validación manejado correctamente")
            results.append(("Validation Error", True, "Proper error handling"))
        else:
            print(f"   ❌ Error de validación no manejado: Status {response.status_code}")
            results.append(("Validation Error", False, f"Unexpected status {response.status_code}"))
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        results.append(("Validation Error", False, str(e)))
    
    # Resumen final
    print("\n" + "=" * 55)
    print("📊 RESUMEN DE COMUNICACIÓN WEB-TO-API")
    print("=" * 55)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total de tests: {total_tests}")
    print(f"✅ Exitosos: {passed_tests}")
    print(f"❌ Fallidos: {failed_tests}")
    print(f"📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n🔍 TESTS FALLIDOS:")
        for test_name, success, details in results:
            if not success:
                print(f"   • {test_name}: {details}")
    
    # Estado final
    if failed_tests == 0:
        print("\n🎉 ¡COMUNICACIÓN WEB-TO-API COMPLETAMENTE FUNCIONAL!")
        print("   La refactorización no ha afectado la comunicación frontend-backend.")
    else:
        print(f"\n⚠️  HAY {failed_tests} PROBLEMA(S) DE COMUNICACIÓN")
        print("   Revisar la configuración del servidor y/o endpoints.")
    
    return passed_tests, failed_tests

def test_server_availability():
    """Verificar que el servidor esté disponible antes de hacer tests."""
    try:
        response = requests.get("http://localhost:8000/chatbot/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor disponible: {data}")
            return True
        else:
            print(f"❌ Servidor responde con error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servidor no disponible: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando disponibilidad del servidor...")
    
    if not test_server_availability():
        print("\n💡 Para iniciar el servidor:")
        print("   cd meribot_app")
        print("   PYTHONPATH=. uvicorn meribot.core.api.app:app --host 127.0.0.1 --port 8000")
        exit(1)
    
    print("\n🚀 Iniciando tests de comunicación Web-to-API...")
    passed, failed = test_web_to_api_communication()
    
    # Guardar resultados
    results_summary = {
        "test_type": "web_to_api_communication",
        "total_tests": passed + failed,
        "passed": passed,
        "failed": failed,
        "success_rate": (passed / (passed + failed)) * 100,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("web_to_api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: web_to_api_test_results.json")
    
    # Exit code
    exit(0 if failed == 0 else 1)