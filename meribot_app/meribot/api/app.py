
# ======================= IMPORTS =======================
import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core y servicios
from meribot.core.chatengine import ChatEngine
from meribot.services.crawler_endpoint import router as crawler_router
from meribot.services.complete_crawler_endpoint import router as complete_crawler_router
from meribot.services.process_docs_endpoint import router as process_docs_router
from meribot.utils.utils import load_config_from_yaml

# ======================= FIN IMPORTS =======================

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
    domains: Optional[List[str]] = None


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


# Inicializar el core
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
            - domains: (Opcional) Array de dominios para filtrar la búsqueda
        
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

        # Procesar directamente con el core
        core_result = await chat_engine.process_message(
            conversation_id=request.conversation_id or "anonymous",
            message=request.question,
            domains=request.domains
        )
        
        # Devolver la respuesta del core
        core_response = core_result.get("response")
        
        # Manejar errores de validación específicamente
        if core_result.get("type") == "validation_error":
            return {
                "response": core_response,
                "conversation_id": core_result.get("conversation_id"),
                "intent": "validation_error",
                "confidence": 0.0,
                "error": core_result.get("error", "Error de validación"),
                "suggested_questions": []
            }
        
        if core_response and core_response.strip() and core_response.strip() != "[Error al generar respuesta]":
            return {
                "response": core_response,
                "conversation_id": core_result.get("conversation_id"),
                "intent": core_result.get("type", "llm"),
                "confidence": 1.0,
                "citations": core_result.get("citations", []),
                "source": core_result.get("source", "llm"),
                "suggested_questions": []
            }
        else:
            # Si el core no responde adecuadamente, devolver mensaje genérico
            return {
                "response": "Lo siento, no he podido encontrar información relevante para tu pregunta. ¿Podrías reformularla de otra manera?",
                "conversation_id": core_result.get("conversation_id"),
                "intent": "no_answer",
                "confidence": 0.0,
                "suggested_questions": []
            }

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

@app.get(
    "/chatbot/allowed_domains",
    summary="Obtener dominios permitidos",
    description="Devuelve la lista de dominios permitidos según la configuración del crawler.",
    response_description="Lista de dominios permitidos",
    tags=["Chatbot"]
)
async def get_allowed_domains():
    """
    Obtiene la lista de dominios permitidos desde la configuración YAML del crawler.

    Returns:
        dict: Un diccionario con la lista de dominios permitidos.
            {
                "allowed_domains": [...]
            }
    """
    allowed_domains = load_config_from_yaml("allowed_domains")
    if allowed_domains is None:
        raise HTTPException(status_code=404, detail="No se encontraron dominios permitidos en la configuración.")
    return {"allowed_domains": allowed_domains}