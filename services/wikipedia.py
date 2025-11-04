"""
Wikipedia service with caching for GAIA v25 (Apolo handler).
"""
import time
import logging
import requests
from typing import Dict, Optional, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)

WIKIPEDIA_API = "https://es.wikipedia.org/w/api.php"
TIMEOUT = 10


class WikipediaCache:
    """Simple file-based cache for Wikipedia queries."""
    
    def __init__(self, cache_dir: Path, ttl: int = 1800):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache files
            ttl: Time-to-live in seconds (default 30 minutes)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        # Simple hash to avoid filesystem issues
        safe_key = "".join(c if c.isalnum() else "_" for c in key.lower())
        return self.cache_dir / f"wiki_{safe_key[:50]}.json"
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached value if not expired."""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if expired
            if time.time() - data.get("timestamp", 0) > self.ttl:
                logger.debug(f"Cache expired for {key}")
                return None
            
            logger.debug(f"Cache hit for {key}")
            return data.get("value")
            
        except Exception as e:
            logger.warning(f"Error reading cache for {key}: {e}")
            return None
    
    def set(self, key: str, value: Dict):
        """Cache a value."""
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                "timestamp": time.time(),
                "value": value
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached {key}")
        except Exception as e:
            logger.warning(f"Error writing cache for {key}: {e}")


class WikipediaService:
    """Wikipedia API service with caching."""
    
    def __init__(self, cache_dir: Path, lang: str = "es", cache_ttl: int = 1800):
        """
        Initialize Wikipedia service.
        
        Args:
            cache_dir: Directory for caching
            lang: Language code (es, en, etc.)
            cache_ttl: Cache time-to-live in seconds
        """
        self.lang = lang
        self.api_url = f"https://{lang}.wikipedia.org/w/api.php"
        self.cache = WikipediaCache(cache_dir, ttl=cache_ttl)
    
    def search(self, query: str, limit: int = 5) -> List[str]:
        """
        Search Wikipedia for matching articles.
        
        Args:
            query: Search query
            limit: Max number of results
            
        Returns:
            List of article titles
        """
        try:
            params = {
                "action": "opensearch",
                "search": query,
                "limit": limit,
                "format": "json"
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            # OpenSearch returns [query, [titles], [descriptions], [urls]]
            titles = data[1] if len(data) > 1 else []
            
            logger.info(f"Search for '{query}' returned {len(titles)} results")
            return titles
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia for '{query}': {e}")
            return []
    
    def get_summary(self, title: str) -> Optional[Dict]:
        """
        Get article summary.
        
        Args:
            title: Article title
            
        Returns:
            Dict with title, summary, and url
        """
        # Check cache first
        cached = self.cache.get(title)
        if cached:
            return cached
        
        try:
            params = {
                "action": "query",
                "prop": "extracts|info",
                "exintro": True,
                "explaintext": True,
                "titles": title,
                "format": "json",
                "inprop": "url"
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            # Get first (and usually only) page
            page = next(iter(pages.values()), None)
            
            if not page or "missing" in page:
                logger.warning(f"Article not found: {title}")
                return None
            
            result = {
                "title": page.get("title", title),
                "summary": page.get("extract", ""),
                "url": page.get("fullurl", ""),
                "pageid": page.get("pageid", 0)
            }
            
            # Cache the result
            self.cache.set(title, result)
            
            logger.info(f"Retrieved summary for '{title}'")
            return result
            
        except Exception as e:
            logger.error(f"Error getting summary for '{title}': {e}")
            return None
    
    def get_snippet(self, query: str) -> Optional[str]:
        """
        Get a snippet for a query (search + first result summary).
        
        Args:
            query: Search query
            
        Returns:
            Text snippet or None
        """
        # Search for articles
        titles = self.search(query, limit=1)
        
        if not titles:
            return None
        
        # Get summary of first result
        summary_data = self.get_summary(titles[0])
        
        if not summary_data:
            return None
        
        # Return first paragraph (up to 500 chars)
        summary = summary_data.get("summary", "")
        if len(summary) > 500:
            summary = summary[:497] + "..."
        
        return summary
