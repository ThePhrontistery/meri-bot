import requests
import json

url = "http://localhost:8000/chatbot/query"
headers = {
    "Content-Type": "application/json"
}
data = {
    "question": "Hello, can you hear me?",
    "conversation_id": "test-conversation-123"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())
except Exception as e:
    print(f"Error: {e}")
