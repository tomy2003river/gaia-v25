"""
Hades handler - Memory and past events for GAIA v25.
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from handlers.base import BaseHandler
from core.errors import Response
from core.memory import Memory

logger = logging.getLogger(__name__)


class HadesHandler(BaseHandler):
    """Handler for memory and past events queries."""
    
    def __init__(self, memory: Memory):
        """
        Initialize Hades handler.
        
        Args:
            memory: Memory service instance
        """
        super().__init__(name="HADES", priority=90)
        self.memory = memory
    
    def can_handle(self, message: str, context: Optional[Dict] = None) -> bool:
        """Check if message is memory-related."""
        return True
    
    def handle(self, message: str, context: Optional[Dict] = None) -> Response:
        """
        Handle memory query.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            Response with memory information
        """
        message_lower = message.lower()
        
        # Check for memory reset command
        if "olvida" in message_lower or "borra" in message_lower or "reset" in message_lower:
            return self._handle_reset()
        
        # Check for summary request
        if "resumen" in message_lower or "resúmen" in message_lower:
            return self._handle_summary()
        
        # Search memory
        keywords = self._extract_keywords(message)
        
        if not keywords:
            return self._handle_recent()
        
        # Search for specific content
        results = []
        for keyword in keywords:
            results.extend(self.memory.search(keyword, limit=3))
        
        if not results:
            return Response(
                text="No recuerdo nada sobre eso en nuestras conversaciones recientes.",
                intent="HADES",
                success=True,
                metadata={"query": keywords}
            )
        
        # Format response
        text = self._format_search_results(results, keywords)
        
        return Response(
            text=text,
            intent="HADES",
            success=True,
            metadata={"query": keywords, "results": len(results)}
        )
    
    def _handle_reset(self) -> Response:
        """Handle memory reset request."""
        self.memory.clear()
        return Response(
            text="He borrado mi memoria de nuestras conversaciones. Empecemos de nuevo.",
            intent="HADES",
            success=True,
            metadata={"action": "reset"}
        )
    
    def _handle_summary(self) -> Response:
        """Handle memory summary request."""
        summary = self.memory.get_summary()
        topics = self.memory.get_topics()
        
        if summary["total_events"] == 0:
            return Response(
                text="Aún no tengo memoria de nuestras conversaciones.",
                intent="HADES",
                success=True
            )
        
        # Format summary
        text = f"He registrado {summary['total_events']} interacciones. "
        
        if topics:
            top_topics = [t[0] for t in topics[:3]]
            text += f"Los temas principales han sido: {', '.join(top_topics)}."
        
        return Response(
            text=text,
            intent="HADES",
            success=True,
            metadata=summary
        )
    
    def _handle_recent(self) -> Response:
        """Handle request for recent memories."""
        recent = self.memory.get_recent(5)
        
        if not recent:
            return Response(
                text="No tengo recuerdos recientes de nuestras conversaciones.",
                intent="HADES",
                success=True
            )
        
        # Format recent memories
        text = "En nuestras conversaciones recientes hemos hablado sobre: "
        topics = [r.get("topic", "varios temas") for r in recent]
        text += ", ".join(set(topics)) + "."
        
        return Response(
            text=text,
            intent="HADES",
            success=True,
            metadata={"recent_count": len(recent)}
        )
    
    def _extract_keywords(self, message: str) -> list:
        """
        Extract keywords from message for memory search.
        
        Args:
            message: User message
            
        Returns:
            List of keywords
        """
        import re
        
        # Remove common words
        stopwords = {
            'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'al',
            'que', 'qué', 'sobre', 'hablamos', 'dijimos', 'recuerda',
            'recordar', 'ayer', 'antes', 'pasado'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b\w+\b', message.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        
        return keywords[:3]  # Limit to 3 keywords
    
    def _format_search_results(self, results: list, keywords: list) -> str:
        """
        Format search results.
        
        Args:
            results: Search results from memory
            keywords: Search keywords
            
        Returns:
            Formatted text
        """
        # Hades speaks about the past with gravity
        text = f"Sobre {', '.join(keywords)}, recuerdo que "
        
        # Get unique topics from results
        topics = set()
        for result in results:
            topic = result.get("topic", "")
            if topic:
                topics.add(topic)
        
        if topics:
            text += f"hablamos de: {', '.join(list(topics)[:3])}."
        else:
            text += "tuvimos una conversación al respecto."
        
        return text
