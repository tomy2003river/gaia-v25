"""
Memory service for GAIA v25 with sliding window and decay.
"""
from collections import deque
from typing import Dict, List, Any, Optional
import time
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class Memory:
    """Memory service with decay and sliding window."""
    
    def __init__(self, maxlen: int = 200, decay: float = 0.95, persist: bool = False, storage_path: Optional[Path] = None):
        """
        Initialize memory.
        
        Args:
            maxlen: Maximum number of events to store
            decay: Decay factor for older events (0-1)
            persist: Whether to persist memory to disk
            storage_path: Path for persistent storage
        """
        self.events = deque(maxlen=maxlen)
        self.decay = decay
        self.persist = persist
        self.storage_path = storage_path
        self.maxlen = maxlen
        
        # Load from disk if persisting
        if self.persist and self.storage_path:
            self._load()
    
    def add(self, item: Dict[str, Any]):
        """
        Add an event to memory.
        
        Args:
            item: Event data (should include 'topic', 'timestamp', 'type')
        """
        event = {
            "item": item,
            "weight": 1.0,
            "timestamp": time.time()
        }
        self.events.append(event)
        
        logger.debug(f"Added to memory: {item.get('topic', 'unknown')}")
        
        if self.persist:
            self._save()
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        """
        Get n most recent events.
        
        Args:
            n: Number of events to retrieve
            
        Returns:
            List of recent events
        """
        recent = list(self.events)[-n:]
        return [e["item"] for e in recent]
    
    def get_topics(self) -> List[tuple]:
        """
        Get topics sorted by weighted importance (recent + frequent).
        
        Returns:
            List of (topic, score) tuples
        """
        scores = {}
        weight = 1.0
        
        # Iterate in reverse (most recent first)
        for event in reversed(self.events):
            weight *= self.decay
            topic = event["item"].get("topic", "misc")
            scores[topic] = scores.get(topic, 0) + weight
        
        # Sort by score descending
        sorted_topics = sorted(scores.items(), key=lambda x: -x[1])
        return sorted_topics
    
    def search(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        Search memory for events containing a keyword.
        
        Args:
            keyword: Keyword to search for
            limit: Maximum results
            
        Returns:
            List of matching events
        """
        keyword_lower = keyword.lower()
        results = []
        
        # Search in reverse (most recent first)
        for event in reversed(self.events):
            item = event["item"]
            
            # Check if keyword appears in any field
            if any(keyword_lower in str(v).lower() for v in item.values()):
                results.append(item)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_summary(self) -> Dict:
        """
        Get a summary of memory state.
        
        Returns:
            Dict with memory statistics
        """
        topics = self.get_topics()
        
        return {
            "total_events": len(self.events),
            "top_topics": topics[:5],
            "oldest_timestamp": self.events[0]["timestamp"] if self.events else None,
            "newest_timestamp": self.events[-1]["timestamp"] if self.events else None,
        }
    
    def clear(self):
        """Clear all memory."""
        self.events.clear()
        logger.info("Memory cleared")
        
        if self.persist:
            self._save()
    
    def _save(self):
        """Save memory to disk."""
        if not self.storage_path:
            return
        
        try:
            data = {
                "maxlen": self.maxlen,
                "decay": self.decay,
                "events": list(self.events)
            }
            
            self.storage_path.parent.mkdir(exist_ok=True)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug("Memory saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def _load(self):
        """Load memory from disk."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore events
            events = data.get("events", [])
            for event in events:
                self.events.append(event)
            
            logger.info(f"Loaded {len(self.events)} events from disk")
            
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
