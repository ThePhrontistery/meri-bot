# conversation.py
# Gestión de conversaciones y contexto para MeriBot

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid
from datetime import datetime

@dataclass
class ConversationContext:
    """
    Representa el contexto de una conversación activa en MeriBot.
    Incluye identificador único, historial de mensajes, estado y metadatos.

    El historial de mensajes se mantiene durante toda la sesión activa y puede recuperarse
    mediante el método get_history().
    """
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Dict] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)

    def add_message(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Añade un mensaje al historial de la conversación.
        :param role: 'user' o 'bot'
        :param content: Texto del mensaje
        :param timestamp: Fecha y hora del mensaje (opcional)
        """
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": timestamp or datetime.utcnow()
        })
        self.updated_at = datetime.utcnow()

    def get_history(self) -> List[Dict]:
        """
        Devuelve el historial completo de mensajes de la sesión activa.
        :return: Lista de mensajes (cada uno con role, content, timestamp)
        """
        return self.messages.copy()

    def close(self):
        """
        Marca la conversación como cerrada y elimina el historial de mensajes.
        Llamar a este método al cerrar el panel de conversación para garantizar que no se conserve el historial.
        """
        self.is_active = False
        self.messages.clear()
        self.updated_at = datetime.utcnow()


class ConversationManager:
    """
    Gestiona la creación y cierre de sesiones de conversación.
    Permite registrar, recuperar y cerrar sesiones activas.
    """
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}

    def get_or_create_session(self, conversation_id: str) -> 'ConversationContext':
        """
        Devuelve la sesión activa para el conversation_id o la crea si no existe.
        Si conversation_id es 'anonymous' o vacío, genera uno nuevo.
        """
        if not conversation_id or conversation_id.lower() == "anonymous":
            context = ConversationContext()
            self.sessions[context.conversation_id] = context
            return context
        if conversation_id in self.sessions:
            return self.sessions[conversation_id]
        context = ConversationContext(conversation_id=conversation_id)
        self.sessions[context.conversation_id] = context
        return context

    def create_session(self, metadata: Optional[Dict] = None) -> ConversationContext:
        """
        Crea una nueva sesión de conversación y la registra.
        :param metadata: Metadatos adicionales (opcional)
        :return: Instancia de ConversationContext
        """
        context = ConversationContext(metadata=metadata or {})
        self.sessions[context.conversation_id] = context
        return context

    def get_session(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        Recupera una sesión de conversación por su ID.
        :param conversation_id: ID de la conversación
        :return: Instancia de ConversationContext o None
        """
        return self.sessions.get(conversation_id)

    def close_session(self, conversation_id: str) -> bool:
        """
        Cierra y elimina una sesión de conversación.
        :param conversation_id: ID de la conversación
        :return: True si se cerró correctamente, False si no existe
        """
        context = self.sessions.get(conversation_id)
        if context:
            context.close()
            del self.sessions[conversation_id]
            return True
        return False
