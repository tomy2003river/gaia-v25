"""
Main GAIA application coordinator.
Integrates router, handlers, services, and memory.
"""
import logging
import time
from typing import Dict, Optional
from pathlib import Path

from config import Config
from core import IntentRouter, Memory, Response, Telemetry
from services import TTSService, WeatherService, WikipediaService
from handlers import CronosHandler, ApoloHandler, HadesHandler, ReaHandler, GenericHandler

logger = logging.getLogger(__name__)


class GAIACore:
    """Core GAIA application logic."""
    
    def __init__(self, config: Config):
        """
        Initialize GAIA core.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize telemetry
        log_file = config.LOGS_DIR / "telemetry.jsonl"
        self.telemetry = Telemetry(log_file=log_file)
        
        # Initialize services
        logger.info("Initializing services...")
        self.tts = TTSService(
            voice_id=config.GAIA_TTS_VOICE_ID or None,
            rate=config.GAIA_TTS_RATE
        )
        
        try:
            self.weather = WeatherService(
                api_key=config.OPENWEATHER_API_KEY,
                lang=config.GAIA_LANG
            )
        except RuntimeError as e:
            logger.warning(f"Weather service disabled: {e}")
            self.weather = None
        
        self.wikipedia = WikipediaService(
            cache_dir=config.CACHE_DIR,
            lang=config.GAIA_LANG,
            cache_ttl=config.GAIA_CACHE_TTL
        )
        
        # Initialize memory
        memory_file = config.DATA_DIR / "memory.json"
        self.memory = Memory(
            maxlen=config.GAIA_MEMORY_MAXLEN,
            decay=config.GAIA_MEMORY_DECAY,
            persist=False,  # Can be enabled via config
            storage_path=memory_file
        )
        
        # Initialize router
        self.router = IntentRouter()
        
        # Initialize handlers
        self.handlers = {}
        
        if self.weather:
            self.handlers["CRONOS"] = CronosHandler(
                weather_service=self.weather,
                default_city=config.GAIA_CITY
            )
        
        self.handlers["APOLO"] = ApoloHandler(wikipedia_service=self.wikipedia)
        self.handlers["HADES"] = HadesHandler(memory=self.memory)
        self.handlers["REA"] = ReaHandler()
        self.handlers["GENERIC"] = GenericHandler()
        self.handlers["GREETING"] = self.handlers["GENERIC"]
        self.handlers["FAREWELL"] = self.handlers["GENERIC"]
        
        logger.info("GAIA Core initialized successfully")
    
    def process_message(self, message: str, speak: bool = True) -> Response:
        """
        Process a user message.
        
        Args:
            message: User message
            speak: Whether to speak the response
            
        Returns:
            Response object
        """
        start_time = time.time()
        
        try:
            # Classify intent
            intent = self.router.classify(message)
            logger.info(f"Intent: {intent}")
            
            # Get appropriate handler
            handler = self.handlers.get(intent, self.handlers["GENERIC"])
            
            # Handle message
            context = {"intent": intent}
            response = handler.handle(message, context)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Log to telemetry
            self.telemetry.log_request(
                intent=intent,
                latency_ms=latency_ms,
                success=response.success,
                error=response.error
            )
            
            # Add to memory
            self.memory.add({
                "type": "interaction",
                "user_message": message,
                "intent": intent,
                "topic": self._extract_topic(message, intent),
                "timestamp": time.time()
            })
            
            # Speak response if requested
            if speak and response.text:
                self.tts.speak(response.text)
            
            logger.info(f"Response generated in {latency_ms:.1f}ms")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            
            # Log error to telemetry
            latency_ms = (time.time() - start_time) * 1000
            self.telemetry.log_request(
                intent="ERROR",
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )
            
            return Response(
                text="Lo siento, ocurrió un error al procesar tu mensaje. Intenta de nuevo.",
                intent="ERROR",
                success=False,
                error=str(e)
            )
    
    def _extract_topic(self, message: str, intent: str) -> str:
        """
        Extract topic from message for memory.
        
        Args:
            message: User message
            intent: Classified intent
            
        Returns:
            Topic string
        """
        if intent == "CRONOS":
            return "clima"
        elif intent == "APOLO":
            return "conocimiento"
        elif intent == "HADES":
            return "memoria"
        elif intent == "REA":
            return "naturaleza"
        else:
            return "conversación"
    
    def get_metrics(self) -> Dict:
        """Get telemetry metrics."""
        return self.telemetry.get_metrics()
    
    def shutdown(self):
        """Shutdown GAIA gracefully."""
        logger.info("Shutting down GAIA...")
        self.tts.shutdown()
        logger.info("GAIA shutdown complete")
