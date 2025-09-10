from typing import Dict, Optional
from .conversation_context import ConversationContext

class ConversationManager:
    """
    Gestiona la creación y cierre de sesiones de conversación.
    Permite registrar, recuperar y cerrar sesiones activas.
    """
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}

    def get_or_create_session(self, conversation_id: str) -> ConversationContext:
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
