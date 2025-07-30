"""Multi-source storage layer with priority resolution."""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
from collections import defaultdict

from ..models.types import ArchitectureGuideline, SearchFilters, ContextFilters
from ..config.models import ArchGuideConfig, MergeStrategy
from ..sources.base import SourceProvider, SourceMetadata
from ..sources.registry import SourceRegistry
from ..utils.cache import CacheManager


class MultiSourceStore:
    """Multi-source storage with priority resolution and caching."""
    
    def __init__(self, config: ArchGuideConfig):
        """Initialize multi-source store."""
        self.config = config
        self.sources: List[SourceProvider] = []
        self.cache = CacheManager()
        self._initialized = False
        self._guidelines: Dict[str, ArchitectureGuideline] = {}
        self._source_map: Dict[str, str] = {}  # guideline_id -> source_name
        self._last_sync: Optional[datetime] = None
    
    async def initialize(self) -> int:
        """Initialize all sources and load guidelines."""
        if self._initialized:
            return len(self._guidelines)
        
        # Create source providers
        await self._create_sources()
        
        # Connect to all sources
        await self._connect_sources()
        
        # Load guidelines
        count = await self._load_guidelines()
        
        self._initialized = True
        self._last_sync = datetime.now()
        
        print(f"Loaded {count} guidelines from {len(self.sources)} sources")
        return count
    
    async def _create_sources(self):
        """Create source providers from configuration."""
        self.sources = []
        
        for source_config in self.config.sources:
            if not source_config.enabled:
                continue
            
            try:
                provider = SourceRegistry.create_provider(source_config)
                self.sources.append(provider)
            except Exception as e:
                print(f"Failed to create source '{source_config.name}': {e}")
    
    async def _connect_sources(self):
        """Connect to all sources, handling failures gracefully."""
        tasks = []
        
        for source in self.sources:
            tasks.append(self._connect_source(source))
        
        if self.config.parallel_fetch:
            # Connect to sources in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Remove failed sources
            successful_sources = []
            for source, result in zip(self.sources, results):
                if isinstance(result, Exception):
                    print(f"Failed to connect to source '{source.config.name}': {result}")
                elif result:
                    successful_sources.append(source)
                else:
                    print(f"Failed to connect to source '{source.config.name}'")
            
            self.sources = successful_sources
        else:
            # Connect to sources sequentially
            successful_sources = []
            for source in self.sources:
                try:
                    if await self._connect_source(source):
                        successful_sources.append(source)
                    else:
                        print(f"Failed to connect to source '{source.config.name}'")
                except Exception as e:
                    print(f"Error connecting to source '{source.config.name}': {e}")
            
            self.sources = successful_sources
    
    async def _connect_source(self, source: SourceProvider) -> bool:
        """Connect to a single source with authentication."""
        try:
            # Authenticate if needed
            if source.config.auth:
                if not await source.authenticate(source.config.auth):
                    return False
            
            # Connect
            return await source.connect()
            
        except Exception as e:
            print(f"Connection error for source '{source.config.name}': {e}")
            return False
    
    async def _load_guidelines(self) -> int:
        """Load guidelines from all sources with priority resolution."""
        self._guidelines.clear()
        self._source_map.clear()
        
        # Get sources ordered by priority (highest first)
        sources_by_priority = sorted(self.sources, key=lambda s: s.config.priority, reverse=True)
        
        if self.config.merge_strategy == MergeStrategy.OVERRIDE:
            await self._load_with_override(sources_by_priority)
        elif self.config.merge_strategy == MergeStrategy.COMBINE:
            await self._load_with_combine(sources_by_priority)
        else:  # LAYERED
            await self._load_with_layered(sources_by_priority)
        
        return len(self._guidelines)
    
    async def _load_with_override(self, sources: List[SourceProvider]):
        """Load guidelines with override strategy (higher priority replaces lower)."""
        for source in reversed(sources):  # Start with lowest priority
            try:
                await source.sync()
                
                async for guideline in source.fetch_guidelines():
                    # Always replace - higher priority sources will override later
                    self._guidelines[guideline.id] = guideline
                    self._source_map[guideline.id] = source.config.name
                    
            except Exception as e:
                print(f"Error loading from source '{source.config.name}': {e}")
    
    async def _load_with_combine(self, sources: List[SourceProvider]):
        """Load guidelines with combine strategy (all available, conflicts favor higher priority)."""
        guideline_sources: Dict[str, tuple[ArchitectureGuideline, int]] = {}
        
        for source in sources:
            try:
                await source.sync()
                
                async for guideline in source.fetch_guidelines():
                    # Keep track of priority for conflict resolution
                    if guideline.id not in guideline_sources or \
                       source.config.priority > guideline_sources[guideline.id][1]:
                        guideline_sources[guideline.id] = (guideline, source.config.priority)
                        self._source_map[guideline.id] = source.config.name
                        
            except Exception as e:
                print(f"Error loading from source '{source.config.name}': {e}")
        
        # Extract final guidelines
        self._guidelines = {gid: data[0] for gid, data in guideline_sources.items()}
    
    async def _load_with_layered(self, sources: List[SourceProvider]):
        """Load guidelines with layered strategy (inheritance and extension)."""
        # Start with base guidelines from lowest priority sources
        for source in reversed(sources):
            try:
                await source.sync()
                
                async for guideline in source.fetch_guidelines():
                    if guideline.id not in self._guidelines:
                        # New guideline
                        self._guidelines[guideline.id] = guideline
                        self._source_map[guideline.id] = source.config.name
                    else:
                        # Extend existing guideline
                        existing = self._guidelines[guideline.id]
                        extended = self._extend_guideline(existing, guideline)
                        self._guidelines[guideline.id] = extended
                        # Keep the original source as primary
                        
            except Exception as e:
                print(f"Error loading from source '{source.config.name}': {e}")
    
    def _extend_guideline(self, base: ArchitectureGuideline, extension: ArchitectureGuideline) -> ArchitectureGuideline:
        """Extend a guideline with content from another (layered strategy)."""
        # Create a copy of the base guideline
        extended_data = base.model_dump()
        
        # Extend content
        if extension.content and extension.content not in base.content:
            extended_data['content'] += f"\n\n## Extended Content\n\n{extension.content}"
        
        # Merge tags
        extended_tags = list(set(base.tags + extension.tags))
        extended_data['tags'] = extended_tags
        
        # Merge examples
        extended_examples = base.examples + extension.examples
        extended_data['examples'] = extended_examples
        
        # Merge patterns
        extended_patterns = base.patterns + extension.patterns
        extended_data['patterns'] = extended_patterns
        
        # Merge anti-patterns
        extended_anti_patterns = base.anti_patterns + extension.anti_patterns
        extended_data['anti_patterns'] = extended_anti_patterns
        
        # Update metadata
        extended_data['metadata']['last_updated'] = datetime.now()
        
        return ArchitectureGuideline(**extended_data)
    
    async def sync_all(self) -> Dict[str, int]:
        """Sync all sources and reload guidelines."""
        if not self._initialized:
            await self.initialize()
            return {}
        
        results = {}
        
        for source in self.sources:
            try:
                count = await source.sync()
                results[source.config.name] = count
            except Exception as e:
                print(f"Sync error for source '{source.config.name}': {e}")
                results[source.config.name] = -1
        
        # Reload guidelines after sync
        await self._load_guidelines()
        self._last_sync = datetime.now()
        
        return results
    
    async def sync_source(self, source_name: str) -> int:
        """Sync a specific source."""
        source = self._find_source(source_name)
        if not source:
            raise ValueError(f"Source '{source_name}' not found")
        
        count = await source.sync()
        
        # Reload all guidelines to handle priority changes
        await self._load_guidelines()
        
        return count
    
    def _find_source(self, name: str) -> Optional[SourceProvider]:
        """Find a source by name."""
        for source in self.sources:
            if source.config.name == name:
                return source
        return None
    
    # Standard guideline access methods
    
    def get_guideline_by_id(self, guideline_id: str) -> Optional[ArchitectureGuideline]:
        """Get a guideline by ID."""
        return self._guidelines.get(guideline_id)
    
    def get_guidelines_by_ids(self, guideline_ids: List[str]) -> List[ArchitectureGuideline]:
        """Get multiple guidelines by IDs."""
        return [self._guidelines[gid] for gid in guideline_ids if gid in self._guidelines]
    
    def get_guidelines_by_topic(self, topic: str, filters: Optional[ContextFilters] = None) -> List[ArchitectureGuideline]:
        """Get guidelines by topic/category."""
        results = []
        
        for guideline in self._guidelines.values():
            # Check category match
            if topic.lower() in guideline.category.lower() or topic.lower() in guideline.title.lower():
                # Apply context filters if provided
                if filters and not self._matches_context(guideline, filters):
                    continue
                results.append(guideline)
        
        return results
    
    def _matches_context(self, guideline: ArchitectureGuideline, filters: ContextFilters) -> bool:
        """Check if guideline matches context filters."""
        if filters.tech_stack:
            if not guideline.metadata.tech_stack:
                return False
            if not any(tech in guideline.metadata.tech_stack for tech in filters.tech_stack):
                return False
        
        return True
    
    def search_guidelines(self, query: str, filters: Optional[SearchFilters] = None, limit: int = 10) -> List[ArchitectureGuideline]:
        """Search guidelines across all sources."""
        results = []
        query_lower = query.lower()
        
        for guideline in self._guidelines.values():
            # Apply filters
            if filters:
                if filters.category and guideline.category != filters.category:
                    continue
                if filters.tags and not any(tag in guideline.tags for tag in filters.tags):
                    continue
                if filters.tech_stack and guideline.metadata.tech_stack:
                    if not any(tech in guideline.metadata.tech_stack for tech in filters.tech_stack):
                        continue
            
            # Search match
            if (query_lower in guideline.title.lower() or
                query_lower in guideline.content.lower() or
                any(query_lower in tag.lower() for tag in guideline.tags)):
                results.append(guideline)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        categories = set()
        for guideline in self._guidelines.values():
            categories.add(guideline.category)
        return sorted(list(categories))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        categories = defaultdict(int)
        sources_stats = {}
        
        for guideline in self._guidelines.values():
            categories[guideline.category] += 1
        
        for source in self.sources:
            metadata = source.get_metadata()
            sources_stats[source.config.name] = {
                'total_guidelines': metadata.total_guidelines,
                'last_sync': metadata.last_sync,
                'error': metadata.error
            }
        
        return {
            'total_guidelines': len(self._guidelines),
            'categories': len(categories),
            'guidelines_per_category': dict(categories),
            'sources': sources_stats,
            'last_sync': self._last_sync,
            'merge_strategy': self.config.merge_strategy.value
        }
    
    def get_source_for_guideline(self, guideline_id: str) -> Optional[str]:
        """Get the source name for a specific guideline."""
        return self._source_map.get(guideline_id)
    
    def get_source_metadata(self) -> List[SourceMetadata]:
        """Get metadata for all sources."""
        return [source.get_metadata() for source in self.sources]
    
    async def close(self):
        """Close all sources and clean up."""
        for source in self.sources:
            await source.close()
    
    @property
    def guidelines(self) -> Dict[str, ArchitectureGuideline]:
        """Get all loaded guidelines (for compatibility)."""
        return self._guidelines