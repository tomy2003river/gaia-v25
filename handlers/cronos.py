"""
Cronos handler - Weather queries for GAIA v25.
"""
import logging
from typing import Dict, Optional
from handlers.base import BaseHandler
from core.errors import Response, ServiceError
from services.weather import WeatherService

logger = logging.getLogger(__name__)


class CronosHandler(BaseHandler):
    """Handler for weather-related queries."""
    
    def __init__(self, weather_service: WeatherService, default_city: str = "Buenos Aires"):
        """
        Initialize Cronos handler.
        
        Args:
            weather_service: Weather service instance
            default_city: Default city for queries
        """
        super().__init__(name="CRONOS", priority=80)
        self.weather_service = weather_service
        self.default_city = default_city
    
    def can_handle(self, message: str, context: Optional[Dict] = None) -> bool:
        """Check if message is weather-related."""
        # This is called after router classification, so we trust the intent
        return True
    
    def handle(self, message: str, context: Optional[Dict] = None) -> Response:
        """
        Handle weather query.
        
        Args:
            message: User message
            context: Optional context with city info
            
        Returns:
            Response with weather information
        """
        # Extract city from context or use default
        city = self.default_city
        if context and "city" in context:
            city = context["city"]
        else:
            # Simple city extraction from message
            city = self._extract_city(message) or self.default_city
        
        try:
            # Get weather data
            weather = self.weather_service.get_current_weather(city)
            
            # Format response in Cronos' style
            text = self._format_response(weather)
            
            return Response(
                text=text,
                intent="CRONOS",
                success=True,
                metadata={
                    "city": weather["city"],
                    "temp": weather["temp"],
                    "description": weather["description"]
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return Response(
                text=f"Lo siento, no pude obtener el clima para {city}. Intenta de nuevo más tarde.",
                intent="CRONOS",
                success=False,
                error=str(e)
            )
    
    def _extract_city(self, message: str) -> Optional[str]:
        """
        Extract city name from message (simple heuristic).
        
        Args:
            message: User message
            
        Returns:
            City name or None
        """
        # Look for "en <city>" or "de <city>"
        import re
        
        patterns = [
            r'\ben\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
            r'\bde\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                # Remove common trailing words
                city = re.sub(r'\s+(hoy|ahora|mañana)$', '', city, flags=re.IGNORECASE)
                return city
        
        return None
    
    def _format_response(self, weather: Dict) -> str:
        """
        Format weather response in Cronos' personality.
        
        Args:
            weather: Weather data dict
            
        Returns:
            Formatted response text
        """
        city = weather["city"]
        temp = weather["temp"]
        desc = weather["description"]
        feels_like = weather.get("feels_like", temp)
        humidity = weather.get("humidity", 0)
        wind = weather.get("wind_speed", 0)
        
        # Cronos speaks with authority about time and weather
        response = f"En {city}, la temperatura actual es de {temp:.1f}°C, con {desc}. "
        
        if abs(feels_like - temp) > 2:
            response += f"Sensación térmica de {feels_like:.1f}°C. "
        
        if humidity > 70:
            response += f"Humedad elevada del {humidity}%. "
        elif humidity < 30:
            response += f"Ambiente seco con {humidity}% de humedad. "
        
        if wind > 5:
            response += f"Vientos de {wind:.1f} m/s."
        
        return response.strip()
