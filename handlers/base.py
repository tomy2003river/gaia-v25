"""
Base handler interface for GAIA v25.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.errors import Response


class BaseHandler(ABC):
    """Abstract base class for all handlers."""
    
    def __init__(self, name: str, priority: int):
        """
        Initialize handler.
        
        Args:
            name: Handler name
            priority: Handler priority (higher = checked first)
        """
        self.name = name
        self.priority = priority
    
    @abstractmethod
    def can_handle(self, message: str, context: Optional[Dict] = None) -> bool:
        """
        Check if this handler can handle the message.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            True if handler can process this message
        """
        pass
    
    @abstractmethod
    def handle(self, message: str, context: Optional[Dict] = None) -> Response:
        """
        Handle the message and generate a response.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            Response object
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, priority={self.priority})"
