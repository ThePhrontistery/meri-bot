from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the question processor
from meribot.nlp.processor import QuestionProcessor

app = FastAPI(
    title="MeriBot API",
    description="API para el servicio de chatbot de C&CA",
    version="0.1.0"
)

# Configuración de CORS
from meribot.services.crawler_endpoint import router as crawler_router
from meribot.services.complete_crawler_endpoint import router as complete_crawler_router
from meribot.services.process_docs_endpoint import router as process_docs_router
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
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    return JSONResponse(content={"status": "ok"}, headers=headers)

app.include_router(crawler_router)
app.include_router(complete_crawler_router)
app.include_router(process_docs_router)

# Initialize the question processor
question_processor = QuestionProcessor()

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
        
        # Process the question using our processor
        result = question_processor.process_question(request.question)
        
        # Add conversation ID to the response if provided
        result["conversation_id"] = request.conversation_id
        
        return result
        
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
