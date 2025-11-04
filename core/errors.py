"""
Response models and error handling for GAIA v25.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import time


@dataclass
class Response:
    """Standard response format for handlers."""
    text: str
    intent: str
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary."""
        return {
            "text": self.text,
            "intent": self.intent,
            "success": self.success,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp
        }


class GAIAError(Exception):
    """Base exception for GAIA errors."""
    pass


class ConfigurationError(GAIAError):
    """Configuration-related errors."""
    pass


class ServiceError(GAIAError):
    """External service errors."""
    pass


class HandlerError(GAIAError):
    """Handler execution errors."""
    pass
