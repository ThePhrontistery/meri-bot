"""
llm_engine.py
Motor de generación de respuestas con LLM para MeriBot CORE.
Soporta integración con Langchain, configuración dinámica, streaming, citación y manejo robusto de errores.
@author: MeriBot Team
"""
import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator
from meribot.core.config import config
from meribot.core.logging import log_generation_failure
from meribot.core.guardrails import apply_guardrails

# Simulación de integración Langchain/LLM (mockable para tests)
class LLMProvider:
    def __init__(self, model: str, params: Dict[str, Any]):
        self.model = model
        self.params = params
    async def generate(self, prompt: str, context: List[str] = None) -> str:
        # Aquí iría la llamada real a Langchain/LLM
        await asyncio.sleep(0.01)
        return f"[LLM:{self.model}] {prompt}"
    async def stream(self, prompt: str, context: List[str] = None) -> AsyncGenerator[str, None]:
        # Simula streaming token a token
        for word in (prompt.split()):
            await asyncio.sleep(0.001)
            yield word + " "

class LLMEngine:
    """
    Motor principal para generación de respuestas con LLM y Langchain.
    Permite configuración dinámica, streaming, citación y manejo de errores.
    """
    def __init__(self, provider: Optional[LLMProvider] = None, guardrails=None, logger=None):
        self.model = config.LLM_MODEL
        self.params = {
            "temperature": getattr(config, "TEMPERATURE", 0.7),
            "max_tokens": getattr(config, "MAX_TOKENS", 512),
            # "top_p": getattr(config, "TOP_P", 1.0),  # Solo si se añade a config
        }
        self.provider = provider or LLMProvider(self.model, self.params)
        # Permite inyectar guardrails y logger para testabilidad
        from meribot.core import guardrails as guardrails_mod
        from meribot.core import logging as logging_mod
        self.guardrails = guardrails or guardrails_mod
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
        # Construir prompt compuesto
        prompt_parts = [system_prompt.strip()]
        if vector_db_texts:
            prompt_parts.append("\n\nContexto relevante extraído de documentos internos:\n" + "\n---\n".join(vector_db_texts))
        if conversation_history:
            for msg in conversation_history:
                prompt_parts.append(f"[{msg['role']}] {msg['content']}")
        prompt_parts.append(f"[user] {user_prompt}")
        full_prompt = "\n".join(prompt_parts)
        safe_prompt = apply_guardrails(full_prompt)
        if safe_prompt is None:
            log_generation_failure(metadata.get("user_id", "unknown") if metadata else "unknown", user_prompt, "Guardrail rejection")
            return "[Input rechazado por política de seguridad]"
        try:
            response = await self.provider.generate(safe_prompt)
            # Simulación de citación automática
            if metadata and metadata.get("citar_fuentes"):
                response += "\n\nFuente: https://ejemplo.com"
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
        prompt_parts = [system_prompt.strip()]
        if vector_db_texts:
            prompt_parts.append("\n\nContexto relevante extraído de documentos internos:\n" + "\n---\n".join(vector_db_texts))
        if conversation_history:
            for msg in conversation_history:
                prompt_parts.append(f"[{msg['role']}] {msg['content']}")
        prompt_parts.append(f"[user] {user_prompt}")
        full_prompt = "\n".join(prompt_parts)
        safe_prompt = self.guardrails.apply_guardrails(full_prompt)
        if safe_prompt is None:
            self.logger.log_guardrail_event(input=user_prompt, type="forbidden_pattern")
            self.logger.log_generation_failure(input=user_prompt, error="Guardrail rejection", user_id=metadata.get("user_id") if metadata else None)
            yield "[Mensaje rechazado por guardrails]"
            return
        try:
            any_token = False
            async for token in self.provider.stream(safe_prompt):
                any_token = True
                yield token
            if not any_token:
                yield "[Error: LLM no generó tokens]"
            if metadata and metadata.get("citar_fuentes"):
                yield "\n\nFuente: https://ejemplo.com"
        except Exception as e:
            self.logger.log_generation_failure(
                metadata.get("user_id") if metadata else None,
                user_prompt,
                str(e)
            )
            yield f"[Error: {str(e)}]"

# Ejemplo de extensión: sustituir LLMProvider por integración real Langchain/OpenAI/Azure
# Configuración avanzada vía config.py
