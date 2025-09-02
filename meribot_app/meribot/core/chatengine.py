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
        Flujo: validación -> caché -> plugins -> vector search -> LLM.
        """
        # 0. Validar datos de entrada
        try:
            validated_input = validate_chat_engine_input(
                conversation_id=conversation_id,
                message=message,
                domains=domains
            )
            # Usar los datos validados y sanitizados
            conversation_id = validated_input.conversation_id
            message = validated_input.message
            domains = validated_input.domains
        except ValueError as e:
            # Retornar error de validación
            return {
                "type": "validation_error",
                "response": f"Error de validación: {str(e)}",
                "citations": [],
                "source": "validation",
                "error": str(e)
            }
        
        session = self.conversation_manager.get_or_create_session(conversation_id)
        context = session.get_history()
        # 1. Buscar en caché
        cached = self.cache.get(message)
        if cached:
            return {"type": "cache", "response": cached, "citations": [], "source": "cache"}
        # 2. Plugins (pre-LLM)
        plugin_response = await self.plugin_manager.run_pre_llm_plugins(message, context)
        if plugin_response:
            return {"type": "plugin", "response": plugin_response, "citations": [], "source": "plugin"}
        # 3. Vector search (con filtrado por dominios)
        # Convertir la lista de dominios en un dominio único para la búsqueda (usar el primero si existe)
        domain = domains[0] if domains and len(domains) > 0 else None
        relevant_chunks = self.vector_search.search(message, domain=domain)
        citations = [chunk["source"] for chunk in relevant_chunks] if relevant_chunks else []
        
        # 4. LLM (con contexto y citación)
        # Los metadatos se construyen internamente a partir de la búsqueda vectorial
        llm_metadata = {}
        if citations:
            llm_metadata["citar_fuentes"] = True
        # Agregar metadatos recuperados de los chunks si existen
        if relevant_chunks:
            for chunk in relevant_chunks:
                if "metadata" in chunk:
                    llm_metadata.update(chunk["metadata"])
        try:
            response = await self.llm_engine.generate_response(
                message,
                context=context,
                metadata=llm_metadata
            )
        except Exception as e:
            log_generation_failure(conversation_id, message, str(e))
            response = "[Error al generar respuesta]"
        # 5. Plugins (post-LLM)
        response = await self.plugin_manager.run_post_llm_plugins(response, context)
        # 6. Actualizar historial y caché
        session.add_message("user", message)
        session.add_message("assistant", response)
        self.cache.set(message, response)
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
        """
        # 0. Validar datos de entrada
        try:
            validated_input = validate_chat_engine_input(
                conversation_id=conversation_id,
                message=message,
                domains=domains
            )
            # Usar los datos validados y sanitizados
            conversation_id = validated_input.conversation_id
            message = validated_input.message
            domains = validated_input.domains
        except ValueError as e:
            yield f"[Error de validación: {str(e)}]"
            return
        
        session = self.conversation_manager.get_or_create_session(conversation_id)
        context = session.get_history()
        # Plugins y caché no soportan streaming, así que solo LLM
        try:
            async for token in self.llm_engine.stream_response(
                message, context=context
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
