"""Tests for dynamic category management functionality."""

import os
import tempfile
import shutil
from pathlib import Path

import pytest

from archguide_mcp_python.storage.store import GuidelineStore
from archguide_mcp_python.models.types import ArchitectureGuideline, GuidelineMetadata
from datetime import datetime


class TestCategoryManagement:
    """Test suite for dynamic category management operations."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.guidelines_path = Path(self.temp_dir) / "guidelines"
        self.guidelines_path.mkdir(parents=True, exist_ok=True)
        
        # Create initial test categories
        (self.guidelines_path / "microservices").mkdir()
        (self.guidelines_path / "security").mkdir()
        
        self.store = GuidelineStore(str(self.guidelines_path))
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_category(self):
        """Test creating a new category."""
        # Create a new category
        success = self.store.create_category("api-design", "Guidelines for API design")
        assert success is True
        
        # Verify category directory was created
        category_path = self.guidelines_path / "api-design"
        assert category_path.exists()
        assert category_path.is_dir()
        
        # Verify metadata file was created
        metadata_file = category_path / ".category.json"
        assert metadata_file.exists()
        
        import json
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        assert metadata["name"] == "api-design"
        assert metadata["description"] == "Guidelines for API design"
        assert "created" in metadata
    
    def test_create_category_without_description(self):
        """Test creating a category without description."""
        success = self.store.create_category("testing")
        assert success is True
        
        category_path = self.guidelines_path / "testing"
        assert category_path.exists()
        
        # No metadata file should be created without description
        metadata_file = category_path / ".category.json"
        assert not metadata_file.exists()
    
    def test_create_duplicate_category(self):
        """Test creating a category that already exists."""
        # First creation should succeed
        success1 = self.store.create_category("duplicate")
        assert success1 is True
        
        # Second creation should fail
        success2 = self.store.create_category("duplicate")
        assert success2 is False
    
    def test_rename_category(self):
        """Test renaming an existing category."""
        # Create some guidelines in the category
        guideline = ArchitectureGuideline(
            id="test-guideline",
            title="Test Guideline",
            category="microservices",
            content="Test content",
            tags=["test"],
            examples=[],
            patterns=[],
            anti_patterns=[],
            metadata=GuidelineMetadata(
                author="Test Author",
                created=datetime.now(),
                last_updated=datetime.now(),
                applicability=["test"]
            )
        )
        self.store.add_guideline(guideline)
        
        # Rename the category
        updated_count = self.store.rename_category("microservices", "distributed-systems")
        assert updated_count == 1
        
        # Verify old directory doesn't exist
        old_path = self.guidelines_path / "microservices"
        assert not old_path.exists()
        
        # Verify new directory exists
        new_path = self.guidelines_path / "distributed-systems"
        assert new_path.exists()
        
        # Verify guideline was updated
        updated_guideline = self.store.get_guideline_by_id("test-guideline")
        assert updated_guideline is not None
        assert updated_guideline.category == "distributed-systems"
    
    def test_rename_nonexistent_category(self):
        """Test renaming a category that doesn't exist."""
        updated_count = self.store.rename_category("nonexistent", "new-name")
        assert updated_count == 0
    
    def test_rename_to_existing_category(self):
        """Test renaming to a category that already exists."""
        updated_count = self.store.rename_category("microservices", "security")
        assert updated_count == 0
    
    def test_delete_empty_category(self):
        """Test deleting an empty category."""
        deleted_count = self.store.delete_category("microservices", force=False)
        assert deleted_count == 0
        
        # Verify directory was deleted
        category_path = self.guidelines_path / "microservices"
        assert not category_path.exists()
    
    def test_delete_non_empty_category_without_force(self):
        """Test deleting a non-empty category without force flag."""
        # Add a guideline to the category
        guideline = ArchitectureGuideline(
            id="test-guideline",
            title="Test Guideline",
            category="microservices",
            content="Test content",
            tags=["test"],
            examples=[],
            patterns=[],
            anti_patterns=[],
            metadata=GuidelineMetadata(
                author="Test Author",
                created=datetime.now(),
                last_updated=datetime.now(),
                applicability=["test"]
            )
        )
        self.store.add_guideline(guideline)
        
        # Try to delete without force
        deleted_count = self.store.delete_category("microservices", force=False)
        assert deleted_count == -1
        
        # Verify category still exists
        category_path = self.guidelines_path / "microservices"
        assert category_path.exists()
    
    def test_delete_non_empty_category_with_force(self):
        """Test deleting a non-empty category with force flag."""
        # Add a guideline to the category
        guideline = ArchitectureGuideline(
            id="test-guideline",
            title="Test Guideline",
            category="microservices",
            content="Test content",
            tags=["test"],
            examples=[],
            patterns=[],
            anti_patterns=[],
            metadata=GuidelineMetadata(
                author="Test Author",
                created=datetime.now(),
                last_updated=datetime.now(),
                applicability=["test"]
            )
        )
        self.store.add_guideline(guideline)
        
        # Delete with force
        deleted_count = self.store.delete_category("microservices", force=True)
        assert deleted_count == 1
        
        # Verify category was deleted
        category_path = self.guidelines_path / "microservices"
        assert not category_path.exists()
        
        # Verify guideline was removed from store
        guideline_after = self.store.get_guideline_by_id("test-guideline")
        assert guideline_after is None
    
    def test_delete_nonexistent_category(self):
        """Test deleting a category that doesn't exist."""
        deleted_count = self.store.delete_category("nonexistent", force=False)
        assert deleted_count == 0
    
    def test_get_category_details_empty(self):
        """Test getting category details when no guidelines exist."""
        details = self.store.get_category_details()
        
        # Should show empty categories
        assert len(details) == 0
    
    def test_get_category_details_with_guidelines(self):
        """Test getting category details with guidelines."""
        # Add guidelines to different categories
        guideline1 = ArchitectureGuideline(
            id="micro-guideline",
            title="Microservices Guideline",
            category="microservices",
            subcategory="patterns",
            content="Microservices content",
            tags=["microservices"],
            examples=[],
            patterns=[],
            anti_patterns=[],
            metadata=GuidelineMetadata(
                author="Test Author",
                created=datetime.now(),
                last_updated=datetime.now(),
                applicability=["enterprise"]
            )
        )
        
        guideline2 = ArchitectureGuideline(
            id="security-guideline",
            title="Security Guideline",
            category="security",
            content="Security content",
            tags=["security"],
            examples=[],
            patterns=[],
            anti_patterns=[],
            metadata=GuidelineMetadata(
                author="Test Author",
                created=datetime.now(),
                last_updated=datetime.now(),
                applicability=["all"]
            )
        )
        
        self.store.add_guideline(guideline1)
        self.store.add_guideline(guideline2)
        
        # Add category description
        (self.guidelines_path / "microservices" / ".category.json").write_text(
            '{"name": "microservices", "description": "Microservices patterns"}'
        )
        
        details = self.store.get_category_details()
        
        assert len(details) == 2
        assert "microservices" in details
        assert "security" in details
        
        micro_details = details["microservices"]
        assert micro_details["count"] == 1
        assert micro_details["description"] == "Microservices patterns"
        assert "patterns" in micro_details["subcategories"]
        
        security_details = details["security"]
        assert security_details["count"] == 1
        assert security_details["description"] is None
        assert len(security_details["subcategories"]) == 0
    
    def test_category_operations_cache_invalidation(self):
        """Test that category operations properly invalidate cache."""
        # Add a guideline
        guideline = ArchitectureGuideline(
            id="test-guideline",
            title="Test Guideline",
            category="microservices",
            content="Test content",
            tags=["test"],
            examples=[],
            patterns=[],
            anti_patterns=[],
            metadata=GuidelineMetadata(
                author="Test Author",
                created=datetime.now(),
                last_updated=datetime.now(),
                applicability=["test"]
            )
        )
        self.store.add_guideline(guideline)
        
        # Get initial categories (should cache)
        initial_categories = self.store.get_categories()
        assert "microservices" in initial_categories
        
        # Create new category
        self.store.create_category("new-category")
        
        # Categories should be updated (cache should be invalidated)
        updated_categories = self.store.get_categories()
        assert "new-category" in updated_categories
        
        # Rename category
        self.store.rename_category("microservices", "distributed-systems")
        
        # Check categories again
        final_categories = self.store.get_categories()
        assert "microservices" not in final_categories
        assert "distributed-systems" in final_categories