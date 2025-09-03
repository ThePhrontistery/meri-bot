"""
llm_engine.py
Motor de generación de respuestas con LLM para MeriBot CORE.
Soporta integración con Langchain, configuración dinámica, streaming, citación y manejo robusto de errores.
@author: MeriBot Team
"""
import asyncio
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, AsyncGenerator
load_dotenv()
from meribot.core.logging import log_generation_failure
from meribot.core.guardrails import apply_guardrails

# Simulación de integración Langchain/LLM (mockable para tests)
class LLMProvider:
    def __init__(self, model: str, params: Dict[str, Any]):
        self.model = model
        self.params = params
        # Cargar variables de Azure OpenAI directamente del entorno
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        self.azure_embeddings_deployment = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT')
        self.azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
    async def generate(self, prompt: str, user_prompt: str, context: List[str] = None) -> str:
        """
        Llama al endpoint de Azure OpenAI para obtener una respuesta generada por el modelo.
        """
        import requests
        import json
        # Construir mensajes para el modelo tipo chat
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_prompt}
        ]
        url = f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}/chat/completions?api-version={self.azure_api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.azure_api_key
        }
        payload = {
            "messages": messages,
            "temperature": self.params.get("temperature", 0.7),
            "max_tokens": self.params.get("max_tokens", 512)
        }
        try:
            # Ejecutar la petición en un hilo para no bloquear el event loop
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            )
            response.raise_for_status()
            result = response.json()
            # Extraer el texto generado
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error Azure OpenAI]: {str(e)}"
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
        # Cargar parámetros del entorno
        self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        self.params = {
            "temperature": float(os.getenv('TEMPERATURE', 0.7)),
            "max_tokens": int(os.getenv('MAX_TOKENS', 512)),
            # "top_p": float(os.getenv('TOP_P', 1.0)),  # Si se añade a .env
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
        # prompt_parts.append(f"[user] {user_prompt}")
        full_prompt = "\n".join(prompt_parts)
        safe_prompt = apply_guardrails(full_prompt)
        if safe_prompt is None:
            log_generation_failure(metadata.get("user_id", "unknown") if metadata else "unknown", user_prompt, "Guardrail rejection")
            return "[Input rechazado por política de seguridad]"
        try:
            response = await self.provider.generate(safe_prompt,user_prompt)
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
