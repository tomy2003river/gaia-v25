"""
Configuration module for GAIA v25.
Loads and validates environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """Central configuration for GAIA."""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / "cache"
    
    # API Keys
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Default settings
    GAIA_CITY = os.getenv("GAIA_CITY", "Buenos Aires")
    GAIA_LANG = os.getenv("GAIA_LANG", "es")
    
    # TTS Settings
    GAIA_TTS_RATE = int(os.getenv("GAIA_TTS_RATE", "160"))
    GAIA_TTS_VOICE_ID = os.getenv("GAIA_TTS_VOICE_ID", "")
    
    # Memory Settings
    GAIA_MEMORY_MAXLEN = int(os.getenv("GAIA_MEMORY_MAXLEN", "200"))
    GAIA_MEMORY_DECAY = float(os.getenv("GAIA_MEMORY_DECAY", "0.95"))
    
    # Cache Settings
    GAIA_CACHE_TTL = int(os.getenv("GAIA_CACHE_TTL", "1800"))  # 30 minutes
    
    # Logging
    GAIA_LOG_LEVEL = os.getenv("GAIA_LOG_LEVEL", "INFO")
    GAIA_LOG_FILE = os.getenv("GAIA_LOG_FILE", "logs/gaia.log")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        
        if not cls.OPENWEATHER_API_KEY:
            errors.append("OPENWEATHER_API_KEY no está configurada. Obtén una clave en https://openweathermap.org/api")
        
        # Create necessary directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.CACHE_DIR.mkdir(exist_ok=True)
        
        if errors:
            return False, errors
        return True, []
    
    @classmethod
    def get_summary(cls):
        """Get configuration summary (without secrets)."""
        return {
            "city": cls.GAIA_CITY,
            "lang": cls.GAIA_LANG,
            "tts_rate": cls.GAIA_TTS_RATE,
            "memory_maxlen": cls.GAIA_MEMORY_MAXLEN,
            "cache_ttl": cls.GAIA_CACHE_TTL,
            "api_key_set": bool(cls.OPENWEATHER_API_KEY),
        }
