
"""
validation.py
Valida y sanitiza los datos de entrada para el CORE de MeriBot usando Pydantic.
"""
import os
import yaml
from typing import List, Optional
from pydantic import BaseModel, Field, validator

# Configuración global: se carga una sola vez al importar el módulo
CRAWLER_CONFIG_PATH = os.path.abspath(os.getenv('CRAWLER_CONFIG_PATH', 'crawler_config.yaml'))

def load_config_from_yaml():
    """
    Carga la configuración desde crawler_config.yaml.
    Devuelve dict con dominios permitidos, límites y patrones peligrosos.
    """
    if not os.path.exists(CRAWLER_CONFIG_PATH):
        return {
            'ALLOWED_DOMAINS': [],
            'MAX_MESSAGE_LENGTH': None,
            'MAX_CONVERSATION_ID_LENGTH': None,
            'MAX_DOMAINS_COUNT': None,
            'DANGEROUS_PATTERNS': []
        }
    try:
        with open(CRAWLER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        allowed_domains = config.get('allowed_domains', [])
        if not isinstance(allowed_domains, list) or not all(isinstance(d, str) for d in allowed_domains):
            allowed_domains = []
        allowed_domains = [d.strip().lower() for d in allowed_domains if d.strip()]
        dangerous_patterns = config.get('dangerous_patterns', [])
        if not isinstance(dangerous_patterns, list) or not all(isinstance(p, str) for p in dangerous_patterns):
            dangerous_patterns = []
        return {
            'ALLOWED_DOMAINS': allowed_domains,
            'MAX_MESSAGE_LENGTH': int(config.get('max_message_length')) if config.get('max_message_length') is not None else None,
            'MAX_CONVERSATION_ID_LENGTH': int(config.get('max_conversation_id_length')) if config.get('max_conversation_id_length') is not None else None,
            'MAX_DOMAINS_COUNT': int(config.get('max_domains_count')) if config.get('max_domains_count') is not None else None,
            'DANGEROUS_PATTERNS': dangerous_patterns
        }
    except Exception:
        return {
            'ALLOWED_DOMAINS': [],
            'MAX_MESSAGE_LENGTH': None,
            'MAX_CONVERSATION_ID_LENGTH': None,
            'MAX_DOMAINS_COUNT': None,
            'DANGEROUS_PATTERNS': []
        }



# Cargar configuración global y asegurar valores por defecto
CONFIG = load_config_from_yaml()
ALLOWED_DOMAINS = CONFIG['ALLOWED_DOMAINS']
if not ALLOWED_DOMAINS:
    raise RuntimeError("No se pudo cargar la lista de dominios permitidos desde crawler_config.yaml. Revisa la ruta y el contenido del archivo.")
MAX_MESSAGE_LENGTH = CONFIG['MAX_MESSAGE_LENGTH'] if CONFIG['MAX_MESSAGE_LENGTH'] is not None else 4000
MAX_CONVERSATION_ID_LENGTH = CONFIG['MAX_CONVERSATION_ID_LENGTH'] if CONFIG['MAX_CONVERSATION_ID_LENGTH'] is not None else 100
MAX_DOMAINS_COUNT = CONFIG['MAX_DOMAINS_COUNT'] if CONFIG['MAX_DOMAINS_COUNT'] is not None else 5
DANGEROUS_PATTERNS = CONFIG['DANGEROUS_PATTERNS']

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

# --- Helper para validación externa ---
def validate_chat_engine_input(conversation_id: str, message: str, domains: Optional[List[str]] = None) -> ChatEngineRequest:
    """
    Valida los datos de entrada y devuelve un objeto ChatEngineRequest.
    Lanza ValueError si los datos no son válidos.
    """
    try:
        return ChatEngineRequest(
            conversation_id=conversation_id,
            message=message,
            domains=domains
        )
    except Exception as e:
        raise ValueError(f"Error de validación en datos de entrada: {str(e)}")



