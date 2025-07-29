"""Tests for the cache manager."""

import pytest
import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from archguide_mcp_python.utils.cache import CacheManager


class TestCacheManager:
    """Test cases for CacheManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cache = CacheManager(default_ttl=0.1)  # 100ms for testing
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        self.cache.set("key1", "value1")
        
        result = self.cache.get("key1")
        assert result == "value1"
    
    def test_cache_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        result = self.cache.get("nonexistent")
        assert result is None
    
    def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        self.cache.set("key1", "value1", ttl=0.05)  # 50ms
        
        # Should be available immediately
        result = self.cache.get("key1")
        assert result == "value1"
        
        # Wait for expiration
        time.sleep(0.1)
        
        # Should be expired now
        result = self.cache.get("key1")
        assert result is None
    
    def test_cache_custom_ttl(self):
        """Test setting cache with custom TTL."""
        self.cache.set("key1", "value1", ttl=0.2)  # 200ms
        
        # Wait less than TTL
        time.sleep(0.1)
        result = self.cache.get("key1")
        assert result == "value1"
        
        # Wait for expiration
        time.sleep(0.15)
        result = self.cache.get("key1")
        assert result is None
    
    def test_cache_delete(self):
        """Test deleting cache entries."""
        self.cache.set("key1", "value1")
        
        # Verify it exists
        assert self.cache.get("key1") == "value1"
        
        # Delete it
        self.cache.delete("key1")
        
        # Verify it's gone
        assert self.cache.get("key1") is None
    
    def test_cache_clear(self):
        """Test clearing all cache entries."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # Verify entries exist
        assert self.cache.get("key1") == "value1"
        assert self.cache.get("key2") == "value2"
        
        # Clear cache
        self.cache.clear()
        
        # Verify all entries are gone
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
    
    def test_cache_size(self):
        """Test cache size tracking."""
        assert self.cache.size() == 0
        
        self.cache.set("key1", "value1")
        assert self.cache.size() == 1
        
        self.cache.set("key2", "value2")
        assert self.cache.size() == 2
        
        self.cache.delete("key1")
        assert self.cache.size() == 1
        
        self.cache.clear()
        assert self.cache.size() == 0
    
    def test_cleanup_expired(self):
        """Test manual cleanup of expired entries."""
        # Set entries with short TTL
        self.cache.set("key1", "value1", ttl=0.05)
        self.cache.set("key2", "value2", ttl=0.05)
        self.cache.set("key3", "value3", ttl=1.0)  # Longer TTL
        
        assert self.cache.size() == 3
        
        # Wait for some to expire
        time.sleep(0.1)
        
        # Cleanup expired entries
        removed_count = self.cache.cleanup_expired()
        
        assert removed_count == 2
        assert self.cache.size() == 1
        assert self.cache.get("key3") == "value3"
    
    def test_cache_different_data_types(self):
        """Test caching different data types."""
        # Test with different data types
        self.cache.set("string", "hello")
        self.cache.set("int", 42)
        self.cache.set("list", [1, 2, 3])
        self.cache.set("dict", {"key": "value"})
        
        assert self.cache.get("string") == "hello"
        assert self.cache.get("int") == 42
        assert self.cache.get("list") == [1, 2, 3]
        assert self.cache.get("dict") == {"key": "value"}