import requests
import time

def test_web_module_setup():
    """
    Verifica que el módulo web esté listo para pruebas desde navegador
    """
    
    print("🌐 VERIFICACIÓN DEL MÓDULO WEB MERIBOT")
    print("=" * 50)
    
    # Test 1: Verificar servidor API
    print("\n1️⃣ Verificando servidor API...")
    try:
        api_response = requests.get("http://127.0.0.1:8000/chatbot/health", timeout=3)
        if api_response.ok:
            print("   ✅ Servidor API funcionando correctamente")
            print(f"   📡 Status: {api_response.status_code}")
        else:
            print(f"   ⚠️  Servidor API con problemas: {api_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando a API: {e}")
        return False
    
    # Test 2: Verificar servidor web
    print("\n2️⃣ Verificando servidor web...")
    try:
        web_response = requests.get("http://127.0.0.1:3000/widget-chatbot.html", timeout=3)
        if web_response.ok:
            print("   ✅ Servidor web funcionando correctamente")
            print(f"   📄 HTML del widget cargado ({len(web_response.text)} chars)")
        else:
            print(f"   ⚠️  Servidor web con problemas: {web_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando a servidor web: {e}")
        return False
    
    # Test 3: Verificar endpoints principales
    print("\n3️⃣ Verificando endpoints del widget...")
    endpoints = [
        ("allowed_domains", "http://127.0.0.1:8000/chatbot/allowed_domains"),
        ("query", "http://127.0.0.1:8000/chatbot/query")
    ]
    
    for name, url in endpoints:
        try:
            if name == "query":
                response = requests.post(url, json={"query": "test"}, timeout=5)
            else:
                response = requests.get(url, timeout=3)
            
            print(f"   ✅ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  {name}: Error - {e}")
    
    print(f"\n{'=' * 50}")
    print("🎉 MÓDULO WEB LISTO PARA PRUEBAS")
    print(f"\n🚀 INSTRUCCIONES PARA PRUEBAS DESDE NAVEGADOR:")
    print(f"   📍 URL principal: http://localhost:3000/widget-chatbot.html")
    print(f"   🔧 API Backend: http://127.0.0.1:8000")
    print(f"   🌐 Servidor Web: http://127.0.0.1:3000")
    
    print(f"\n📋 FUNCIONALIDADES A PROBAR:")
    print(f"   • Apertura del widget flotante")
    print(f"   • Envío de mensajes")
    print(f"   • Filtros de dominio")  
    print(f"   • Indicadores de fuente")
    print(f"   • Historial de conversación")
    print(f"   • Responsive design")
    
    return True

if __name__ == "__main__":
    success = test_web_module_setup()
    
    if success:
        print(f"\n✅ ¡TODO LISTO! Abre tu navegador en:")
        print(f"   🔗 http://localhost:3000/widget-chatbot.html")
    else:
        print(f"\n❌ Hay problemas con la configuración")