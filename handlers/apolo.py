"""
Apolo handler - Knowledge queries for GAIA v25.
"""
import logging
from typing import Dict, Optional
from handlers.base import BaseHandler
from core.errors import Response
from services.wikipedia import WikipediaService

logger = logging.getLogger(__name__)


class ApoloHandler(BaseHandler):
    """Handler for knowledge and information queries."""
    
    def __init__(self, wikipedia_service: WikipediaService):
        """
        Initialize Apolo handler.
        
        Args:
            wikipedia_service: Wikipedia service instance
        """
        super().__init__(name="APOLO", priority=70)
        self.wikipedia_service = wikipedia_service
    
    def can_handle(self, message: str, context: Optional[Dict] = None) -> bool:
        """Check if message is knowledge-related."""
        return True
    
    def handle(self, message: str, context: Optional[Dict] = None) -> Response:
        """
        Handle knowledge query.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            Response with knowledge information
        """
        # Extract query from message
        query = self._extract_query(message)
        
        if not query:
            return Response(
                text="¿Sobre qué tema deseas que te cuente?",
                intent="APOLO",
                success=True
            )
        
        try:
            # Search Wikipedia
            titles = self.wikipedia_service.search(query, limit=3)
            
            if not titles:
                return Response(
                    text=f"No encontré información sobre '{query}' en mis fuentes. ¿Podrías reformular la pregunta?",
                    intent="APOLO",
                    success=True,
                    metadata={"query": query, "results": 0}
                )
            
            # Get summary of first result
            summary_data = self.wikipedia_service.get_summary(titles[0])
            
            if not summary_data:
                return Response(
                    text=f"Encontré referencias a '{query}', pero no pude obtener los detalles. Intenta de nuevo.",
                    intent="APOLO",
                    success=False,
                    metadata={"query": query}
                )
            
            # Format response in Apolo's style
            text = self._format_response(summary_data, titles)
            
            return Response(
                text=text,
                intent="APOLO",
                success=True,
                metadata={
                    "query": query,
                    "title": summary_data["title"],
                    "url": summary_data["url"],
                    "alternatives": titles[1:] if len(titles) > 1 else []
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Apolo handler: {e}")
            return Response(
                text=f"Ocurrió un error al buscar información sobre '{query}'. Intenta de nuevo más tarde.",
                intent="APOLO",
                success=False,
                error=str(e)
            )
    
    def _extract_query(self, message: str) -> Optional[str]:
        """
        Extract query topic from message.
        
        Args:
            message: User message
            
        Returns:
            Query string or None
        """
        import re
        
        # Patterns to extract query
        patterns = [
            r'(?:qué\s+sabes\s+de|saber\s+de|cuéntame\s+sobre|háblame\s+de|información\s+sobre)\s+(.+)',
            r'(?:quién\s+es|qué\s+es)\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                # Clean up
                query = re.sub(r'[?.!]$', '', query)
                return query
        
        # If no pattern matches, use the whole message (cleaned)
        query = re.sub(r'^(apolo|oye|hey|dime)\s+', '', message, flags=re.IGNORECASE)
        query = re.sub(r'[?.!]$', '', query).strip()
        
        return query if len(query) > 2 else None
    
    def _format_response(self, summary_data: Dict, titles: list) -> str:
        """
        Format knowledge response in Apolo's personality.
        
        Args:
            summary_data: Wikipedia summary data
            titles: List of matching titles
            
        Returns:
            Formatted response text
        """
        title = summary_data["title"]
        summary = summary_data["summary"]
        
        # Apolo speaks as a knowledgeable guide
        response = f"Según mis fuentes, sobre {title}: "
        
        # Trim summary to reasonable length
        if len(summary) > 400:
            # Find last sentence within 400 chars
            truncated = summary[:400]
            last_period = truncated.rfind('.')
            if last_period > 200:
                summary = summary[:last_period + 1]
            else:
                summary = truncated + "..."
        
        response += summary
        
        # Suggest alternatives if available
        if len(titles) > 1:
            alternatives = ", ".join(titles[1:3])
            response += f" (También encontré información sobre: {alternatives})"
        
        return response
