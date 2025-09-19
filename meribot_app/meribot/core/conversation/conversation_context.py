
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid, os
from datetime import datetime
from meribot.utils.logging import get_logger

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

    logger = get_logger("meribot.conversation.context", log_file=os.getenv("MERIBOT_LOG_FILE"))

    def add_message(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Añade un mensaje al historial de la conversación.
        :param role: 'user' o 'bot'
        :param content: Texto del mensaje
        :param timestamp: Fecha y hora del mensaje (opcional)
        :raises RuntimeError: Si la conversación está cerrada
        """
        if not self.is_active:
            self.logger.error(f"Intento de añadir mensaje a conversación cerrada: {self.conversation_id}")
            raise RuntimeError(f"La conversación {self.conversation_id} está cerrada.")
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": timestamp or datetime.utcnow()
        })
        self.updated_at = datetime.utcnow()
        self.logger.info(f"Mensaje añadido a conversación {self.conversation_id}: role={role}")

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
        :raises RuntimeError: Si la conversación ya está cerrada
        """
        if not self.is_active:
            self.logger.warning(f"Intento de cerrar conversación ya cerrada: {self.conversation_id}")
            raise RuntimeError(f"La conversación {self.conversation_id} ya está cerrada.")
        self.is_active = False
        self.messages.clear()
        self.updated_at = datetime.utcnow()
        self.logger.info(f"Conversación {self.conversation_id} cerrada correctamente.")
