"""
config.py
---------
Gestión centralizada de parámetros de configuración del motor de chat MeriBot.
Lee variables desde .env, entorno y valores por defecto.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pydantic import ConfigDict
import os

class MeriBotConfig(BaseSettings):
    model_config = ConfigDict(extra="allow")
    """
    Configuración global del motor de chat MeriBot.
    Los parámetros pueden ser sobreescritos por variables de entorno o archivo .env.
    """
    LLM_MODEL: str = Field('gpt-3.5-turbo', description="Modelo LLM por defecto")
    SYSTEM_PROMPT: str = Field('Eres MeriBot, un asistente conversacional.', description="Prompt base del sistema")
    TEMPERATURE: float = Field(0.7, ge=0.0, le=2.0, description="Temperatura para generación de texto")
    MAX_TOKENS: int = Field(1024, ge=128, le=4096, description="Máximo de tokens por respuesta")

    model_config = ConfigDict(
        env_file=os.getenv('MERIBOT_ENV_FILE', '.env'),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra="allow"
    )

    @validator('LLM_MODEL')
    def model_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('LLM_MODEL no puede estar vacío')
        return v

    @validator('TEMPERATURE')
    def temperature_range(cls, v):
        if not (0.0 <= v <= 2.0):
            raise ValueError('TEMPERATURE fuera de rango (0.0-2.0)')
        return v

    @validator('MAX_TOKENS')
    def tokens_range(cls, v):
        if not (128 <= v <= 4096):
            raise ValueError('MAX_TOKENS fuera de rango (128-4096)')
        return v

# Instancia singleton para uso global
config: MeriBotConfig = MeriBotConfig()

"""
Parámetros configurables:
- LLM_MODEL: Modelo LLM a utilizar (str)
- SYSTEM_PROMPT: Prompt base del sistema (str)
- TEMPERATURE: Temperatura de generación (float, 0.0-2.0)
- MAX_TOKENS: Máximo de tokens por respuesta (int, 128-4096)

Prioridad de carga:
1. Variables de entorno
2. Archivo .env (en raíz del proyecto o ruta definida por MERIBOT_ENV_FILE)
3. Valores por defecto
"""
