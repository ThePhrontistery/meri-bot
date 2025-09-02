"""
chatengine.py
Coordinador principal del CORE de MeriBot. Orquesta plugins, vector search, caché y LLM.
Proporciona una interfaz asíncrona y extensible para la API y otros módulos.
@author: MeriBot Team
"""
from typing import Any, Dict, List, Optional, AsyncGenerator
from meribot.core.plugin_manager import PluginManager
from meribot.core.vector_search import VectorSearch
from meribot.core.cache import ResponseCache
from meribot.core.llm_engine import LLMEngine
from meribot.core.conversation import ConversationManager
from meribot.core.logging import log_generation_failure
from meribot.core.validation import validate_chat_engine_input
import os

class ChatEngine:
    """
    Punto de entrada principal del CORE. Gestiona el flujo conversacional,
    orquesta plugins, vector search, caché y LLM, y expone una API asíncrona.
    """
    def __init__(
        self,
        plugin_manager: Optional[PluginManager] = None,
        vector_search: Optional[VectorSearch] = None,
        cache: Optional[ResponseCache] = None,
        llm_engine: Optional[LLMEngine] = None,
        conversation_manager: Optional[ConversationManager] = None,
    ):
        self.plugin_manager = plugin_manager or PluginManager()
        self.vector_search = vector_search or VectorSearch()
        self.cache = cache or ResponseCache()
        self.llm_engine = llm_engine or LLMEngine()
        self.conversation_manager = conversation_manager or ConversationManager()

    async def process_message(
        self,
        conversation_id: str,
        message: str,
        domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje de usuario y retorna la respuesta generada, citaciones y metadatos.
        Flujo: validación -> obtención de contexto -> búsqueda vectorial -> LLM -> actualización de historial.
        """
        # 1. Validar datos de entrada
        try:
            validated_input = validate_chat_engine_input(
                conversation_id=conversation_id,
                message=message,
                domains=domains
            )
            conversation_id = validated_input.conversation_id
            message = validated_input.message
            domains = validated_input.domains
        except ValueError as e:
            return {
                "type": "validation_error",
                "response": f"Error de validación: {str(e)}",
                "citations": [],
                "source": "validation",
                "error": str(e)
            }

        # 2. Obtener contexto de la conversación
        session = self.conversation_manager.get_or_create_session(conversation_id)
        conversation_history = session.get_history()

        # 3. Buscar en la base vectorial (usando todos los dominios recibidos)
        relevant_chunks = self.vector_search.search(message, domains=domains)
        citations = [chunk["source"] for chunk in relevant_chunks] if relevant_chunks else []
        vector_db_texts = [chunk.get("document") for chunk in relevant_chunks] if relevant_chunks else []

        # 4. Preparar metadatos para el LLM
        llm_metadata = {}
        if citations:
            llm_metadata["citar_fuentes"] = True
        if relevant_chunks:
            for chunk in relevant_chunks:
                if "metadata" in chunk:
                    llm_metadata.update(chunk["metadata"])

        # 5. Preparar argumentos para el LLM
        system_prompt = os.getenv("SYSTEM_PROMPT", "")
        user_prompt = message

        # 6. Llamar al LLM para generar la respuesta
        try:
            response = await self.llm_engine.generate_response(
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                user_prompt=user_prompt,
                vector_db_texts=vector_db_texts,
                metadata=llm_metadata
            )
        except Exception as e:
            log_generation_failure(conversation_id, message, str(e))
            response = "[Error al generar respuesta]"

        # 7. Actualizar historial de la conversación
        session.add_message("user", message)
        session.add_message("assistant", response)

        # 8. Retornar respuesta y citaciones
        return {
            "type": "llm",
            "response": response,
            "citations": citations,
            "source": "llm",
        }

    async def stream_response(
        self,
        conversation_id: str,
        message: str,
        domains: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Genera respuesta en streaming, orquestando el flujo completo.
        Flujo: validación -> obtención de contexto -> búsqueda vectorial -> LLM (streaming).
        """
        # 1. Validar datos de entrada
        try:
            validated_input = validate_chat_engine_input(
                conversation_id=conversation_id,
                message=message,
                domains=domains
            )
            conversation_id = validated_input.conversation_id
            message = validated_input.message
            domains = validated_input.domains
        except ValueError as e:
            yield f"[Error de validación: {str(e)}]"
            return

        # 2. Obtener contexto de la conversación
        session = self.conversation_manager.get_or_create_session(conversation_id)
        conversation_history = session.get_history()

        # 3. Buscar en la base vectorial (usando todos los dominios recibidos)
        relevant_chunks = self.vector_search.search(message, domains=domains)
        vector_db_texts = [chunk.get("document") for chunk in relevant_chunks] if relevant_chunks else []
        llm_metadata = {}
        citations = [chunk["source"] for chunk in relevant_chunks] if relevant_chunks else []
        if citations:
            llm_metadata["citar_fuentes"] = True
        if relevant_chunks:
            for chunk in relevant_chunks:
                if "metadata" in chunk:
                    llm_metadata.update(chunk["metadata"])
        system_prompt = os.getenv("SYSTEM_PROMPT", "")
        user_prompt = message

        # 4. Llamar al LLM en modo streaming
        try:
            async for token in self.llm_engine.stream_response(
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                user_prompt=user_prompt,
                vector_db_texts=vector_db_texts,
                metadata=llm_metadata
            ):
                yield token
        except Exception as e:
            log_generation_failure(conversation_id, message, str(e))
            yield "[Error al generar respuesta]"

    def close_session(self, conversation_id: str):
        """Cierra la sesión y limpia el historial para la conversación dada."""
        self.conversation_manager.close_session(conversation_id)

    def get_context(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Devuelve el historial de mensajes de la sesión activa."""
        session = self.conversation_manager.get_or_create_session(conversation_id)
        return session.get_history()

    # Métodos de filtrado avanzado
    def filter_chunks(self, chunks, domain=None, metadata=None):
        """Filtra fragmentos por dominio y metadatos."""
        if domain:
            chunks = [c for c in chunks if c.get("domain") == domain]
        if metadata:
            for k, v in metadata.items():
                chunks = [c for c in chunks if c.get(k) == v]
        return chunks
