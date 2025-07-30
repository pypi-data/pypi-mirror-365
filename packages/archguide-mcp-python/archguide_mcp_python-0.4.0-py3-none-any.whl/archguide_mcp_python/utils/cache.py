"""Caching utilities for the ArchGuide MCP Server."""

import time
from typing import Any, Optional, Dict, TypeVar, Generic

T = TypeVar('T')


class CacheEntry(Generic[T]):
    """Represents a single cache entry with TTL."""
    
    def __init__(self, data: T, ttl: float):
        self.data = data
        self.expiry = time.time() + ttl


class CacheManager:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: float = 300.0):  # 5 minutes default
        self._cache: Dict[str, CacheEntry[Any]] = {}
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if time.time() > entry.expiry:
            del self._cache[key]
            return None
        
        return entry.data
    
    def set(self, key: str, data: Any, ttl: Optional[float] = None) -> None:
        """Set an item in the cache with optional TTL."""
        if ttl is None:
            ttl = self._default_ttl
        
        self._cache[key] = CacheEntry(data, ttl)
    
    def delete(self, key: str) -> None:
        """Delete an item from the cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry.expiry
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Return the number of items in the cache."""
        return len(self._cache)