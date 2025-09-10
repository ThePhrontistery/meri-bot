
"""
validation.py
Valida y sanitiza los datos de entrada para el CORE de MeriBot usando Pydantic.
"""
import os
from meribot.utils.utils import load_config_from_yaml
from typing import List, Optional
from pydantic import BaseModel, Field, validator

# Configuración global: se carga una sola vez al importar el módulo
CRAWLER_CONFIG_PATH = os.path.abspath(os.getenv('CRAWLER_CONFIG_PATH', 'crawler_config.yaml'))

# Cargar configuración global y asegurar valores por defecto usando la función genérica
ALLOWED_DOMAINS = load_config_from_yaml('allowed_domains')
if not ALLOWED_DOMAINS:
    raise RuntimeError("No se pudo cargar la lista de dominios permitidos desde crawler_config.yaml. Revisa la ruta y el contenido del archivo.")
ALLOWED_DOMAINS = [d.strip().lower() for d in ALLOWED_DOMAINS if isinstance(d, str) and d.strip()]
MAX_MESSAGE_LENGTH = load_config_from_yaml('max_message_length')
MAX_MESSAGE_LENGTH = int(MAX_MESSAGE_LENGTH) if MAX_MESSAGE_LENGTH is not None else 4000
MAX_CONVERSATION_ID_LENGTH = load_config_from_yaml('max_conversation_id_length')
MAX_CONVERSATION_ID_LENGTH = int(MAX_CONVERSATION_ID_LENGTH) if MAX_CONVERSATION_ID_LENGTH is not None else 100
MAX_DOMAINS_COUNT = load_config_from_yaml('max_domains_count')
MAX_DOMAINS_COUNT = int(MAX_DOMAINS_COUNT) if MAX_DOMAINS_COUNT is not None else 5
DANGEROUS_PATTERNS = load_config_from_yaml('dangerous_patterns')
DANGEROUS_PATTERNS = [p for p in DANGEROUS_PATTERNS if isinstance(p, str)] if DANGEROUS_PATTERNS else []

# --- Modelo principal de validación ---
class ChatEngineRequest(BaseModel):
    """
    Valida los datos de entrada del ChatEngine: conversation_id, message y domains.
    """
    conversation_id: str = Field(
        ..., description="ID de la conversación para mantener el contexto",
        min_length=1, max_length=MAX_CONVERSATION_ID_LENGTH
    )
    message: str = Field(
        ..., description="Mensaje del usuario a procesar",
        min_length=1, max_length=MAX_MESSAGE_LENGTH
    )
    domains: Optional[List[str]] = Field(
        None, description="Lista de dominios para filtrar la búsqueda",
        max_items=MAX_DOMAINS_COUNT
    )

    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        if not v or not v.strip():
            raise ValueError("conversation_id no puede estar vacío")
        return v.strip()

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        message = v.strip()
        # Detectar patrones peligrosos
        message_lower = message.lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in message_lower:
                raise ValueError(f"El mensaje contiene patrones potencialmente peligrosos: {pattern}")
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"El mensaje excede la longitud máxima permitida ({MAX_MESSAGE_LENGTH} caracteres)")
        if not message.replace(' ', '').replace('\n', '').replace('\t', ''):
            raise ValueError("El mensaje no puede contener solo espacios en blanco")
        return message

    @validator('domains')
    def validate_domains(cls, v):
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("domains debe ser una lista")
        if not ALLOWED_DOMAINS:
            raise ValueError("No se pudo cargar la lista de dominios permitidos desde crawler_config.yaml")
        # Validar cada dominio
        for domain in v:
            if not isinstance(domain, str):
                raise ValueError("Cada dominio debe ser una cadena de texto")
            domain = domain.strip().lower()
            if not domain:
                raise ValueError("Los dominios no pueden estar vacíos")
            if domain not in ALLOWED_DOMAINS:
                raise ValueError(f"Dominio no permitido: '{domain}'. Dominios permitidos: {', '.join(ALLOWED_DOMAINS)}")
        # Normalizar y eliminar duplicados manteniendo el orden
        normalized_domains = [domain.strip().lower() for domain in v]
        unique_domains = []
        for domain in normalized_domains:
            if domain not in unique_domains:
                unique_domains.append(domain)
        return unique_domains

    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        extra = 'forbid'




