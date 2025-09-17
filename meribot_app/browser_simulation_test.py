import requests
import time

def test_from_browser_perspective():
    """
    Simula las llamadas que hace el navegador para verificar que todo funciona
    """
    
    base_url = "http://127.0.0.1:8000"
    
    print("🌐 SIMULACIÓN DE PRUEBAS DESDE NAVEGADOR")
    print("=" * 50)
    
    tests = [
        {
            "name": "Health Check",
            "url": f"{base_url}/chatbot/health",
            "method": "GET"
        },
        {
            "name": "Allowed Domains", 
            "url": f"{base_url}/chatbot/allowed_domains",
            "method": "GET"
        },
        {
            "name": "Query Chatbot",
            "url": f"{base_url}/chatbot/query",
            "method": "POST",
            "data": {"query": "Prueba desde navegador", "domain": "training"}
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=5)
            else:
                response = requests.post(test['url'], json=test.get('data'), timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.ok:
                result = response.json()
                print(f"   ✅ Exitoso - {len(str(result))} chars de respuesta")
                if 'intent' in result:
                    print(f"   Intent: {result.get('intent', 'N/A')}")
            else:
                print(f"   ⚠️  Status no-OK: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    print(f"\n{'=' * 50}")
    if all_passed:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("✅ El sistema está listo para pruebas desde navegador")
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON")
        print("🔧 Verificar configuración del servidor")
    
    return all_passed

if __name__ == "__main__":
    success = test_from_browser_perspective()
    
    if success:
        print(f"\n🚀 INSTRUCCIONES PARA EL NAVEGADOR:")
        print(f"   1. Servidor API: http://127.0.0.1:8000")
        print(f"   2. Servidor Web: http://127.0.0.1:3000") 
        print(f"   3. Prueba completa: http://localhost:3000/browser_test.html")
        print(f"   4. Prueba simple: http://localhost:3000/simple_widget_test.html")