"""
chatengine.py
Coordinador principal del CORE de MeriBot. Orquesta plugins, vector search y LLM.
Proporciona una interfaz asíncrona y extensible para la API y otros módulos.
"""

import os

from typing import Any, Dict, List, Optional, AsyncGenerator
from meribot.core.plugins.plugin_manager import PluginManager
 
from meribot.core.llm.llm_engine import LLMEngine
from meribot.core.conversation import ConversationManager
from meribot.core.db.chromadb_connector import ChromaDBConnector
from meribot.core.logger import get_logger, log_generation_failure
from meribot.core.validation import ChatEngineRequest

# Importar la función utilitaria desde config
from meribot.core.config import load_system_prompt

logger = get_logger("meribot.core", log_file=os.getenv("MERIBOT_LOG_FILE"))

class ChatEngine:
    """
    Punto de entrada principal del CORE. Gestiona el flujo conversacional,
    orquesta plugins, búsqueda vectorial y LLM, y expone una API asíncrona.
    """
    def __init__(
        self,
        plugin_manager: Optional[PluginManager] = None,
        chromadb_connector: Optional[ChromaDBConnector] = None,
        llm_engine: Optional[LLMEngine] = None,
        conversation_manager: Optional[ConversationManager] = None,
    ):
        self.plugin_manager = plugin_manager or PluginManager()
        self.chroma_connector = chromadb_connector or ChromaDBConnector()
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
    # Validar datos de entrada
        try:
            validated_input = ChatEngineRequest(
                conversation_id=conversation_id,
                message=message,
                domains=domains
            )
            conversation_id = validated_input.conversation_id
            message = validated_input.message
            domains = validated_input.domains
        except Exception as e:
            return {
                "type": "validation_error",
                "response": f"Error de validación: {str(e)}",
                "citations": [],
                "source": "validation",
                "error": str(e)
            }

    # Obtener contexto de la conversación
        session = self.conversation_manager.get_or_create_session(conversation_id)
        conversation_history = session.get_history()

        # Buscar en la base vectorial
        relevant_chunks = self.chroma_connector.similarity_search(query_text=message, domains=domains)
        citations = []
        seen = set()
        if relevant_chunks:
            for chunk in relevant_chunks:
                meta = chunk.get("metadatas", {})
                title = meta.get("title")
                url = meta.get("url")
                key = (title, url)
                if key not in seen:
                    seen.add(key)
                    citations.append({"title": title, "url": url})
        vector_db_texts = [chunk.get("document") for chunk in relevant_chunks] if relevant_chunks else []

    # ...

    # Preparar metadatos para el LLM
        llm_metadata = {}
        if citations:
            llm_metadata["citar_fuentes"] = True
        if relevant_chunks:
            for chunk in relevant_chunks:
                if "metadata" in chunk:
                    llm_metadata.update(chunk["metadata"])

    # Preparar argumentos para el LLM
        system_prompt = load_system_prompt()
        user_prompt = message

    # ...


    # Llamar al LLM para generar la respuesta
        try:
            response = await self.llm_engine.generate_response(
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                user_prompt=user_prompt,
                vector_db_texts=vector_db_texts,
                metadata=llm_metadata
            )
        except Exception as e:
            log_generation_failure(logger, conversation_id, message, str(e))
            response = "[Error al generar respuesta]"

    # Actualizar historial de la conversación
        session.add_message("user", message)
        session.add_message("assistant", response)
    # ...

    # Retornar respuesta y citaciones
        return {
            "type": "llm",
            "response": response,
            "citations": citations,
            "source": "llm",
            "conversation_id": session.conversation_id,
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
            validated_input = ChatEngineRequest(
                conversation_id=conversation_id,
                message=message,
                domains=domains
            )
            conversation_id = validated_input.conversation_id
            message = validated_input.message
            domains = validated_input.domains
        except Exception as e:
            yield f"[Error de validación: {str(e)}]"
            return

        # 2. Obtener contexto de la conversación
        session = self.conversation_manager.get_or_create_session(conversation_id)
        conversation_history = session.get_history()

        # 3. Buscar en la base vectorial (usando todos los dominios recibidos)
        relevant_chunks = self.chroma_connector.similarity_search(query_text=message, domains=domains)
        citations = []
        seen = set()
        if relevant_chunks:
            for chunk in relevant_chunks:
                meta = chunk.get("metadatas", {})
                title = meta.get("title")
                url = meta.get("url")
                key = (title, url)
                if key not in seen:
                    seen.add(key)
                    citations.append({"title": title, "url": url})
        vector_db_texts = [chunk.get("document") for chunk in relevant_chunks] if relevant_chunks else []
        llm_metadata = {}
        if citations:
            llm_metadata["citar_fuentes"] = True
        if relevant_chunks:
            for chunk in relevant_chunks:
                if "metadata" in chunk:
                    llm_metadata.update(chunk["metadata"])
        system_prompt = load_system_prompt()
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
            log_generation_failure(logger, conversation_id, message, str(e))
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
