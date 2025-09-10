import os
from typing import Any, Dict, List, Optional, AsyncGenerator
from meribot.core.logging import log_generation_failure
from meribot.core import logging as logging_mod
from .llm_provider import LLMProvider

class LLMEngine:
    def _build_full_prompt(self, system_prompt: str, conversation_history: List[Dict], user_prompt: str = None, vector_db_texts: List[str] = None) -> str:
        """
        Construye el prompt compuesto para el LLM a partir del prompt de sistema, historial, mensaje de usuario y textos vectoriales.
        """
        prompt_parts = [system_prompt.strip()]
        if vector_db_texts:
            prompt_parts.append("\n\nContexto relevante extraído de documentos internos:\n" + "\n---\n".join(vector_db_texts))
        if conversation_history:
            for msg in conversation_history:
                prompt_parts.append(f"[{msg['role']}] {msg['content']}")
        if user_prompt is not None:
            prompt_parts.append(f"[user] {user_prompt}")
        return "\n".join(prompt_parts)
    """
    Motor principal para generación de respuestas con LLM y Langchain.
    Permite configuración dinámica, streaming, citación y manejo de errores.
    """
    def __init__(self, provider: Optional[LLMProvider] = None, logger=None):
        # Cargar parámetros del entorno
        self.model = os.getenv('LLM_MODEL')
        temp = os.getenv('TEMPERATURE')
        max_tokens = os.getenv('MAX_TOKENS')
        self.params = {
            "temperature": float(temp) if temp is not None else 0.7,
            "max_tokens": int(max_tokens) if max_tokens is not None else 512,
        }
        self.provider = provider or LLMProvider(self.model, self.params)
        # Permite inyectar logger para testabilidad
        self.logger = logger or logging_mod

    async def generate_response(self, system_prompt: str, conversation_history: List[Dict], user_prompt: str, vector_db_texts: List[str], metadata: Dict[str, Any] = None) -> str:
        """
        Genera una respuesta usando el LLM, aplicando guardrails y citando fuentes si corresponde.
        :param system_prompt: Instrucción de sistema
        :param conversation_history: Historial de conversación (lista de mensajes)
        :param user_prompt: Mensaje actual del usuario
        :param vector_db_texts: Lista de textos recuperados de la base vectorial
        :param metadata: Metadatos opcionales
        :return: Respuesta generada o mensaje de error
        """
        full_prompt = self._build_full_prompt(system_prompt, conversation_history, user_prompt, vector_db_texts)
        try:
            response = await self.provider.generate(full_prompt, user_prompt)
            return response
        except Exception as e:
            log_generation_failure(metadata.get("user_id", "unknown") if metadata else "unknown", user_prompt, str(e))
            return "[Error al generar respuesta]"

    async def stream_response(self, system_prompt: str, conversation_history: List[Dict], user_prompt: str, vector_db_texts: List[str], metadata: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """
        Genera una respuesta en modo streaming (token a token).
        :param system_prompt: Instrucción de sistema
        :param conversation_history: Historial de conversación (lista de mensajes)
        :param user_prompt: Mensaje actual del usuario
        :param vector_db_texts: Lista de textos recuperados de la base vectorial
        :param metadata: Metadatos opcionales
        :yield: Fragmentos de la respuesta
        """
        full_prompt = self._build_full_prompt(system_prompt, conversation_history, user_prompt, vector_db_texts)
        try:
            any_token = False
            async for token in self.provider.stream(full_prompt):
                any_token = True
                yield token
            if not any_token:
                yield "[Error: LLM no generó tokens]"
            # Si se requiere citar fuentes, aquí se puede añadir lógica dinámica
        except Exception as e:
            self.logger.log_generation_failure(
                metadata.get("user_id") if metadata else None,
                user_prompt,
                str(e)
            )
            yield f"[Error: {str(e)}]"
