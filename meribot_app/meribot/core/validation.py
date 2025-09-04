"""
validation.py
Módulo de validación de datos de entrada para el CORE de MeriBot.
Utiliza Pydantic para validar y sanitizar los datos antes del procesamiento.
@author: MeriBot Team
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re


class ChatEngineRequest(BaseModel):
    """
    Modelo de validación para los datos de entrada del ChatEngine.
    Valida conversation_id, message y domains antes del procesamiento.
    """
    
    conversation_id: str = Field(
        ..., 
        description="ID de la conversación para mantener el contexto",
        min_length=1,
        max_length=100
    )
    
    message: str = Field(
        ..., 
        description="Mensaje del usuario a procesar",
        min_length=1,
        max_length=4000
    )
    
    domains: Optional[List[str]] = Field(
        None,
        description="Lista de dominios para filtrar la búsqueda",
        max_items=5
    )

    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        """
        Valida el conversation_id.
        TODO: Implementar validaciones específicas en el futuro:
        - Formato de ID válido
        - Caracteres permitidos
        - Patrones de seguridad
        - Verificación contra base de datos de sesiones activas
        """
        if not v or not v.strip():
            raise ValueError("conversation_id no puede estar vacío")
        
        return v.strip()

    @validator('message')
    def validate_message(cls, v):
        """
        Valida el mensaje del usuario.
        Previene ataques de prompt injection y sanitiza el contenido.
        """
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        
        message = v.strip()
        
        # Detectar patrones de prompt injection
        dangerous_patterns = [
            'ignore previous',
            'ignore all previous',
            'forget previous',
            'system:',
            'assistant:',
            'user:',
            '### instruction',
            '### system',
            'jailbreak',
            'pretend you are',
            'act as if',
            'role:',
            '<|system|>',
            '<|assistant|>',
            '<|user|>'
        ]
        
        message_lower = message.lower()
        for pattern in dangerous_patterns:
            if pattern in message_lower:
                raise ValueError(f"El mensaje contiene patrones potencialmente peligrosos: {pattern}")
        
        # Verificar longitud después de limpiar
        if len(message) > 4000:
            raise ValueError("El mensaje excede la longitud máxima permitida (4000 caracteres)")
        
        # Verificar que no contenga solo espacios en blanco
        if not message.replace(' ', '').replace('\n', '').replace('\t', ''):
            raise ValueError("El mensaje no puede contener solo espacios en blanco")
        
        return message

    @validator('domains')
    def validate_domains(cls, v):
        """
        Valida la lista de dominios permitidos.
        Verifica que los dominios estén en la whitelist de dominios permitidos.
        """
        if v is None:
            return v
        
        # Lista de dominios permitidos (whitelist)
        allowed_domains = [
            'hr',           # Recursos Humanos
            'policies',     # Políticas corporativas
            'intranet',     # Intranet y sistemas internos
            'access',       # Control de acceso
            'tech',         # Tecnología e IT
            'finance',      # Finanzas
            'legal',        # Legal y compliance
            'training',     # Formación y desarrollo
            'benefits',     # Beneficios y compensación
            'procedures',   # Procedimientos operativos
            'security',     # Seguridad corporativa
            'facilities',   # Instalaciones y oficinas
            'projects',     # Gestión de proyectos
            'clients',      # Información de clientes
            'tools'         # Herramientas corporativas
        ]
        
        if not isinstance(v, list):
            raise ValueError("domains debe ser una lista")
        
        # Validar cada dominio
        for domain in v:
            if not isinstance(domain, str):
                raise ValueError("Cada dominio debe ser una cadena de texto")
            
            domain = domain.strip().lower()
            if not domain:
                raise ValueError("Los dominios no pueden estar vacíos")
            
            if domain not in allowed_domains:
                raise ValueError(f"Dominio no permitido: '{domain}'. Dominios permitidos: {', '.join(allowed_domains)}")
        
        # Normalizar dominios (convertir a minúsculas y eliminar espacios)
        normalized_domains = [domain.strip().lower() for domain in v]
        
        # Eliminar duplicados manteniendo el orden
        unique_domains = []
        for domain in normalized_domains:
            if domain not in unique_domains:
                unique_domains.append(domain)
        
        return unique_domains

    class Config:
        """Configuración del modelo Pydantic."""
        str_strip_whitespace = True  # Eliminar espacios automáticamente
        validate_assignment = True   # Validar en asignaciones posteriores
        extra = 'forbid'            # No permitir campos adicionales


def validate_chat_engine_input(
    conversation_id: str,
    message: str,
    domains: Optional[List[str]] = None
) -> ChatEngineRequest:
    """
    Función helper para validar los datos de entrada del ChatEngine.
    
    Args:
        conversation_id: ID de la conversación
        message: Mensaje del usuario
        domains: Lista opcional de dominios para filtrar
        
    Returns:
        ChatEngineRequest: Objeto validado y sanitizado
        
    Raises:
        ValueError: Si algún dato no es válido
        ValidationError: Si la validación de Pydantic falla
    """
    try:
        return ChatEngineRequest(
            conversation_id=conversation_id,
            message=message,
            domains=domains
        )
    except Exception as e:
        # Re-lanzar con mensaje más descriptivo
        raise ValueError(f"Error de validación en datos de entrada: {str(e)}")


# Constantes para reutilización
ALLOWED_DOMAINS = [
    'hr', 'cca', 'onboarding', 'sdo', 'tech', 'finance',
    'legal', 'training', 'benefits', 'procedures', 'security',
    'facilities', 'projects', 'clients', 'tools'
]

MAX_MESSAGE_LENGTH = 4000
MAX_CONVERSATION_ID_LENGTH = 100
MAX_DOMAINS_COUNT = 5
