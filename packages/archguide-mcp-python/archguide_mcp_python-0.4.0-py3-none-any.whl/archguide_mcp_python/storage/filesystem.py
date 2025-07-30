"""Filesystem storage for architecture guidelines."""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import frontmatter

from ..models.types import ArchitectureGuideline, GuidelineMetadata
from ..parsers.content import ContentParser


class FileSystemStorage:
    """File-based storage for architecture guidelines."""
    
    def __init__(self, guidelines_path: str = "./guidelines"):
        """Initialize filesystem storage."""
        self.guidelines_path = Path(guidelines_path)
        self.parser = ContentParser()
    
    def load_all_guidelines(self) -> List[ArchitectureGuideline]:
        """Load all guidelines from the filesystem."""
        guidelines = []
        
        if not self.guidelines_path.exists():
            return guidelines
        
        # Get all category directories
        categories = [
            d for d in self.guidelines_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        
        for category_dir in categories:
            category = category_dir.name
            markdown_files = list(category_dir.glob("*.md"))
            
            for file_path in markdown_files:
                guideline = self._load_guideline(file_path, category)
                if guideline:
                    guidelines.append(guideline)
        
        return guidelines
    
    def _load_guideline(self, file_path: Path, category: str) -> Optional[ArchitectureGuideline]:
        """Load a single guideline from a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Extract frontmatter data
            metadata_dict = post.metadata
            markdown_content = post.content
            
            # Parse content for examples, patterns, and anti-patterns
            examples, patterns, anti_patterns = self.parser.parse_content(markdown_content)
            
            # Create metadata object
            metadata = GuidelineMetadata(
                author=metadata_dict.get('author', 'Unknown'),
                reviewers=metadata_dict.get('reviewers'),
                created=self._parse_date(metadata_dict.get('created')),
                last_updated=self._parse_date(metadata_dict.get('lastUpdated', metadata_dict.get('last_updated'))),
                applicability=metadata_dict.get('applicability', []),
                tech_stack=metadata_dict.get('techStack', metadata_dict.get('tech_stack')),
                prerequisites=metadata_dict.get('prerequisites'),
                related_guidelines=metadata_dict.get('relatedGuidelines', metadata_dict.get('related_guidelines'))
            )
            
            # Create guideline object
            guideline = ArchitectureGuideline(
                id=metadata_dict.get('id', file_path.stem),
                title=metadata_dict.get('title', file_path.stem.replace('-', ' ').title()),
                category=category,
                subcategory=metadata_dict.get('subcategory'),
                tags=metadata_dict.get('tags', []),
                content=markdown_content,
                examples=examples,
                patterns=patterns,
                anti_patterns=anti_patterns,
                version=metadata_dict.get('version', '1.0.0'),
                metadata=metadata
            )
            
            return guideline
            
        except Exception as e:
            print(f"Error loading guideline from {file_path}: {e}")
            return None
    
    def _parse_date(self, date_value) -> datetime:
        """Parse date from various formats."""
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            try:
                # Try parsing ISO format first
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try parsing YYYY-MM-DD format
                    return datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    pass
        
        # Default to current time if parsing fails
        return datetime.now()
    
    def save_guideline(self, guideline: ArchitectureGuideline) -> None:
        """Save a guideline to the filesystem."""
        # Create category directory if it doesn't exist
        category_dir = self.guidelines_path / guideline.category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{guideline.id}.md"
        file_path = category_dir / filename
        
        # Prepare frontmatter
        metadata = {
            'id': guideline.id,
            'title': guideline.title,
            'category': guideline.category,
            'tags': guideline.tags,
            'version': guideline.version,
            'author': guideline.metadata.author,
            'created': guideline.metadata.created.isoformat(),
            'lastUpdated': guideline.metadata.last_updated.isoformat(),
            'applicability': guideline.metadata.applicability
        }
        
        if guideline.subcategory:
            metadata['subcategory'] = guideline.subcategory
        
        if guideline.metadata.reviewers:
            metadata['reviewers'] = guideline.metadata.reviewers
        
        if guideline.metadata.tech_stack:
            metadata['techStack'] = guideline.metadata.tech_stack
        
        if guideline.metadata.prerequisites:
            metadata['prerequisites'] = guideline.metadata.prerequisites
        
        if guideline.metadata.related_guidelines:
            metadata['relatedGuidelines'] = guideline.metadata.related_guidelines
        
        # Create frontmatter post
        post = frontmatter.Post(guideline.content, **metadata)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def delete_guideline(self, guideline_id: str, category: str) -> bool:
        """Delete a guideline from the filesystem."""
        file_path = self.guidelines_path / category / f"{guideline_id}.md"
        
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def get_categories(self) -> List[str]:
        """Get list of available categories."""
        if not self.guidelines_path.exists():
            return []
        
        categories = [
            d.name for d in self.guidelines_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        
        return sorted(categories)
    
    def create_category(self, category_name: str, description: Optional[str] = None,
                       parent_category: Optional[str] = None) -> bool:
        """Create a new category directory."""
        try:
            # Create the category path
            if parent_category:
                category_path = self.guidelines_path / parent_category / category_name
            else:
                category_path = self.guidelines_path / category_name
            
            # Create the directory
            category_path.mkdir(parents=True, exist_ok=False)
            
            # Create a metadata file for the category
            if description:
                metadata_file = category_path / ".category.json"
                import json
                with open(metadata_file, 'w') as f:
                    json.dump({
                        "name": category_name,
                        "description": description,
                        "created": datetime.now().isoformat()
                    }, f, indent=2)
            
            return True
            
        except FileExistsError:
            return False
        except Exception as e:
            print(f"Error creating category {category_name}: {e}")
            return False
    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """Rename a category directory."""
        try:
            old_path = self.guidelines_path / old_name
            new_path = self.guidelines_path / new_name
            
            if not old_path.exists():
                return False
            
            if new_path.exists():
                return False
            
            # Rename the directory
            old_path.rename(new_path)
            
            # Update metadata file if it exists
            metadata_file = new_path / ".category.json"
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                metadata['name'] = new_name
                metadata['renamed_from'] = old_name
                metadata['renamed_at'] = datetime.now().isoformat()
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error renaming category from {old_name} to {new_name}: {e}")
            return False
    
    def delete_category(self, category_name: str) -> bool:
        """Delete a category directory."""
        try:
            category_path = self.guidelines_path / category_name
            
            if not category_path.exists():
                return False
            
            # Remove the directory and all its contents
            import shutil
            shutil.rmtree(category_path)
            
            return True
            
        except Exception as e:
            print(f"Error deleting category {category_name}: {e}")
            return False
    
    def get_category_metadata(self) -> Dict[str, Dict[str, str]]:
        """Get metadata for all categories."""
        metadata = {}
        
        if not self.guidelines_path.exists():
            return metadata
        
        for category_dir in self.guidelines_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
            
            category_name = category_dir.name
            metadata_file = category_dir / ".category.json"
            
            if metadata_file.exists():
                try:
                    import json
                    with open(metadata_file, 'r') as f:
                        category_metadata = json.load(f)
                    metadata[category_name] = category_metadata
                except Exception as e:
                    print(f"Error reading metadata for category {category_name}: {e}")
            else:
                metadata[category_name] = {"name": category_name}
        
        return metadata