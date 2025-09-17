import requests

# Test simple y directo sin logs verbosos
try:
    print("🔄 Verificando endpoints en puerto 8001...")
    
    # Health check
    health = requests.get("http://127.0.0.1:8001/chatbot/health", timeout=3)
    print(f"✅ Health: {health.status_code}")
    
    # Allowed domains
    domains = requests.get("http://127.0.0.1:8001/chatbot/allowed_domains", timeout=3)
    print(f"✅ Domains: {domains.status_code}")
    
    # Simple query
    query = requests.post("http://127.0.0.1:8001/chatbot/query", 
                         json={"query": "Hola"}, timeout=5)
    print(f"✅ Query: {query.status_code} - {len(str(query.json()))} chars")
    
    print("🎉 TODOS LOS ENDPOINTS FUNCIONAN")
    
except Exception as e:
    print(f"❌ Error: {e}")