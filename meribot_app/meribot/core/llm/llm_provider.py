import os
import asyncio
import requests
import json
from typing import Any, Dict, AsyncGenerator

class LLMProvider:
    def __init__(self, model: str, params: Dict[str, Any]):
        self.model = model
        self.params = params
        # Cargar variables de Azure OpenAI directamente del entorno
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        self.azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION')

    async def generate(self, prompt: str, user_prompt: str) -> str:
        """
        Llama al endpoint de Azure OpenAI para obtener una respuesta generada por el modelo.
        """
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
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error Azure OpenAI]: {str(e)}"

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Simula streaming token a token.
        """
        for word in prompt.split():
            await asyncio.sleep(0.001)
            yield word + " "
