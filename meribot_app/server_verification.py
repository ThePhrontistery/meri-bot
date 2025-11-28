import requests
import time

def verify_servers():
    """
    Verifica que ambos servidores estén funcionando correctamente
    """
    
    print("🔍 VERIFICACIÓN DE SERVIDORES")
    print("=" * 40)
    
    # Test API Server
    print("\n🔧 Servidor API (Backend)")
    try:
        api_health = requests.get("http://127.0.0.1:8000/chatbot/health", timeout=3)
        if api_health.status_code == 200:
            print("   ✅ API Server: FUNCIONANDO")
            print(f"   📡 Response: {api_health.json()}")
        else:
            print(f"   ❌ API Server: Error {api_health.status_code}")
    except Exception as e:
        print(f"   ❌ API Server: No responde - {e}")
        return False
    
    # Test Web Server
    print("\n🌐 Servidor Web (Frontend)")
    try:
        web_response = requests.get("http://127.0.0.1:3000/widget-chatbot.html", timeout=3)
        if web_response.status_code == 200:
            print("   ✅ Web Server: FUNCIONANDO")
            print(f"   📄 HTML Size: {len(web_response.text)} chars")
        else:
            print(f"   ❌ Web Server: Error {web_response.status_code}")
    except Exception as e:
        print(f"   ❌ Web Server: No responde - {e}")
        return False
    
    # Test Query Endpoint
    print("\n💬 Test de Query")
    try:
        query_payload = {
            "question": "Hola MeriBot, ¿estás funcionando?",
            "conversation_id": "test_browser",
            "domains": ["training"]
        }
        query_response = requests.post(
            "http://127.0.0.1:8000/chatbot/query", 
            json=query_payload, 
            timeout=10
        )
        if query_response.status_code == 200:
            result = query_response.json()
            print("   ✅ Query Test: FUNCIONANDO")
            print(f"   🤖 Response Length: {len(str(result))} chars")
        else:
            print(f"   ⚠️  Query Test: Status {query_response.status_code}")
    except Exception as e:
        print(f"   ❌ Query Test: Error - {e}")
    
    print(f"\n{'=' * 40}")
    print("🎉 SERVIDORES LISTOS PARA PRUEBAS")
    print(f"\n🌐 ACCEDE AL WIDGET EN TU NAVEGADOR:")
    print(f"   🔗 http://localhost:3000/widget-chatbot.html")
    print(f"\n📋 INFORMACIÓN TÉCNICA:")
    print(f"   🔧 API Backend: http://127.0.0.1:8000")
    print(f"   🌐 Web Frontend: http://127.0.0.1:3000")
    print(f"   📚 Documentación API: http://127.0.0.1:8000/docs")
    
    return True

if __name__ == "__main__":
    success = verify_servers()
    
    if success:
        print(f"\n✅ ¡TODO LISTO!")
        print(f"Copia esta URL en tu navegador:")
        print(f"🔗 http://localhost:3000/widget-chatbot.html")
    else:
        print(f"\n❌ Hay problemas con los servidores")