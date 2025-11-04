"""
TTS Service with thread-safe queue for GAIA v25.
Implements a single worker thread to prevent concurrent pyttsx3 issues.
"""
import queue
import threading
import logging

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logging.warning("pyttsx3 not available. TTS will be disabled.")

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service with thread-safe queue."""
    
    def __init__(self, voice_id=None, rate=160):
        """
        Initialize TTS service.
        
        Args:
            voice_id: Optional voice ID to use
            rate: Speech rate (words per minute)
        """
        self.enabled = PYTTSX3_AVAILABLE
        if not self.enabled:
            logger.warning("TTS service disabled - pyttsx3 not available")
            return
        
        self.q = queue.Queue()
        self.engine = None
        self.voice_id = voice_id
        self.rate = rate
        self._stop_event = threading.Event()
        
        # Initialize engine and start worker thread
        try:
            self._init_engine()
            self.worker = threading.Thread(target=self._loop, daemon=True)
            self.worker.start()
            logger.info("TTS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.enabled = False
    
    def _init_engine(self):
        """Initialize pyttsx3 engine with settings."""
        self.engine = pyttsx3.init()
        
        # Set voice if specified
        if self.voice_id:
            try:
                self.engine.setProperty('voice', self.voice_id)
            except Exception as e:
                logger.warning(f"Could not set voice {self.voice_id}: {e}")
        else:
            # Try to find a Spanish voice
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    try:
                        self.engine.setProperty('voice', voice.id)
                        logger.info(f"Selected Spanish voice: {voice.name}")
                        break
                    except Exception:
                        pass
        
        # Set speech rate
        self.engine.setProperty('rate', self.rate)
    
    def _loop(self):
        """Worker thread loop that processes TTS queue."""
        while not self._stop_event.is_set():
            try:
                text = self.q.get(timeout=1.0)
                if text is None:  # Shutdown signal
                    break
                
                # Speak the text
                self.engine.say(text)
                self.engine.runAndWait()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TTS error: {e}")
    
    def speak(self, text: str):
        """
        Queue text for speech (non-blocking).
        
        Args:
            text: Text to speak
        """
        if not self.enabled:
            return
        
        if not text or not isinstance(text, str):
            return
        
        try:
            self.q.put(text)
        except Exception as e:
            logger.error(f"Failed to queue TTS: {e}")
    
    def shutdown(self):
        """Shutdown TTS service gracefully."""
        if not self.enabled:
            return
        
        self._stop_event.set()
        self.q.put(None)  # Signal worker to stop
        
        if hasattr(self, 'worker'):
            self.worker.join(timeout=2.0)
    
    def clear_queue(self):
        """Clear pending TTS messages."""
        if not self.enabled:
            return
        
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except queue.Empty:
                break
