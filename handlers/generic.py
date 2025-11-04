"""
Generic handler - Fallback for unclassified queries.
"""
import logging
import random
from typing import Dict, Optional
from handlers.base import BaseHandler
from core.errors import Response

logger = logging.getLogger(__name__)


class GenericHandler(BaseHandler):
    """Fallback handler for generic queries."""
    
    def __init__(self):
        """Initialize Generic handler."""
        super().__init__(name="GENERIC", priority=10)
        
        self.greetings = [
            "¡Hola! Soy GAIA, tu asistente multimodal. ¿En qué puedo ayudarte?",
            "¡Saludos! Estoy aquí para asistirte. ¿Qué necesitas?",
            "Hola, ¿cómo puedo ayudarte hoy?",
        ]
        
        self.farewells = [
            "¡Hasta luego! Fue un placer ayudarte.",
            "¡Adiós! Que tengas un excelente día.",
            "Nos vemos pronto. Cuídate.",
        ]
        
        self.unknown = [
            "No estoy segura de cómo ayudarte con eso. Puedo ayudarte con el clima, información general, naturaleza, o recordar conversaciones anteriores.",
            "Interesante pregunta. Mis especialidades son clima, conocimiento general, naturaleza y memoria. ¿Puedo ayudarte con algo de eso?",
            "No comprendo completamente tu pregunta. ¿Podrías reformularla? Puedo ayudarte con clima, información, naturaleza o memoria.",
        ]
    
    def can_handle(self, message: str, context: Optional[Dict] = None) -> bool:
        """Generic handler can handle anything."""
        return True
    
    def handle(self, message: str, context: Optional[Dict] = None) -> Response:
        """
        Handle generic query.
        
        Args:
            message: User message
            context: Optional context with intent info
            
        Returns:
            Response
        """
        message_lower = message.lower()
        
        # Check intent from context
        intent = context.get("intent", "GENERIC") if context else "GENERIC"
        
        # Handle greetings
        if intent == "GREETING" or any(word in message_lower for word in ["hola", "buenos días", "buenas tardes", "hey"]):
            text = random.choice(self.greetings)
            return Response(
                text=text,
                intent="GREETING",
                success=True
            )
        
        # Handle farewells
        if intent == "FAREWELL" or any(word in message_lower for word in ["adiós", "chau", "hasta luego", "bye"]):
            text = random.choice(self.farewells)
            return Response(
                text=text,
                intent="FAREWELL",
                success=True
            )
        
        # Handle help requests
        if "ayuda" in message_lower or "help" in message_lower or "puedes hacer" in message_lower:
            return self._handle_help()
        
        # Unknown query
        text = random.choice(self.unknown)
        return Response(
            text=text,
            intent="GENERIC",
            success=True,
            metadata={"fallback": True}
        )
    
    def _handle_help(self) -> Response:
        """Handle help request."""
        text = """Soy GAIA, tu asistente multimodal. Puedo ayudarte con:

🌤️ **Clima**: Pregúntame sobre el tiempo en cualquier ciudad
📚 **Conocimiento**: Pídeme información sobre cualquier tema
🌿 **Naturaleza**: Háblame sobre animales, plantas y ecosistemas
🧠 **Memoria**: Puedo recordar nuestras conversaciones

Algunos ejemplos:
- "¿Qué tiempo hace en Madrid?"
- "Cuéntame sobre Albert Einstein"
- "¿Qué sabes sobre los océanos?"
- "¿De qué hablamos ayer?"
"""
        
        return Response(
            text=text,
            intent="HELP",
            success=True
        )
