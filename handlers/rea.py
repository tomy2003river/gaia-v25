"""
Rea handler - Nature queries for GAIA v25.
"""
import logging
from typing import Dict, Optional
from handlers.base import BaseHandler
from core.errors import Response

logger = logging.getLogger(__name__)


class ReaHandler(BaseHandler):
    """Handler for nature, animals, and plants queries."""
    
    def __init__(self):
        """Initialize Rea handler."""
        super().__init__(name="REA", priority=60)
        
        # Simple knowledge base (can be extended with external API)
        self.nature_facts = {
            "árbol": "Los árboles son fundamentales para la vida en la Tierra. Producen oxígeno, absorben CO2, y proveen hábitat para innumerables especies.",
            "pájaro": "Las aves son vertebrados de sangre caliente con plumas, picos y capacidad de vuelo (en la mayoría). Existen más de 10,000 especies.",
            "ecosistema": "Un ecosistema es un sistema biológico formado por una comunidad de organismos vivos y su ambiente físico, interactuando como una unidad.",
            "planta": "Las plantas son organismos autótrofos que realizan fotosíntesis, convirtiendo luz solar en energía química. Son la base de la mayoría de cadenas alimentarias.",
            "animal": "Los animales son organismos multicelulares heterótrofos que se alimentan de otros organismos. Incluyen desde invertebrados microscópicos hasta grandes mamíferos.",
            "flora": "La flora se refiere al conjunto de plantas de una región o período específico. Es esencial para el equilibrio ecológico.",
            "fauna": "La fauna es el conjunto de animales de una región o período. Su diversidad indica la salud del ecosistema.",
            "bosque": "Los bosques cubren aproximadamente 31% de la superficie terrestre y albergan el 80% de la biodiversidad terrestre.",
            "océano": "Los océanos cubren el 71% de la superficie terrestre y contienen el 97% del agua del planeta. Son cruciales para el clima global.",
            "selva": "Las selvas tropicales, aunque cubren solo el 6% de la Tierra, albergan más del 50% de las especies del planeta.",
        }
    
    def can_handle(self, message: str, context: Optional[Dict] = None) -> bool:
        """Check if message is nature-related."""
        return True
    
    def handle(self, message: str, context: Optional[Dict] = None) -> Response:
        """
        Handle nature query.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            Response with nature information
        """
        # Extract topic from message
        topic = self._extract_topic(message)
        
        if not topic:
            return Response(
                text="Puedo hablarte sobre árboles, animales, plantas, ecosistemas y la naturaleza en general. ¿Qué te interesa saber?",
                intent="REA",
                success=True
            )
        
        # Look for matching fact
        fact = self._find_fact(topic)
        
        if fact:
            text = self._format_response(topic, fact)
            return Response(
                text=text,
                intent="REA",
                success=True,
                metadata={"topic": topic}
            )
        else:
            # Generic nature response
            text = f"La naturaleza es sabia. Sobre {topic}, te puedo decir que forma parte del delicado equilibrio de nuestro ecosistema. Cada elemento en la naturaleza tiene su rol."
            return Response(
                text=text,
                intent="REA",
                success=True,
                metadata={"topic": topic, "source": "generic"}
            )
    
    def _extract_topic(self, message: str) -> Optional[str]:
        """
        Extract nature topic from message.
        
        Args:
            message: User message
            
        Returns:
            Topic string or None
        """
        message_lower = message.lower()
        
        # Check for direct matches in our knowledge base
        for keyword in self.nature_facts.keys():
            if keyword in message_lower:
                return keyword
        
        # Check for related terms
        nature_terms = {
            "arboles": "árbol",
            "tree": "árbol",
            "bird": "pájaro",
            "pajaros": "pájaro",
            "plantas": "planta",
            "plant": "planta",
            "animales": "animal",
            "animals": "animal",
            "forest": "bosque",
            "jungle": "selva",
            "ocean": "océano",
            "sea": "océano",
        }
        
        for term, canonical in nature_terms.items():
            if term in message_lower:
                return canonical
        
        return None
    
    def _find_fact(self, topic: str) -> Optional[str]:
        """
        Find fact for topic.
        
        Args:
            topic: Topic to look up
            
        Returns:
            Fact string or None
        """
        return self.nature_facts.get(topic)
    
    def _format_response(self, topic: str, fact: str) -> str:
        """
        Format response in Rea's personality.
        
        Args:
            topic: Topic
            fact: Fact text
            
        Returns:
            Formatted response
        """
        # Rea speaks with reverence for nature
        responses = [
            f"La naturaleza nos enseña sobre {topic}: {fact}",
            f"Déjame hablarte sobre {topic}. {fact}",
            f"En la naturaleza, {topic} es fascinante: {fact}",
        ]
        
        import random
        return random.choice(responses)
