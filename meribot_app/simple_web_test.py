import requests
import json

# Test 1: Allowed domains (igual que en el widget)
print("🔍 Test 1: Allowed domains")
r = requests.get('http://127.0.0.1:8000/chatbot/allowed_domains')
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

# Test 2: Chatbot query simple 
print("\n🔍 Test 2: Chatbot query simple")
payload = {
    'question': 'Hola, ¿cómo estás?',
    'conversation_id': None
}
r2 = requests.post('http://127.0.0.1:8000/chatbot/query', 
                   json=payload, 
                   headers={'Content-Type': 'application/json'})
print(f"Status: {r2.status_code}")
data = r2.json()
print(f"Response length: {len(data.get('response', ''))} chars")
print(f"Conversation ID: {data.get('conversation_id', 'None')}")
print(f"Intent: {data.get('intent', 'None')}")

# Test 3: Query con dominios (igual que en el widget)
print("\n🔍 Test 3: Query con dominios")
payload2 = {
    'question': 'Información sobre training',
    'conversation_id': 'test-123',
    'domains': ['training', 'cca']
}
r3 = requests.post('http://127.0.0.1:8000/chatbot/query', 
                   json=payload2, 
                   headers={'Content-Type': 'application/json'})
print(f"Status: {r3.status_code}")
data3 = r3.json()
print(f"Response length: {len(data3.get('response', ''))} chars")
print(f"✅ Web-to-API communication working!")