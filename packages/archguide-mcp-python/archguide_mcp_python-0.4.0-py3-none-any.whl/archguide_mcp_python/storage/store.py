"""Main guideline store that combines filesystem and search capabilities."""

import json
from typing import List, Optional, Dict, Any
from ..models.types import ArchitectureGuideline, SearchFilters, ContextFilters
from ..utils.cache import CacheManager
from .filesystem import FileSystemStorage
from .search import SearchIndex


class GuidelineStore:
    """Main store for architecture guidelines with caching and search."""
    
    def __init__(self, guidelines_path: str = "./guidelines", 
                 index_dir: Optional[str] = None):
        """Initialize the guideline store."""
        self.filesystem = FileSystemStorage(guidelines_path)
        self.search_index = SearchIndex(index_dir)
        self.cache = CacheManager()
        self.guidelines: Dict[str, ArchitectureGuideline] = {}
        self._initialized = False
    
    async def initialize(self) -> int:
        """Initialize the store by loading all guidelines."""
        if self._initialized:
            return len(self.guidelines)
        
        # Load all guidelines from filesystem
        guidelines = self.filesystem.load_all_guidelines()
        
        # Clear existing data
        self.guidelines.clear()
        self.search_index.clear()
        
        # Index and store guidelines
        for guideline in guidelines:
            self.guidelines[guideline.id] = guideline
            self.search_index.add_guideline(guideline)
        
        self._initialized = True
        print(f"Loaded {len(guidelines)} architecture guidelines")
        return len(guidelines)
    
    def get_guideline_by_id(self, guideline_id: str) -> Optional[ArchitectureGuideline]:
        """Get a guideline by its ID."""
        return self.guidelines.get(guideline_id)
    
    def get_guidelines_by_ids(self, guideline_ids: List[str]) -> List[ArchitectureGuideline]:
        """Get multiple guidelines by their IDs."""
        return [
            guideline for guideline_id in guideline_ids
            if (guideline := self.guidelines.get(guideline_id)) is not None
        ]
    
    def get_guidelines_by_topic(self, topic: str, 
                               context: Optional[ContextFilters] = None) -> List[ArchitectureGuideline]:
        """Get guidelines by topic with optional context filtering."""
        cache_key = f"topic:{topic}:{json.dumps(context.model_dump() if context else {})}"
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        # Find guidelines matching the topic
        results = []
        
        for guideline in self.guidelines.values():
            # Topic matching
            topic_match = (
                topic.lower() in [tag.lower() for tag in guideline.tags] or
                topic.lower() == guideline.category.lower() or
                topic.lower() in guideline.title.lower()
            )
            
            if not topic_match:
                continue
            
            # Apply context filtering if provided
            if context:
                context_match = True
                
                # Tech stack filtering
                if context.tech_stack:
                    if not guideline.metadata.tech_stack:
                        context_match = False
                    else:
                        tech_match = any(
                            tech.lower() in [t.lower() for t in guideline.metadata.tech_stack]
                            for tech in context.tech_stack
                        )
                        context_match = context_match and tech_match
                
                # Scale filtering
                if context.scale:
                    scale_match = context.scale.lower() in [
                        app.lower() for app in guideline.metadata.applicability
                    ]
                    context_match = context_match and scale_match
                
                # Domain filtering
                if context.domain:
                    domain_match = context.domain.lower() in [
                        app.lower() for app in guideline.metadata.applicability
                    ]
                    context_match = context_match and domain_match
                
                if not context_match:
                    continue
            
            results.append(guideline)
        
        # Cache the results
        self.cache.set(cache_key, results)
        return results
    
    def search_guidelines(self, query: str, filters: Optional[SearchFilters] = None,
                         limit: int = 10) -> List[ArchitectureGuideline]:
        """Search guidelines using full-text search."""
        # Get matching guideline IDs from search index
        guideline_ids = self.search_index.search(query, filters, limit)
        
        # Return corresponding guideline objects
        return self.get_guidelines_by_ids(guideline_ids)
    
    def get_categories(self) -> List[str]:
        """Get list of available categories."""
        categories = set()
        
        # Add categories from guidelines
        for guideline in self.guidelines.values():
            categories.add(guideline.category)
        
        # Add empty categories from filesystem
        filesystem_categories = self.filesystem.get_categories()
        categories.update(filesystem_categories)
        
        return sorted(list(categories))
    
    def add_guideline(self, guideline: ArchitectureGuideline) -> None:
        """Add a new guideline to the store."""
        # Save to filesystem
        self.filesystem.save_guideline(guideline)
        
        # Add to in-memory store
        self.guidelines[guideline.id] = guideline
        
        # Add to search index
        self.search_index.add_guideline(guideline)
        
        # Clear cache
        self.cache.clear()
    
    def update_guideline(self, guideline: ArchitectureGuideline) -> None:
        """Update an existing guideline."""
        # Save to filesystem
        self.filesystem.save_guideline(guideline)
        
        # Update in-memory store
        self.guidelines[guideline.id] = guideline
        
        # Update search index
        self.search_index.update_guideline(guideline)
        
        # Clear cache
        self.cache.clear()
    
    def delete_guideline(self, guideline_id: str) -> bool:
        """Delete a guideline from the store."""
        guideline = self.guidelines.get(guideline_id)
        if not guideline:
            return False
        
        # Delete from filesystem
        success = self.filesystem.delete_guideline(guideline_id, guideline.category)
        
        if success:
            # Remove from in-memory store
            del self.guidelines[guideline_id]
            
            # Remove from search index
            self.search_index.delete_guideline(guideline_id)
            
            # Clear cache
            self.cache.clear()
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the guideline store."""
        categories = self.get_categories()
        
        stats = {
            'total_guidelines': len(self.guidelines),
            'categories': len(categories),
            'category_list': categories,
            'cache_size': self.cache.size()
        }
        
        # Count guidelines per category
        category_counts = {}
        for guideline in self.guidelines.values():
            category_counts[guideline.category] = category_counts.get(guideline.category, 0) + 1
        
        stats['guidelines_per_category'] = category_counts
        
        return stats
    
    def reload_guidelines(self) -> int:
        """Reload all guidelines from filesystem."""
        self._initialized = False
        self.cache.clear()
        
        # Load all guidelines from filesystem (sync version for dynamic management)
        guidelines = self.filesystem.load_all_guidelines()
        
        # Clear existing data
        self.guidelines.clear()
        self.search_index.clear()
        
        # Index and store guidelines
        for guideline in guidelines:
            self.guidelines[guideline.id] = guideline
            self.search_index.add_guideline(guideline)
        
        self._initialized = True
        print(f"Reloaded {len(guidelines)} architecture guidelines")
        return len(guidelines)
    
    # Dynamic category management methods
    
    def create_category(self, category_name: str, description: Optional[str] = None,
                       parent_category: Optional[str] = None) -> bool:
        """Create a new category."""
        try:
            # Create category in filesystem
            success = self.filesystem.create_category(category_name, description, parent_category)
            
            if success:
                # Clear cache to reflect new category
                self.cache.clear()
            
            return success
        except Exception as e:
            print(f"Error creating category: {e}")
            return False
    
    def rename_category(self, old_name: str, new_name: str) -> int:
        """Rename a category and update all guidelines in it."""
        updated_count = 0
        
        # Get all guidelines in the old category
        guidelines_to_update = [
            g for g in self.guidelines.values() 
            if g.category == old_name
        ]
        
        # Rename category in filesystem
        if self.filesystem.rename_category(old_name, new_name):
            # Update each guideline
            for guideline in guidelines_to_update:
                guideline.category = new_name
                self.guidelines[guideline.id] = guideline
                self.search_index.update_guideline(guideline)
                updated_count += 1
            
            # Clear cache
            self.cache.clear()
        
        return updated_count
    
    def delete_category(self, category_name: str, force: bool = False) -> int:
        """Delete a category and optionally all its guidelines."""
        # Check if category has guidelines
        guidelines_in_category = [
            g for g in self.guidelines.values() 
            if g.category == category_name
        ]
        
        if guidelines_in_category and not force:
            return -1  # Category not empty
        
        deleted_count = 0
        
        # Delete all guidelines in the category if force=True
        if force:
            for guideline in guidelines_in_category:
                if self.delete_guideline(guideline.id):
                    deleted_count += 1
        
        # Delete the category directory
        self.filesystem.delete_category(category_name)
        
        # Clear cache
        self.cache.clear()
        
        return deleted_count
    
    def get_category_details(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about all categories."""
        category_info = {}
        
        # Get category metadata from filesystem
        category_metadata = self.filesystem.get_category_metadata()
        
        # Count guidelines per category
        for guideline in self.guidelines.values():
            category = guideline.category
            if category not in category_info:
                category_info[category] = {
                    'count': 0,
                    'description': category_metadata.get(category, {}).get('description'),
                    'subcategories': set()
                }
            
            category_info[category]['count'] += 1
            
            if guideline.subcategory:
                category_info[category]['subcategories'].add(guideline.subcategory)
        
        # Convert sets to lists
        for info in category_info.values():
            info['subcategories'] = sorted(list(info['subcategories']))
        
        return category_info