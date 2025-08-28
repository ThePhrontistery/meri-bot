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
        user_id: str,
        message: str,
        domain: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje de usuario y retorna la respuesta generada, citaciones y metadatos.
        Flujo: caché -> plugins -> vector search -> LLM.
        """
        session = self.conversation_manager.get_or_create_session(user_id)
        context = session.get_history()
        # 1. Buscar en caché
        cached = self.cache.get(message)
        if cached:
            return {"type": "cache", "response": cached, "citations": [], "source": "cache"}
        # 2. Plugins (pre-LLM)
        plugin_response = await self.plugin_manager.run_pre_llm_plugins(message, context, metadata)
        if plugin_response:
            return {"type": "plugin", "response": plugin_response, "citations": [], "source": "plugin"}
        # 3. Vector search (con filtrado por dominio/metadatos)
        relevant_chunks = self.vector_search.search(message, domain=domain, metadata=metadata)
        citations = [chunk["source"] for chunk in relevant_chunks] if relevant_chunks else []
        # 4. LLM (con contexto y citación)
        llm_metadata = dict(metadata or {})
        if citations:
            llm_metadata["citar_fuentes"] = True
        try:
            response = await self.llm_engine.generate_response(
                message,
                context=context,
                metadata=llm_metadata
            )
        except Exception as e:
            log_generation_failure(user_id, message, str(e))
            response = "[Error al generar respuesta]"
        # 5. Plugins (post-LLM)
        response = await self.plugin_manager.run_post_llm_plugins(response, context, metadata)
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
        user_id: str,
        message: str,
        domain: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Genera respuesta en streaming, orquestando el flujo completo.
        """
        session = self.conversation_manager.get_or_create_session(user_id)
        context = session.get_history()
        # Plugins y caché no soportan streaming, así que solo LLM
        try:
            async for token in self.llm_engine.stream_response(
                message, context=context, metadata=metadata
            ):
                yield token
        except Exception as e:
            log_generation_failure(user_id, message, str(e))
            yield "[Error al generar respuesta]"

    def close_session(self, user_id: str):
        """Cierra la sesión y limpia el historial para el usuario dado."""
        self.conversation_manager.close_session(user_id)

    def get_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Devuelve el historial de mensajes de la sesión activa."""
        session = self.conversation_manager.get_or_create_session(user_id)
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
