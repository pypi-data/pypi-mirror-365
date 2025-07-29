"""Tests for dynamic guideline management functionality."""

import pytest
import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from archguide_mcp_python.storage.store import GuidelineStore
from archguide_mcp_python.models.types import (
    ArchitectureGuideline, GuidelineMetadata, Pattern, AntiPattern, CodeExample
)


class TestDynamicGuidelineManagement:
    """Test cases for dynamic guideline management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for guidelines
        self.temp_dir = tempfile.mkdtemp()
        self.guidelines_dir = os.path.join(self.temp_dir, 'guidelines')
        os.makedirs(self.guidelines_dir)
        
        # Create store
        self.store = GuidelineStore(guidelines_path=self.guidelines_dir)
        # Use sync version of initialize for testing
        self.store.reload_guidelines()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_add_guideline(self):
        """Test adding a new guideline dynamically."""
        # Create a test guideline
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now(),
            tech_stack=["python", "fastapi"],
            applicability=["startup", "enterprise"]
        )
        
        patterns = [
            Pattern(
                name="Test Pattern",
                description="A test pattern for testing",
                when="When you need to test",
                implementation="Implement testing logic",
                consequences=["Good testing", "Better code"]
            )
        ]
        
        guideline = ArchitectureGuideline(
            id="test-dynamic-guideline",
            title="Dynamic Test Guideline",
            category="testing",
            tags=["test", "dynamic"],
            content="This is a dynamically created guideline for testing purposes.",
            patterns=patterns,
            metadata=metadata
        )
        
        # Add guideline
        initial_count = len(self.store.guidelines)
        self.store.add_guideline(guideline)
        
        # Verify it was added
        assert len(self.store.guidelines) == initial_count + 1
        assert "test-dynamic-guideline" in self.store.guidelines
        
        # Verify it can be retrieved
        retrieved = self.store.get_guideline_by_id("test-dynamic-guideline")
        assert retrieved is not None
        assert retrieved.title == "Dynamic Test Guideline"
        assert retrieved.category == "testing"
        assert len(retrieved.patterns) == 1
        assert retrieved.patterns[0].name == "Test Pattern"
    
    def test_update_guideline(self):
        """Test updating an existing guideline."""
        # First add a guideline
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now()
        )
        
        guideline = ArchitectureGuideline(
            id="test-update-guideline",
            title="Original Title",
            category="testing",
            content="Original content",
            metadata=metadata
        )
        
        self.store.add_guideline(guideline)
        
        # Update the guideline
        guideline.title = "Updated Title"
        guideline.content = "Updated content with new information"
        guideline.tags = ["updated", "test"]
        guideline.metadata.last_updated = datetime.now()
        
        self.store.update_guideline(guideline)
        
        # Verify the update
        retrieved = self.store.get_guideline_by_id("test-update-guideline")
        assert retrieved is not None
        assert retrieved.title == "Updated Title"
        assert retrieved.content == "Updated content with new information"
        assert "updated" in retrieved.tags
    
    def test_delete_guideline(self):
        """Test deleting a guideline."""
        # First add a guideline
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now()
        )
        
        guideline = ArchitectureGuideline(
            id="test-delete-guideline",
            title="To Be Deleted",
            category="testing",
            content="This will be deleted",
            metadata=metadata
        )
        
        self.store.add_guideline(guideline)
        initial_count = len(self.store.guidelines)
        
        # Verify it exists
        assert "test-delete-guideline" in self.store.guidelines
        
        # Delete it
        success = self.store.delete_guideline("test-delete-guideline")
        assert success is True
        
        # Verify it's gone
        assert len(self.store.guidelines) == initial_count - 1
        assert "test-delete-guideline" not in self.store.guidelines
        assert self.store.get_guideline_by_id("test-delete-guideline") is None
    
    def test_delete_nonexistent_guideline(self):
        """Test deleting a guideline that doesn't exist."""
        success = self.store.delete_guideline("nonexistent-guideline")
        assert success is False
    
    def test_reload_guidelines(self):
        """Test reloading guidelines from filesystem."""
        # Add a guideline
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now()
        )
        
        guideline = ArchitectureGuideline(
            id="test-reload-guideline",
            title="Reload Test",
            category="testing",
            content="Test reload functionality",
            metadata=metadata
        )
        
        self.store.add_guideline(guideline)
        initial_count = len(self.store.guidelines)
        
        # Manually clear the in-memory store to simulate need for reload
        self.store.guidelines.clear()
        assert len(self.store.guidelines) == 0
        
        # Reload from filesystem
        count = self.store.reload_guidelines()
        
        # Verify guidelines are loaded back
        assert count == initial_count
        assert len(self.store.guidelines) == initial_count
        assert "test-reload-guideline" in self.store.guidelines
    
    def test_guideline_with_examples(self):
        """Test adding guideline with code examples."""
        examples = [
            CodeExample(
                title="Python Example",
                description="A simple Python function",
                language="python",
                code="def hello():\n    return 'Hello, World!'"
            ),
            CodeExample(
                title="JavaScript Example",
                description="A simple JavaScript function",
                language="javascript",
                code="function hello() {\n    return 'Hello, World!';\n}"
            )
        ]
        
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now()
        )
        
        guideline = ArchitectureGuideline(
            id="test-examples-guideline",
            title="Guideline with Examples",
            category="examples",
            content="This guideline demonstrates code examples",
            examples=examples,
            metadata=metadata
        )
        
        self.store.add_guideline(guideline)
        
        # Verify examples are preserved
        retrieved = self.store.get_guideline_by_id("test-examples-guideline")
        assert retrieved is not None
        assert len(retrieved.examples) == 2
        assert retrieved.examples[0].language == "python"
        assert retrieved.examples[1].language == "javascript"
        assert "def hello():" in retrieved.examples[0].code
    
    def test_guideline_with_anti_patterns(self):
        """Test adding guideline with anti-patterns."""
        anti_patterns = [
            AntiPattern(
                name="Bad Practice",
                description="This is a bad way to do things",
                why="It causes problems",
                instead="Do it this way instead"
            )
        ]
        
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now()
        )
        
        guideline = ArchitectureGuideline(
            id="test-antipatterns-guideline",
            title="Guideline with Anti-patterns",
            category="patterns",
            content="This guideline demonstrates anti-patterns",
            anti_patterns=anti_patterns,
            metadata=metadata
        )
        
        self.store.add_guideline(guideline)
        
        # Verify anti-patterns are preserved
        retrieved = self.store.get_guideline_by_id("test-antipatterns-guideline")
        assert retrieved is not None
        assert len(retrieved.anti_patterns) == 1
        assert retrieved.anti_patterns[0].name == "Bad Practice"
        assert retrieved.anti_patterns[0].why == "It causes problems"
    
    def test_cache_invalidation_on_add(self):
        """Test that cache is invalidated when adding guidelines."""
        # Get initial cache size
        initial_cache_size = self.store.cache.size()
        
        # Add some cached data by getting guidelines
        self.store.get_guidelines_by_topic("testing")
        cache_size_after_query = self.store.cache.size()
        
        # Cache should have grown
        assert cache_size_after_query >= initial_cache_size
        
        # Add a new guideline
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now()
        )
        
        guideline = ArchitectureGuideline(
            id="test-cache-invalidation",
            title="Cache Test",
            category="testing",
            content="Test cache invalidation",
            metadata=metadata
        )
        
        self.store.add_guideline(guideline)
        
        # Cache should be cleared
        assert self.store.cache.size() == 0
    
    def test_search_index_updated_on_add(self):
        """Test that search index is updated when adding guidelines."""
        # Add a guideline with searchable content
        metadata = GuidelineMetadata(
            author="Test Author",
            created=datetime.now(),
            last_updated=datetime.now()
        )
        
        guideline = ArchitectureGuideline(
            id="test-search-index",
            title="Searchable Guideline",
            category="search",
            content="This guideline contains unique searchable content about microservices",
            tags=["searchable", "unique"],
            metadata=metadata
        )
        
        self.store.add_guideline(guideline)
        
        # Search for the content
        results = self.store.search_guidelines("unique searchable content")
        
        # Should find the guideline
        assert len(results) > 0
        found_guideline = next((g for g in results if g.id == "test-search-index"), None)
        assert found_guideline is not None
        assert found_guideline.title == "Searchable Guideline"