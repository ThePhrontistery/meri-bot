#!/usr/bin/env python3
"""
Script de simulación para mostrar la estructura de request/response del API
"""

print("🤖 SIMULACIÓN DE ENVÍO Y RESPUESTA DEL API MERIBOT")
print("=" * 60)

# Simulación de peticiones de ejemplo
test_cases = [
    {
        "name": "Pregunta básica sin dominios",
        "request": {
            "question": "¿Qué es Capgemini?",
            "conversation_id": "test-conversation-001"
        },
        "expected_response": {
            "response": "Capgemini es una empresa multinacional de consultoría de tecnología e innovación...",
            "conversation_id": "test-conversation-001",
            "intent": "llm",
            "confidence": 1.0,
            "citations": ["documento1.pdf", "intranet-capgemini.html"],
            "source": "llm",
            "suggested_questions": []
        }
    },
    {
        "name": "Pregunta con filtro de dominios",
        "request": {
            "question": "¿Cuáles son las políticas de recursos humanos?",
            "conversation_id": "test-conversation-002",
            "domains": ["hr", "policies"]
        },
        "expected_response": {
            "response": "Las políticas de recursos humanos de Capgemini incluyen...",
            "conversation_id": "test-conversation-002",
            "intent": "llm", 
            "confidence": 1.0,
            "citations": ["politicas_rrhh.pdf", "manual_empleado.docx"],
            "source": "llm",
            "suggested_questions": []
        }
    },
    {
        "name": "Pregunta sin conversation_id",
        "request": {
            "question": "¿Cómo puedo acceder a la intranet?",
            "domains": ["intranet", "access"]
        },
        "expected_response": {
            "response": "Para acceder a la intranet de Capgemini debes...",
            "conversation_id": None,
            "intent": "llm",
            "confidence": 1.0,
            "citations": ["guia_acceso.pdf"],
            "source": "llm",
            "suggested_questions": []
        }
    },
    {
        "name": "Respuesta de error",
        "request": {
            "question": "¿Cuál es el sentido de la vida?",
            "conversation_id": "test-conversation-004"
        },
        "expected_response": {
            "response": "Lo siento, no he podido encontrar información relevante para tu pregunta. ¿Podrías reformularla de otra manera?",
            "conversation_id": "test-conversation-004",
            "intent": "no_answer",
            "confidence": 0.0,
            "suggested_questions": []
        }
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n📤 CASO DE PRUEBA {i}: {test_case['name']}")
    print("-" * 50)
    
    print("🔹 REQUEST (POST /chatbot/query):")
    print("   URL: http://127.0.0.1:8000/chatbot/query")
    print("   Headers: Content-Type: application/json")
    print("   Body:")
    for key, value in test_case['request'].items():
        print(f"     {key}: {repr(value)}")
    
    print("\n🔹 EXPECTED RESPONSE:")
    print("   Status: 200 OK")
    print("   Content-Type: application/json")
    print("   Body:")
    for key, value in test_case['expected_response'].items():
        if isinstance(value, str) and len(value) > 60:
            print(f"     {key}: {repr(value[:60] + '...')}")
        else:
            print(f"     {key}: {repr(value)}")
    
    print("\n" + "=" * 60)

print("\n🏁 SIMULACIÓN COMPLETADA")
print("\n📋 RESUMEN DEL FLUJO:")
print("1. La API recibe una petición POST en /chatbot/query")
print("2. Se valida el request según el modelo QueryRequest")
print("3. Se llama a chat_engine.process_message() con:")
print("   - conversation_id: ID de la conversación")
print("   - message: La pregunta del usuario")
print("   - domains: Lista de dominios para filtrar (opcional)")
print("4. El core procesa la petición:")
print("   - Busca en caché")
print("   - Ejecuta plugins pre-LLM")
print("   - Realiza búsqueda vectorial con filtros")
print("   - Genera respuesta con LLM")
print("   - Ejecuta plugins post-LLM")
print("5. Se devuelve la respuesta estructurada al cliente")

print("\n🔧 PARÁMETROS DE ENTRADA SOPORTADOS:")
print("- question (str): Pregunta del usuario [REQUERIDO]")
print("- conversation_id (str, opcional): ID de conversación")
print("- domains (List[str], opcional): Filtros de dominio")

print("\n📤 ESTRUCTURA DE RESPUESTA:")
print("- response (str): Respuesta generada")
print("- conversation_id (str): ID de conversación")
print("- intent (str): Tipo de respuesta (llm, cache, plugin, no_answer, error)")
print("- confidence (float): Nivel de confianza (0.0-1.0)")
print("- citations (List[str]): Fuentes consultadas")
print("- source (str): Origen de la respuesta")
print("- suggested_questions (List[str]): Preguntas sugeridas")
