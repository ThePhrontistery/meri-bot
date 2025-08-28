from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Import the question processor y el core
from meribot.nlp.processor import QuestionProcessor
from meribot.core.chatengine import ChatEngine

app = FastAPI(
    title="MeriBot API",
    description="API para el servicio de chatbot de C&CA",
    version="0.1.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET"],  # Explicitly list allowed methods
    allow_headers=["*"],
    expose_headers=["*"],
)

class QueryRequest(BaseModel):
    """Modelo para las peticiones de consulta al chatbot."""
    question: str
    conversation_id: Optional[str] = None

@app.options("/chatbot/query")
async def options_chatbot():
    """Handle OPTIONS for CORS preflight"""
    response = JSONResponse(content={"status": "ok"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# Inicializar el question processor y el core
question_processor = QuestionProcessor()
chat_engine = ChatEngine()

@app.post(
    "/chatbot/query",
    summary="Chatbot Query Endpoint",
    description="""
    Procesa preguntas del usuario y devuelve respuestas del chatbot.
    
    Este endpoint acepta preguntas en lenguaje natural y devuelve respuestas
    generadas por el sistema de IA del chatbot.
    """,
    response_description="Respuesta del chatbot con metadatos adicionales"
)
async def query_chatbot(request: QueryRequest, response: Response):
    """
    Procesa una pregunta del usuario y devuelve una respuesta del chatbot.
    
    Args:
        request (QueryRequest): Contiene:
            - question: La pregunta del usuario como texto
            - conversation_id: (Opcional) ID de conversación para mantener contexto
        
    Returns:
        dict: Un diccionario con:
            - response: La respuesta del chatbot
            - conversation_id: ID de la conversación
            - intent: El intent detectado (si aplica)
            - confidence: Nivel de confianza de la respuesta (0.0 a 1.0)
            - suggested_questions: Preguntas sugeridas relacionadas
    """
    try:
        # Set CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"

        # 1. Procesar primero con el NLP
        nlp_result = question_processor.process_question(request.question)
        pred_intents = {"greeting", "farewell", "help", "thanks"}
        # Si el intent es uno de los predeterminados, responder directamente
        if nlp_result.get("intent") in pred_intents and nlp_result["confidence"] > 0.0:
            nlp_result["conversation_id"] = request.conversation_id
            return nlp_result

        # 2. Si no, pasar al core
        core_result = await chat_engine.process_message(
            user_id=request.conversation_id or "anonymous",
            message=request.question
        )
        # Si el core responde con algo útil, devolverlo
        core_response = core_result.get("response")
        if core_response and core_response.strip() and core_response.strip() != "[Error al generar respuesta]":
            return {
                "response": core_response,
                "conversation_id": request.conversation_id,
                "intent": core_result.get("type", "llm"),
                "confidence": 1.0,
                "citations": core_result.get("citations", []),
                "source": core_result.get("source", "llm"),
                "suggested_questions": []
            }

        # 3. Si el core no responde, fallback a la respuesta genérica del NLP
        nlp_result["conversation_id"] = request.conversation_id
        return nlp_result

    except Exception as e:
        # Log the error for debugging
        print(f"Error processing question: {str(e)}")
        # Return a user-friendly error message
        return {
            "response": "Lo siento, ha ocurrido un error al procesar tu pregunta. Por favor, inténtalo de nuevo más tarde.",
            "error": str(e),
            "conversation_id": request.conversation_id,
            "intent": "error",
            "confidence": 0.0,
            "suggested_questions": []
        }

@app.get(
    "/chatbot/health",
    summary="Check Service Status",
    description="Verifica el estado del servicio y devuelve el estado actual.",
    response_description="Estado actual del servicio",
    tags=["Chatbot"]
)
async def health_check():
    """
    Verifica el estado del servicio del chatbot.
    
    Returns:
        dict: Un diccionario con el estado actual del servicio
            {
                "status": "ok",
                "service": "meribot-api"
            }
    """
    return {"status": "ok", "service": "meribot-api"}
