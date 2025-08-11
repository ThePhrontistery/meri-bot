"""
Question processing module for MeriBot.

This module handles the natural language understanding and processing of user questions.
"""
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionProcessor:
    """Processes user questions and generates appropriate responses."""
    
    def __init__(self):
        """Initialize the question processor with necessary models and data."""
        # TODO: Load any required models or data here
        self.greetings = ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos"]
        self.farewells = ["adiós", "hasta luego", "hasta pronto", "chao", "nos vemos"]
        
        # Simple intent classification patterns
        self.intent_patterns = {
            "greeting": self.greetings,
            "farewell": self.farewells,
            "help": ["ayuda", "qué puedes hacer", "cómo funciona"],
            "thanks": ["gracias", "muchas gracias", "te lo agradezco"],
        }
        
        # Knowledge base (in a real application, this would be in a database)
        self.knowledge_base = {
            "horario": "Nuestro horario de atención es de lunes a viernes de 8:00 a 18:00.",
            "contacto": "Puedes contactarnos en el correo contacto@ceca.com o al teléfono +34 123 456 789.",
            "ubicación": "Nuestras oficinas están ubicadas en Calle Ejemplo 123, Madrid, España.",
            "servicios": "Ofrecemos servicios de consultoría, desarrollo de software y formación.",
        }
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a user question and generate a response.
        
        Args:
            question: The user's question as a string.
            
        Returns:
            dict: A dictionary containing the response and metadata.
        """
        # Convert to lowercase for case-insensitive matching
        question_lower = question.lower().strip()
        
        # Check for empty question
        if not question_lower:
            return self._create_response("Por favor, formula una pregunta.")
        
        # Check for greetings
        if any(greeting in question_lower for greeting in self.greetings):
            return self._create_response(
                "¡Hola! Soy MeriBot, tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            )
        
        # Check for farewells
        if any(farewell in question_lower for farewell in self.farewells):
            return self._create_response(
                "¡Hasta luego! Si tienes más preguntas, no dudes en volver a preguntar."
            )
        
        # Check for help
        if any(help_word in question_lower for help_word in self.intent_patterns["help"]):
            return self._create_response(
                "Puedo ayudarte con información sobre nuestros servicios, horarios, contacto y más. "
                "¿Sobre qué te gustaría saber?"
            )
        
        # Check for thanks
        if any(thanks_word in question_lower for thanks_word in self.intent_patterns["thanks"]):
            return self._create_response(
                "¡De nada! Estoy aquí para ayudarte. ¿Hay algo más en lo que pueda asistirte?"
            )
        
        # Check knowledge base for direct matches
        for keyword, answer in self.knowledge_base.items():
            if keyword in question_lower:
                return self._create_response(answer)
        
        # Default response if no specific intent is matched
        return self._create_response(
            "Lo siento, no tengo información específica sobre eso. "
            "¿Podrías reformular tu pregunta o preguntar sobre otro tema?"
        )
    
    def _create_response(self, message: str, intent: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a standardized response object.
        
        Args:
            message: The response message to send to the user.
            intent: The detected intent, if any.
            
        Returns:
            dict: A standardized response object.
        """
        return {
            "response": message,
            "intent": intent,
            "confidence": 1.0 if intent else 0.0,
            "suggested_questions": self._get_suggested_questions(intent) if intent else []
        }
    
    def _get_suggested_questions(self, intent: str) -> list:
        """
        Get suggested follow-up questions based on the detected intent.
        
        Args:
            intent: The detected intent.
            
        Returns:
            list: A list of suggested follow-up questions.
        """
        suggestions = {
            "greeting": [
                "¿Cuáles son vuestros horarios de atención?",
                "¿Dónde estáis ubicados?",
                "¿Qué servicios ofrecen?"
            ],
            "farewell": [],
            "help": [
                "¿Cuál es vuestra dirección?",
                "¿Cómo puedo contactar con soporte?",
                "¿Qué tipo de servicios ofrecen?"
            ],
            "thanks": [
                "¿Neitas ayuda con algo más?",
                "¿Te gustaría programar una cita?",
                "¿Hay algo más en lo que pueda asistirte?"
            ]
        }
        
        return suggestions.get(intent, [])
