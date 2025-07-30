"""Base source provider interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, AsyncIterator
from pydantic import BaseModel

from ..models.types import ArchitectureGuideline
from ..config.models import GuidelineSourceConfig, AuthConfig


class SourceMetadata(BaseModel):
    """Metadata about a guideline source."""
    name: str
    type: str
    last_sync: Optional[datetime] = None
    total_guidelines: int = 0
    available_categories: List[str] = []
    available_tags: List[str] = []
    version: Optional[str] = None
    error: Optional[str] = None


class SourceProvider(ABC):
    """Abstract base class for guideline source providers."""
    
    def __init__(self, config: GuidelineSourceConfig):
        """Initialize the source provider with configuration."""
        self.config = config
        self.metadata = SourceMetadata(
            name=config.name,
            type=config.type.value
        )
        self._guidelines_cache: Dict[str, ArchitectureGuideline] = {}
        self._initialized = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the source and verify access.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def fetch_guidelines(self) -> AsyncIterator[ArchitectureGuideline]:
        """Fetch guidelines from the source.
        
        Yields:
            ArchitectureGuideline objects
        """
        pass
    
    @abstractmethod
    async def get_guideline(self, guideline_id: str) -> Optional[ArchitectureGuideline]:
        """Get a specific guideline by ID.
        
        Args:
            guideline_id: The ID of the guideline to fetch
            
        Returns:
            The guideline if found, None otherwise
        """
        pass
    
    async def sync(self) -> int:
        """Sync guidelines from the source.
        
        Returns:
            Number of guidelines synced
        """
        try:
            # Clear cache
            self._guidelines_cache.clear()
            
            # Reset metadata
            self.metadata.error = None
            self.metadata.total_guidelines = 0
            categories = set()
            tags = set()
            
            # Fetch all guidelines
            async for guideline in self.fetch_guidelines():
                # Apply filters
                if self._should_include_guideline(guideline):
                    self._guidelines_cache[guideline.id] = guideline
                    self.metadata.total_guidelines += 1
                    categories.add(guideline.category)
                    tags.update(guideline.tags)
            
            # Update metadata
            self.metadata.last_sync = datetime.now()
            self.metadata.available_categories = sorted(list(categories))
            self.metadata.available_tags = sorted(list(tags))
            
            self._initialized = True
            return self.metadata.total_guidelines
            
        except Exception as e:
            self.metadata.error = str(e)
            raise
    
    def _should_include_guideline(self, guideline: ArchitectureGuideline) -> bool:
        """Check if a guideline should be included based on filters."""
        # Check category filters
        if self.config.include_categories:
            if guideline.category not in self.config.include_categories:
                return False
        
        if self.config.exclude_categories:
            if guideline.category in self.config.exclude_categories:
                return False
        
        # Check tag filters
        if self.config.include_tags:
            if not any(tag in guideline.tags for tag in self.config.include_tags):
                return False
        
        if self.config.exclude_tags:
            if any(tag in guideline.tags for tag in self.config.exclude_tags):
                return False
        
        return True
    
    async def list_guidelines(self) -> List[ArchitectureGuideline]:
        """List all cached guidelines."""
        if not self._initialized:
            await self.sync()
        return list(self._guidelines_cache.values())
    
    async def search_guidelines(
        self, 
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[ArchitectureGuideline]:
        """Search guidelines within this source.
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            
        Returns:
            List of matching guidelines
        """
        if not self._initialized:
            await self.sync()
        
        results = []
        query_lower = query.lower()
        
        for guideline in self._guidelines_cache.values():
            # Check category filter
            if category and guideline.category != category:
                continue
            
            # Check tag filter
            if tags and not any(tag in guideline.tags for tag in tags):
                continue
            
            # Search in title, content, and tags
            if (query_lower in guideline.title.lower() or
                query_lower in guideline.content.lower() or
                any(query_lower in tag.lower() for tag in guideline.tags)):
                results.append(guideline)
        
        return results
    
    def get_metadata(self) -> SourceMetadata:
        """Get source metadata."""
        return self.metadata
    
    async def authenticate(self, auth: AuthConfig) -> bool:
        """Authenticate with the source.
        
        Args:
            auth: Authentication configuration
            
        Returns:
            True if authentication successful
        """
        # Default implementation - override in subclasses that need auth
        return True
    
    async def close(self):
        """Close connections and clean up resources."""
        # Default implementation - override in subclasses that need cleanup
        pass
    
    def __repr__(self) -> str:
        """String representation of the source provider."""
        return f"{self.__class__.__name__}(name='{self.config.name}', type='{self.config.type}')"