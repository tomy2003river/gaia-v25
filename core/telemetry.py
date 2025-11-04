"""
Telemetry and logging system for GAIA v25.
"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "intent"):
            log_data["intent"] = record.intent
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
        
        return json.dumps(log_data, ensure_ascii=False)


class Telemetry:
    """Telemetry collection for GAIA."""
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize telemetry.
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "intents": {},
            "latencies": [],
        }
    
    def log_request(self, intent: str, latency_ms: float, success: bool, error: Optional[str] = None):
        """
        Log a request.
        
        Args:
            intent: Intent name
            latency_ms: Request latency in milliseconds
            success: Whether request was successful
            error: Error message if failed
        """
        self.metrics["requests"] += 1
        
        if not success:
            self.metrics["errors"] += 1
        
        # Track per-intent stats
        if intent not in self.metrics["intents"]:
            self.metrics["intents"][intent] = {
                "count": 0,
                "errors": 0,
                "latencies": []
            }
        
        self.metrics["intents"][intent]["count"] += 1
        if not success:
            self.metrics["intents"][intent]["errors"] += 1
        
        self.metrics["intents"][intent]["latencies"].append(latency_ms)
        self.metrics["latencies"].append(latency_ms)
        
        # Log to file if configured
        if self.log_file:
            self._write_log({
                "timestamp": datetime.utcnow().isoformat(),
                "intent": intent,
                "latency_ms": latency_ms,
                "success": success,
                "error": error
            })
    
    def _write_log(self, data: Dict[str, Any]):
        """Write log entry to file."""
        try:
            if self.log_file:
                self.log_file.parent.mkdir(exist_ok=True)
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.error(f"Failed to write telemetry log: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        metrics = {
            "total_requests": self.metrics["requests"],
            "total_errors": self.metrics["errors"],
            "error_rate": self.metrics["errors"] / max(self.metrics["requests"], 1),
        }
        
        # Calculate percentiles if we have data
        if self.metrics["latencies"]:
            sorted_latencies = sorted(self.metrics["latencies"])
            n = len(sorted_latencies)
            metrics["latency_p50"] = sorted_latencies[int(n * 0.5)]
            metrics["latency_p95"] = sorted_latencies[int(n * 0.95)]
            metrics["latency_avg"] = sum(sorted_latencies) / n
        
        # Per-intent metrics
        metrics["by_intent"] = {}
        for intent, data in self.metrics["intents"].items():
            intent_latencies = data["latencies"]
            if intent_latencies:
                metrics["by_intent"][intent] = {
                    "count": data["count"],
                    "errors": data["errors"],
                    "error_rate": data["errors"] / max(data["count"], 1),
                    "avg_latency": sum(intent_latencies) / len(intent_latencies)
                }
        
        return metrics
    
    def reset(self):
        """Reset metrics."""
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "intents": {},
            "latencies": [],
        }


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON format
    if log_file:
        log_file.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
