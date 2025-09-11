#!/usr/bin/env python3
"""
Script para simular una petición POST al endpoint del chatbot
"""
import requests
import json

# URL del endpoint
url = "http://127.0.0.1:8000/chatbot/query"

# Datos de la petición - simulando diferentes escenarios
test_cases = [
    {
        "name": "Pregunta básica sin dominios",
        "data": {
            "question": "¿Qué es Capgemini?",
            "conversation_id": "test-conversation-001"
        }
    },
    {
        "name": "Pregunta con filtro de dominios",
        "data": {
            "question": "¿Cuáles son las políticas de recursos humanos?",
            "conversation_id": "test-conversation-002", 
            "domains": ["hr", "policies"]
        }
    },
    {
        "name": "Pregunta sin conversation_id",
        "data": {
            "question": "¿Cómo puedo acceder a la intranet?",
            "domains": ["intranet", "access"]
        }
    },
    {
        "name": "Pregunta con message vacío",
        "data": {
            "question": "",
            "conversation_id": "test-conversation-003",
            "domains": ["test"]
        }
    }
]

# Headers
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("🤖 Simulación de peticiones al API de MeriBot")
print("=" * 50)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n📤 Test Case {i}: {test_case['name']}")
    print("-" * 40)
    
    try:
        # Realizar la petición POST
        response = requests.post(url, json=test_case['data'], headers=headers, timeout=30)
        
        print(f"📋 Request Body:")
        print(json.dumps(test_case['data'], indent=2, ensure_ascii=False))
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📥 Response Body:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # Mostrar información clave
            print(f"\n✅ Información clave:")
            print(f"   • Respuesta: {response_data.get('response', 'N/A')[:100]}{'...' if len(response_data.get('response', '')) > 100 else ''}")
            print(f"   • Tipo/Intent: {response_data.get('intent', 'N/A')}")
            print(f"   • Confianza: {response_data.get('confidence', 'N/A')}")
            print(f"   • Citaciones: {len(response_data.get('citations', []))}")
            print(f"   • Fuente: {response_data.get('source', 'N/A')}")
        else:
            print(f"❌ Error en la respuesta:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n" + "=" * 50)

print("\n🏁 Simulación completada")
