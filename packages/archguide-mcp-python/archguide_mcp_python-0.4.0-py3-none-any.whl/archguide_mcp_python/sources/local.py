"""Local filesystem source provider."""

import os
from pathlib import Path
from typing import Optional, AsyncIterator
from datetime import datetime

from .base import SourceProvider
from ..models.types import ArchitectureGuideline
from ..storage.filesystem import FileSystemStorage


class LocalSourceProvider(SourceProvider):
    """Source provider for local filesystem guidelines."""
    
    def __init__(self, config):
        """Initialize local source provider."""
        super().__init__(config)
        
        # Resolve path
        path = config.path or "./guidelines"
        self.path = Path(path).resolve()
        
        # Use existing filesystem storage
        self.storage = FileSystemStorage(str(self.path))
    
    async def connect(self) -> bool:
        """Verify the local path exists and is accessible."""
        try:
            if not self.path.exists():
                self.metadata.error = f"Path does not exist: {self.path}"
                return False
            
            if not self.path.is_dir():
                self.metadata.error = f"Path is not a directory: {self.path}"
                return False
            
            # Check read permissions
            if not os.access(self.path, os.R_OK):
                self.metadata.error = f"No read access to path: {self.path}"
                return False
            
            return True
            
        except Exception as e:
            self.metadata.error = f"Error accessing path: {str(e)}"
            return False
    
    async def fetch_guidelines(self) -> AsyncIterator[ArchitectureGuideline]:
        """Fetch guidelines from the local filesystem."""
        try:
            # Load all guidelines using existing filesystem storage
            guidelines = self.storage.load_all_guidelines()
            
            for guideline in guidelines:
                yield guideline
                
        except Exception as e:
            self.metadata.error = f"Error loading guidelines: {str(e)}"
            raise
    
    async def get_guideline(self, guideline_id: str) -> Optional[ArchitectureGuideline]:
        """Get a specific guideline by ID from cache."""
        if not self._initialized:
            await self.sync()
        
        return self._guidelines_cache.get(guideline_id)
    
    async def watch_changes(self, callback):
        """Watch for changes in the guidelines directory.
        
        Args:
            callback: Function to call when changes are detected
        """
        # This could be implemented using watchdog or similar libraries
        # For now, it's a placeholder for future enhancement
        raise NotImplementedError("File watching not yet implemented")
    
    def get_categories(self) -> list[str]:
        """Get available categories from the filesystem."""
        return self.storage.get_categories()
    
    def create_guideline_file(self, guideline: ArchitectureGuideline) -> bool:
        """Create a new guideline file in the filesystem.
        
        Args:
            guideline: The guideline to save
            
        Returns:
            True if successful
        """
        try:
            return self.storage.save_guideline(guideline)
        except Exception as e:
            self.metadata.error = f"Error saving guideline: {str(e)}"
            return False
    
    def update_guideline_file(self, guideline: ArchitectureGuideline) -> bool:
        """Update an existing guideline file.
        
        Args:
            guideline: The guideline to update
            
        Returns:
            True if successful
        """
        return self.create_guideline_file(guideline)
    
    def delete_guideline_file(self, guideline_id: str) -> bool:
        """Delete a guideline file.
        
        Args:
            guideline_id: ID of the guideline to delete
            
        Returns:
            True if successful
        """
        try:
            guideline = self._guidelines_cache.get(guideline_id)
            if not guideline:
                return False
            
            # Find the file path
            category_path = self.path / guideline.category
            
            # Look for the file
            for file_path in category_path.glob("*.md"):
                if file_path.stem == guideline_id or \
                   file_path.stem == guideline.title.lower().replace(' ', '-'):
                    file_path.unlink()
                    return True
            
            return False
            
        except Exception as e:
            self.metadata.error = f"Error deleting guideline: {str(e)}"
            return False
    
    def __repr__(self) -> str:
        """String representation."""
        return f"LocalSourceProvider(path='{self.path}', guidelines={self.metadata.total_guidelines})"