import requests
import json

def test_validation_fix():
    """
    Prueba el fix del error de validación de dominios
    """
    
    print("🔧 VERIFICACIÓN DEL FIX DE VALIDACIÓN")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Query sin domains (debe funcionar ahora)
    print("\n1️⃣ Test: Query sin dominios especificados")
    try:
        payload = {
            "question": "Hola, ¿cómo estás?"
            # No incluimos domains para probar que None funciona
        }
        
        response = requests.post(f"{base_url}/chatbot/query", 
                               json=payload, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Éxito - Respuesta: {len(str(result))} chars")
            print(f"   Intent: {result.get('intent', 'N/A')}")
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"   ❌ Error de validación: {error_detail}")
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Query con domains válidos
    print("\n2️⃣ Test: Query con dominios válidos")
    try:
        payload = {
            "question": "¿Qué información tienes sobre formación?",
            "domains": ["training"]  # Usar 'domains' como array
        }
        
        response = requests.post(f"{base_url}/chatbot/query", 
                               json=payload, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Éxito - Respuesta: {len(str(result))} chars")
        else:
            error_detail = response.json()
            print(f"   ❌ Error: {error_detail}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Verificar allowed_domains endpoint
    print("\n3️⃣ Test: Endpoint allowed_domains")
    try:
        response = requests.get(f"{base_url}/chatbot/allowed_domains", timeout=5)
        
        if response.status_code == 200:
            domains = response.json()
            print(f"   ✅ Dominios disponibles: {domains}")
        else:
            print(f"   ❌ Error obteniendo dominios: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n{'=' * 40}")
    print("🎯 Fix aplicado. Prueba desde navegador:")
    print(f"   📍 Widget: http://localhost:3001/widget-chatbot.html")
    print(f"   🔧 API: http://127.0.0.1:8002")

if __name__ == "__main__":
    test_validation_fix()