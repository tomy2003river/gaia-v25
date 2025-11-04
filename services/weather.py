"""
Weather service for GAIA v25 (Cronos handler).
Uses OpenWeatherMap API with proper error handling and timeouts.
"""
import os
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

API_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
TIMEOUT = 10  # seconds


class WeatherService:
    """OpenWeather API service with error handling."""
    
    def __init__(self, api_key: Optional[str] = None, lang: str = "es"):
        """
        Initialize weather service.
        
        Args:
            api_key: OpenWeather API key
            lang: Language for weather descriptions
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.lang = lang
        
        if not self.api_key:
            raise RuntimeError("OPENWEATHER_API_KEY no está configurada")
    
    def get_current_weather(self, city: str) -> Dict:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Dict with weather data
            
        Raises:
            requests.RequestException: On API errors
        """
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": self.lang
            }
            
            response = requests.get(
                API_ENDPOINT,
                params=params,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            result = {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "city": data.get("name", city),
                "country": data.get("sys", {}).get("country", ""),
                "wind_speed": data.get("wind", {}).get("speed", 0),
            }
            
            logger.info(f"Weather retrieved for {city}: {result['temp']}°C")
            return result
            
        except requests.Timeout:
            logger.error(f"Timeout getting weather for {city}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error getting weather for {city}: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing weather data for {city}: {e}")
            raise RuntimeError(f"Error procesando datos del clima: {e}")
    
    def get_forecast(self, city: str, days: int = 3) -> Dict:
        """
        Get weather forecast (placeholder for future implementation).
        
        Args:
            city: City name
            days: Number of days
            
        Returns:
            Forecast data
        """
        # TODO: Implement with forecast API endpoint
        logger.warning("Forecast not implemented yet")
        return {"error": "Pronóstico no disponible aún"}
