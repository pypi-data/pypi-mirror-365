"""Search index implementation using Whoosh."""

import os
import tempfile
from typing import List, Optional
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.writing import IndexWriter

from ..models.types import ArchitectureGuideline, SearchFilters


class SearchIndex:
    """Full-text search index for architecture guidelines."""
    
    def __init__(self, index_dir: Optional[str] = None):
        """Initialize the search index."""
        if index_dir is None:
            # Use a temporary directory if none specified
            self._temp_dir = tempfile.mkdtemp()
            self.index_dir = self._temp_dir
        else:
            self.index_dir = index_dir
            self._temp_dir = None
        
        # Define the schema for our search index
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            content=TEXT(stored=True),
            category=TEXT(stored=True),
            tags=TEXT(stored=True),
            examples=TEXT(stored=True),
            patterns=TEXT(stored=True),
            tech_stack=TEXT(stored=True)
        )
        
        self._index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or open the Whoosh index."""
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
        
        if index.exists_in(self.index_dir):
            self._index = index.open_dir(self.index_dir)
        else:
            self._index = index.create_in(self.index_dir, self.schema)
    
    def add_guideline(self, guideline: ArchitectureGuideline) -> None:
        """Add a guideline to the search index."""
        writer: IndexWriter = self._index.writer()
        
        try:
            # Prepare searchable content
            examples_text = ' '.join([
                f"{ex.title} {ex.code} {ex.description}"
                for ex in guideline.examples
            ])
            
            patterns_text = ' '.join([
                f"{p.name} {p.description} {p.implementation}"
                for p in guideline.patterns
            ])
            
            tech_stack_text = ' '.join(guideline.metadata.tech_stack or [])
            tags_text = ' '.join(guideline.tags)
            
            writer.add_document(
                id=guideline.id,
                title=guideline.title,
                content=guideline.content,
                category=guideline.category,
                tags=tags_text,
                examples=examples_text,
                patterns=patterns_text,
                tech_stack=tech_stack_text
            )
            
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e
    
    def search(self, query: str, filters: Optional[SearchFilters] = None, 
               limit: int = 10) -> List[str]:
        """Search the index and return matching guideline IDs."""
        with self._index.searcher() as searcher:
            # Create multifield query parser for searching across multiple fields
            from whoosh.qparser import MultifieldParser
            search_fields = ["title", "content", "tags", "examples", "patterns"]
            parser = MultifieldParser(search_fields, self._index.schema)
            
            # Build the search query
            query_obj = parser.parse(query)
            
            # Apply filters if provided
            if filters:
                filter_queries = []
                
                if filters.category:
                    category_parser = QueryParser("category", self._index.schema)
                    filter_queries.append(category_parser.parse(filters.category))
                
                if filters.tags:
                    for tag in filters.tags:
                        tag_parser = QueryParser("tags", self._index.schema)
                        filter_queries.append(tag_parser.parse(tag))
                
                if filters.tech_stack:
                    for tech in filters.tech_stack:
                        tech_parser = QueryParser("tech_stack", self._index.schema)
                        filter_queries.append(tech_parser.parse(tech))
                
                # Combine filters with AND logic
                if filter_queries:
                    from whoosh.query import And
                    combined_filter = And(filter_queries)
                    query_obj = And([query_obj, combined_filter])
            
            # Execute search
            results = searcher.search(query_obj, limit=limit)
            
            # Return guideline IDs
            return [hit['id'] for hit in results]
    
    def update_guideline(self, guideline: ArchitectureGuideline) -> None:
        """Update an existing guideline in the index."""
        writer: IndexWriter = self._index.writer()
        
        try:
            # Delete existing document
            writer.delete_by_term('id', guideline.id)
            
            # Add updated document
            examples_text = ' '.join([
                f"{ex.title} {ex.code} {ex.description}"
                for ex in guideline.examples
            ])
            
            patterns_text = ' '.join([
                f"{p.name} {p.description} {p.implementation}"
                for p in guideline.patterns
            ])
            
            tech_stack_text = ' '.join(guideline.metadata.tech_stack or [])
            tags_text = ' '.join(guideline.tags)
            
            writer.add_document(
                id=guideline.id,
                title=guideline.title,
                content=guideline.content,
                category=guideline.category,
                tags=tags_text,
                examples=examples_text,
                patterns=patterns_text,
                tech_stack=tech_stack_text
            )
            
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e
    
    def delete_guideline(self, guideline_id: str) -> None:
        """Delete a guideline from the index."""
        writer: IndexWriter = self._index.writer()
        
        try:
            writer.delete_by_term('id', guideline_id)
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e
    
    def clear(self) -> None:
        """Clear all documents from the index."""
        writer: IndexWriter = self._index.writer()
        
        try:
            # Delete all documents by using a query that matches everything
            from whoosh.query import Every
            writer.delete_by_query(Every())
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e
    
    def __del__(self):
        """Cleanup temporary directory if created."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            import shutil
            shutil.rmtree(self._temp_dir)