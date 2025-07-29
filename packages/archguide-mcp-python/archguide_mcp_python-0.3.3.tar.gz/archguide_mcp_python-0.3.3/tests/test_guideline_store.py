"""Tests for the guideline store."""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from archguide_mcp_python.storage.store import GuidelineStore
from archguide_mcp_python.models.types import ArchitectureGuideline, GuidelineMetadata, ContextFilters


class TestGuidelineStore:
    """Test cases for GuidelineStore."""
    
    @pytest.fixture
    def temp_guidelines_dir(self):
        """Create temporary directory with sample guidelines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            guidelines_dir = Path(temp_dir) / "guidelines"
            guidelines_dir.mkdir()
            
            # Create microservices category
            microservices_dir = guidelines_dir / "microservices"
            microservices_dir.mkdir()
            
            # Create sample guideline file
            sample_guideline = """---
id: test-guideline
title: Test Microservices Guideline
category: microservices
tags: [microservices, testing]
author: Test Author
created: 2024-01-01
lastUpdated: 2024-01-02
applicability: [enterprise]
techStack: [python, fastapi]
---

# Test Microservices Guideline

This is a test guideline for microservices.

## Pattern: Test Pattern

### Description
This is a test pattern.

### When to use
When testing.

### Implementation
Do testing things.

### Consequences
- Better testing
- More confidence

## Anti-pattern: Bad Testing

### Description
Don't do bad testing.

### Why it's bad
It's bad for quality.

### Instead
Do good testing.
"""
            
            (microservices_dir / "test-guideline.md").write_text(sample_guideline)
            
            yield str(guidelines_dir)
    
    @pytest.fixture
    def store(self, temp_guidelines_dir):
        """Create GuidelineStore with temporary directory."""
        return GuidelineStore(temp_guidelines_dir)
    
    @pytest.mark.asyncio
    async def test_initialize_store(self, store):
        """Test store initialization."""
        count = await store.initialize()
        
        assert count == 1
        assert len(store.guidelines) == 1
        assert "test-guideline" in store.guidelines
    
    @pytest.mark.asyncio
    async def test_get_guideline_by_id(self, store):
        """Test getting guideline by ID."""
        await store.initialize()
        
        guideline = store.get_guideline_by_id("test-guideline")
        
        assert guideline is not None
        assert guideline.title == "Test Microservices Guideline"
        assert guideline.category == "microservices"
        assert "microservices" in guideline.tags
        assert "testing" in guideline.tags
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_guideline(self, store):
        """Test getting non-existent guideline."""
        await store.initialize()
        
        guideline = store.get_guideline_by_id("nonexistent")
        
        assert guideline is None
    
    @pytest.mark.asyncio
    async def test_get_guidelines_by_topic(self, store):
        """Test getting guidelines by topic."""
        await store.initialize()
        
        # Test by tag
        guidelines = store.get_guidelines_by_topic("microservices")
        assert len(guidelines) == 1
        assert guidelines[0].id == "test-guideline"
        
        # Test by category
        guidelines = store.get_guidelines_by_topic("microservices")
        assert len(guidelines) == 1
        
        # Test non-matching topic
        guidelines = store.get_guidelines_by_topic("nonexistent")
        assert len(guidelines) == 0
    
    @pytest.mark.asyncio
    async def test_get_guidelines_with_context_filters(self, store):
        """Test getting guidelines with context filtering."""
        await store.initialize()
        
        # Test with matching tech stack
        context = ContextFilters(tech_stack=["python"])
        guidelines = store.get_guidelines_by_topic("microservices", context)
        assert len(guidelines) == 1
        
        # Test with non-matching tech stack
        context = ContextFilters(tech_stack=["java"])
        guidelines = store.get_guidelines_by_topic("microservices", context)
        assert len(guidelines) == 0
        
        # Test with matching scale
        context = ContextFilters(scale="enterprise")
        guidelines = store.get_guidelines_by_topic("microservices", context)
        assert len(guidelines) == 1
        
        # Test with non-matching scale
        context = ContextFilters(scale="startup")
        guidelines = store.get_guidelines_by_topic("microservices", context)
        assert len(guidelines) == 0
    
    @pytest.mark.asyncio
    async def test_search_guidelines(self, store):
        """Test searching guidelines."""
        await store.initialize()
        
        # Search for content that should match
        results = store.search_guidelines("microservices")
        assert len(results) >= 1
        
        # Search for content that shouldn't match
        results = store.search_guidelines("nonexistent-term")
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_get_categories(self, store):
        """Test getting available categories."""
        await store.initialize()
        
        categories = store.get_categories()
        
        assert "microservices" in categories
        assert len(categories) >= 1
    
    @pytest.mark.asyncio
    async def test_get_stats(self, store):
        """Test getting store statistics."""
        await store.initialize()
        
        stats = store.get_stats()
        
        assert stats["total_guidelines"] == 1
        assert stats["categories"] == 1
        assert "microservices" in stats["category_list"]
        assert stats["guidelines_per_category"]["microservices"] == 1
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, store):
        """Test that caching works properly."""
        await store.initialize()
        
        # First call should populate cache
        guidelines1 = store.get_guidelines_by_topic("microservices")
        
        # Second call should use cache (verify by checking cache size)
        guidelines2 = store.get_guidelines_by_topic("microservices")
        
        assert guidelines1 == guidelines2
        assert store.cache.size() > 0