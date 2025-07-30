"""FastMCP server implementation for ArchGuide."""

import asyncio
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .models.types import (
    GuidelineRequest, SearchRequest, ComplianceRequest, 
    ContextFilters, SearchFilters, CreateGuidelineRequest, UpdateGuidelineRequest,
    ArchitectureGuideline, GuidelineMetadata, Pattern, AntiPattern, CodeExample
)
from .storage.store import GuidelineStore
from .storage.multisource import MultiSourceStore
from .config.models import load_config
from .utils.formatters import (
    format_guideline_for_ai, format_search_results,
    format_compliance_report, format_categories
)

# Import version info
from . import __version__, __author__, __description__


# MCP server instance
mcp = FastMCP("ArchGuide MCP Server")

# Global store instance
store: Optional[MultiSourceStore] = None


async def get_store() -> MultiSourceStore:
    """Get or initialize the multi-source guideline store."""
    global store
    if store is None:
        # Load configuration
        config = load_config()
        
        # If no sources configured, use legacy fallback
        if not config.sources:
            from .config.models import get_default_config
            config = get_default_config()
        
        store = MultiSourceStore(config)
        await store.initialize()
    return store


async def get_legacy_store() -> GuidelineStore:
    """Get legacy single-source store for backward compatibility."""
    # Try custom path first, then local development path, then packaged path
    guidelines_path = os.getenv("GUIDELINES_PATH")
    if not guidelines_path:
        # Try local development directory first
        local_path = "./guidelines"
        if os.path.exists(local_path):
            guidelines_path = local_path
        else:
            # Try packaged guidelines
            import sys
            import sysconfig
            
            # Try to find guidelines in the package installation
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "..", "..", "guidelines"),
                os.path.join(os.path.dirname(__file__), "guidelines"),  # Packaged with the module
                os.path.join(sysconfig.get_path("data"), "guidelines"),
                os.path.join(sys.prefix, "guidelines"),
                os.path.join(sys.prefix, "share", "guidelines"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    guidelines_path = path
                    break
            else:
                guidelines_path = "./guidelines"  # fallback
    
    legacy_store = GuidelineStore(guidelines_path)
    await legacy_store.initialize()
    return legacy_store


@mcp.tool()
async def get_version() -> str:
    """
    Get the current version and information about the ArchGuide MCP server.
    
    Returns:
        Version information including version number, author, and description
    """
    return f"""ArchGuide MCP Server Information:
- Version: {__version__}
- Author: {__author__}
- Description: {__description__}
- Python Package: archguide-mcp-python
- PyPI: https://pypi.org/project/archguide-mcp-python/
"""


@mcp.tool()
async def get_architecture_guideline(
    topic: str,
    context: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None,
    include_examples: bool = True
) -> str:
    """
    Fetch architecture guidelines for a specific topic, pattern, or category.
    
    Args:
        topic: The architecture topic (e.g., "microservices", "caching", "api-design")
        context: Additional context for filtering (tech_stack, scale, domain)
        version: Specific version of guidelines (default: latest)
        include_examples: Include code examples (default: true)
    
    Returns:
        Formatted architecture guidelines for the specified topic
    """
    try:
        guideline_store = await get_store()
        
        # Parse context filters
        context_filters = None
        if context:
            context_filters = ContextFilters(**context)
        
        # Get guidelines by topic
        guidelines = guideline_store.get_guidelines_by_topic(topic, context_filters)
        
        if not guidelines:
            return f"No architecture guidelines found for topic: {topic}. Try searching with different terms or check available categories using the list-categories tool."
        
        # Filter by version if specified
        if version:
            guidelines = [g for g in guidelines if g.version == version]
            if not guidelines:
                return f"No guidelines found for topic '{topic}' with version '{version}'."
        
        # Format for AI consumption
        return format_guideline_for_ai(guidelines, include_examples)
        
    except Exception as e:
        return f"Error fetching guidelines: {str(e)}"


@mcp.tool()
async def search_patterns(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10
) -> str:
    """
    Search for architecture patterns, best practices, and solutions.
    
    Args:
        query: Search query for patterns and guidelines
        filters: Optional filters (category, tags, tech_stack)
        limit: Maximum number of results (default: 10)
    
    Returns:
        Search results with matching patterns and guidelines
    """
    try:
        guideline_store = await get_store()
        
        # Parse search filters
        search_filters = None
        if filters:
            search_filters = SearchFilters(**filters)
        
        # Search guidelines
        results = guideline_store.search_guidelines(query, search_filters, limit)
        
        if not results:
            return f'No architecture patterns found matching "{query}". Try different search terms or browse available categories.'
        
        # Format search results
        return format_search_results(results)
        
    except Exception as e:
        return f"Search error: {str(e)}"


@mcp.tool()
async def list_categories() -> str:
    """
    List all available architecture guideline categories.
    
    Returns:
        List of available categories
    """
    try:
        guideline_store = await get_store()
        categories = guideline_store.get_categories()
        return format_categories(categories)
        
    except Exception as e:
        return f"Error listing categories: {str(e)}"


@mcp.tool()
async def check_compliance(
    design: str,
    guidelines: Optional[List[str]] = None
) -> str:
    """
    Check if a design or code snippet complies with architecture guidelines.
    
    Args:
        design: Design description or code snippet to check
        guidelines: Specific guideline IDs to check against (optional)
    
    Returns:
        Compliance report with violations and recommendations
    """
    try:
        guideline_store = await get_store()
        
        # Get guidelines to check against
        if guidelines:
            guideline_objects = guideline_store.get_guidelines_by_ids(guidelines)
        else:
            # Use all guidelines if none specified
            guideline_objects = list(guideline_store.guidelines.values())
        
        if not guideline_objects:
            return "No guidelines available for compliance check."
        
        # Generate compliance report
        return format_compliance_report(guideline_objects, design)
        
    except Exception as e:
        return f"Compliance check error: {str(e)}"


@mcp.tool()
async def get_guidelines_path() -> str:
    """
    Get information about sources and paths being used by the server.
    
    Returns:
        Detailed information about sources and guidelines
    """
    multisource_store = await get_store()
    
    # Get source metadata
    source_info = []
    for metadata in multisource_store.get_source_metadata():
        source_info.append(f"""
Source: {metadata.name} ({metadata.type})
- Guidelines: {metadata.total_guidelines}
- Categories: {len(metadata.available_categories)}
- Last Sync: {metadata.last_sync or 'Never'}
- Error: {metadata.error or 'None'}
- Available Categories: {', '.join(metadata.available_categories) if metadata.available_categories else 'None'}""")
    
    # Overall stats
    stats = multisource_store.get_stats()
    
    return f"""Multi-Source Guidelines Information:
Total Guidelines: {stats['total_guidelines']}
Total Categories: {stats['categories']}
Merge Strategy: {stats['merge_strategy']}
Last Sync: {stats['last_sync'] or 'Never'}

Guidelines per Category:
{chr(10).join(f'- {cat}: {count}' for cat, count in stats['guidelines_per_category'].items())}

Sources:
{chr(10).join(source_info)}

Environment:
- GUIDELINES_PATH: {os.getenv("GUIDELINES_PATH", "not set")}
- Local ./guidelines exists: {os.path.exists("./guidelines")}
- Config file search paths: .archguide.yaml, archguide.yaml, ~/.archguide/config.yaml"""


@mcp.tool()
async def get_server_stats() -> str:
    """
    Get statistics about the ArchGuide server.
    
    Returns:
        Server statistics including guideline counts and categories
    """
    try:
        guideline_store = await get_store()
        stats = guideline_store.get_stats()
        
        lines = [
            "# ArchGuide Server Statistics",
            "",
            f"**Total Guidelines**: {stats['total_guidelines']}",
            f"**Categories**: {stats['categories']}",
            f"**Cache Size**: {stats['cache_size']} items",
            "",
            "## Guidelines per Category:",
        ]
        
        for category, count in stats['guidelines_per_category'].items():
            lines.append(f"- **{category}**: {count}")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error getting server stats: {str(e)}"


@mcp.tool()
async def add_guideline(
    title: str,
    category: str,
    content: str,
    subcategory: Optional[str] = None,
    tags: Optional[List[str]] = None,
    patterns: Optional[List[Dict[str, str]]] = None,
    anti_patterns: Optional[List[Dict[str, str]]] = None,
    examples: Optional[List[Dict[str, str]]] = None,
    tech_stack: Optional[List[str]] = None,
    applicability: Optional[List[str]] = None,
    author: str = "Claude Code User"
) -> str:
    """
    Add a new architecture guideline dynamically.
    
    Args:
        title: Title of the guideline
        category: Category (e.g., 'microservices', 'security', 'cloud-native')
        content: Main content in markdown format
        subcategory: Optional subcategory
        tags: List of tags for categorization
        patterns: List of patterns with keys: name, description, when, implementation, consequences
        anti_patterns: List of anti-patterns with keys: name, description, why, instead
        examples: List of code examples with keys: title, description, language, code
        tech_stack: Applicable technology stack
        applicability: Contexts where this applies (e.g., ['startup', 'enterprise'])
        author: Author of the guideline
    
    Returns:
        Success message with guideline ID
    """
    try:
        guideline_store = await get_store()
        
        # Generate unique ID
        guideline_id = f"{category}-{title.lower().replace(' ', '-')}-{str(uuid.uuid4())[:8]}"
        
        # Create metadata
        now = datetime.now()
        metadata = GuidelineMetadata(
            author=author,
            created=now,
            last_updated=now,
            tech_stack=tech_stack or [],
            applicability=applicability or [],
            prerequisites=None,
            related_guidelines=None
        )
        
        # Parse patterns
        pattern_objects = []
        if patterns:
            for p in patterns:
                pattern_objects.append(Pattern(
                    name=p.get('name', ''),
                    description=p.get('description', ''),
                    when=p.get('when', ''),
                    implementation=p.get('implementation', ''),
                    consequences=p.get('consequences', '').split('\n') if p.get('consequences') else []
                ))
        
        # Parse anti-patterns
        anti_pattern_objects = []
        if anti_patterns:
            for ap in anti_patterns:
                anti_pattern_objects.append(AntiPattern(
                    name=ap.get('name', ''),
                    description=ap.get('description', ''),
                    why=ap.get('why', ''),
                    instead=ap.get('instead', '')
                ))
        
        # Parse examples
        example_objects = []
        if examples:
            for ex in examples:
                example_objects.append(CodeExample(
                    title=ex.get('title', ''),
                    description=ex.get('description', ''),
                    language=ex.get('language', 'text'),
                    code=ex.get('code', ''),
                    explanation=ex.get('explanation')
                ))
        
        # Create guideline
        guideline = ArchitectureGuideline(
            id=guideline_id,
            title=title,
            category=category,
            subcategory=subcategory,
            tags=tags or [],
            content=content,
            examples=example_objects,
            patterns=pattern_objects,
            anti_patterns=anti_pattern_objects,
            metadata=metadata
        )
        
        # Add to store
        guideline_store.add_guideline(guideline)
        
        return f"✅ Successfully added guideline '{title}' with ID: {guideline_id}"
        
    except Exception as e:
        return f"❌ Error adding guideline: {str(e)}"


@mcp.tool()
async def update_guideline(
    guideline_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    patterns: Optional[List[Dict[str, str]]] = None,
    anti_patterns: Optional[List[Dict[str, str]]] = None,
    examples: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Update an existing architecture guideline.
    
    Args:
        guideline_id: ID of the guideline to update
        title: New title (optional)
        content: New content (optional)
        tags: New tags (optional)
        patterns: New patterns list (optional)
        anti_patterns: New anti-patterns list (optional)
        examples: New examples list (optional)
    
    Returns:
        Success or error message
    """
    try:
        guideline_store = await get_store()
        
        # Get existing guideline
        existing = guideline_store.get_guideline_by_id(guideline_id)
        if not existing:
            return f"❌ Guideline with ID '{guideline_id}' not found"
        
        # Update fields if provided
        if title:
            existing.title = title
        if content:
            existing.content = content
        if tags:
            existing.tags = tags
        
        # Update patterns if provided
        if patterns:
            pattern_objects = []
            for p in patterns:
                pattern_objects.append(Pattern(
                    name=p.get('name', ''),
                    description=p.get('description', ''),
                    when=p.get('when', ''),
                    implementation=p.get('implementation', ''),
                    consequences=p.get('consequences', '').split('\n') if p.get('consequences') else []
                ))
            existing.patterns = pattern_objects
        
        # Update anti-patterns if provided
        if anti_patterns:
            anti_pattern_objects = []
            for ap in anti_patterns:
                anti_pattern_objects.append(AntiPattern(
                    name=ap.get('name', ''),
                    description=ap.get('description', ''),
                    why=ap.get('why', ''),
                    instead=ap.get('instead', '')
                ))
            existing.anti_patterns = anti_pattern_objects
        
        # Update examples if provided
        if examples:
            example_objects = []
            for ex in examples:
                example_objects.append(CodeExample(
                    title=ex.get('title', ''),
                    description=ex.get('description', ''),
                    language=ex.get('language', 'text'),
                    code=ex.get('code', ''),
                    explanation=ex.get('explanation')
                ))
            existing.examples = example_objects
        
        # Update metadata
        existing.metadata.last_updated = datetime.now()
        
        # Save changes
        guideline_store.update_guideline(existing)
        
        return f"✅ Successfully updated guideline '{existing.title}' (ID: {guideline_id})"
        
    except Exception as e:
        return f"❌ Error updating guideline: {str(e)}"


@mcp.tool()
async def delete_guideline(guideline_id: str) -> str:
    """
    Delete an architecture guideline.
    
    Args:
        guideline_id: ID of the guideline to delete
    
    Returns:
        Success or error message
    """
    try:
        guideline_store = await get_store()
        
        # Check if guideline exists
        existing = guideline_store.get_guideline_by_id(guideline_id)
        if not existing:
            return f"❌ Guideline with ID '{guideline_id}' not found"
        
        # Delete the guideline
        success = guideline_store.delete_guideline(guideline_id)
        
        if success:
            return f"✅ Successfully deleted guideline '{existing.title}' (ID: {guideline_id})"
        else:
            return f"❌ Failed to delete guideline with ID '{guideline_id}'"
        
    except Exception as e:
        return f"❌ Error deleting guideline: {str(e)}"


@mcp.tool()
async def reload_guidelines() -> str:
    """
    Reload all guidelines from the filesystem.
    
    This will refresh the in-memory store with any changes made to 
    guideline files in the guidelines/ directory.
    
    Returns:
        Status message with count of loaded guidelines
    """
    try:
        guideline_store = await get_store()
        count = guideline_store.reload_guidelines()
        
        return f"✅ Successfully reloaded {count} guidelines from filesystem"
        
    except Exception as e:
        return f"❌ Error reloading guidelines: {str(e)}"


@mcp.tool()
async def create_category(
    category_name: str,
    description: Optional[str] = None,
    parent_category: Optional[str] = None
) -> str:
    """
    Create a new category for organizing architecture guidelines.
    
    Args:
        category_name: Name of the new category (alphanumeric with hyphens)
        description: Optional description of the category
        parent_category: Optional parent category for creating subcategories
    
    Returns:
        Success message or error
    """
    try:
        guideline_store = await get_store()
        
        # Validate category name
        import re
        if not re.match(r'^[a-z0-9-]+$', category_name.lower()):
            return "❌ Category name must contain only lowercase letters, numbers, and hyphens"
        
        # Check if category already exists
        existing_categories = guideline_store.get_categories()
        if category_name in existing_categories:
            return f"❌ Category '{category_name}' already exists"
        
        # Create the category
        success = guideline_store.create_category(category_name, description, parent_category)
        
        if success:
            return f"✅ Successfully created category '{category_name}'"
        else:
            return f"❌ Failed to create category '{category_name}'"
            
    except Exception as e:
        return f"❌ Error creating category: {str(e)}"


@mcp.tool()
async def rename_category(
    old_name: str,
    new_name: str
) -> str:
    """
    Rename an existing category.
    
    Args:
        old_name: Current name of the category
        new_name: New name for the category
    
    Returns:
        Success message with count of updated guidelines
    """
    try:
        guideline_store = await get_store()
        
        # Validate new category name
        import re
        if not re.match(r'^[a-z0-9-]+$', new_name.lower()):
            return "❌ Category name must contain only lowercase letters, numbers, and hyphens"
        
        # Check if old category exists
        existing_categories = guideline_store.get_categories()
        if old_name not in existing_categories:
            return f"❌ Category '{old_name}' does not exist"
        
        # Check if new name already exists
        if new_name in existing_categories:
            return f"❌ Category '{new_name}' already exists"
        
        # Rename the category
        updated_count = guideline_store.rename_category(old_name, new_name)
        
        return f"✅ Successfully renamed category '{old_name}' to '{new_name}'. Updated {updated_count} guidelines."
        
    except Exception as e:
        return f"❌ Error renaming category: {str(e)}"


@mcp.tool()
async def delete_category(
    category_name: str,
    force: bool = False
) -> str:
    """
    Delete a category and optionally all its guidelines.
    
    Args:
        category_name: Name of the category to delete
        force: If True, delete all guidelines in the category. If False, only delete if empty.
    
    Returns:
        Success message or error
    """
    try:
        guideline_store = await get_store()
        
        # Check if category exists
        existing_categories = guideline_store.get_categories()
        if category_name not in existing_categories:
            return f"❌ Category '{category_name}' does not exist"
        
        # Delete the category
        deleted_count = guideline_store.delete_category(category_name, force)
        
        if deleted_count == -1:
            return f"❌ Category '{category_name}' is not empty. Use force=True to delete all guidelines."
        
        return f"✅ Successfully deleted category '{category_name}'. Removed {deleted_count} guidelines."
        
    except Exception as e:
        return f"❌ Error deleting category: {str(e)}"


@mcp.tool()
async def list_categories_detailed() -> str:
    """
    List all categories with detailed information including guideline counts.
    
    Returns:
        Detailed list of categories with statistics
    """
    try:
        guideline_store = await get_store()
        stats = guideline_store.get_stats()
        
        if not stats['guidelines_per_category']:
            return "No categories found."
        
        lines = ["# Architecture Guideline Categories\n"]
        
        for category, count in sorted(stats['guidelines_per_category'].items()):
            lines.append(f"## {category}")
            lines.append(f"- **Guidelines**: {count}")
            
            # Show which sources contribute to this category
            source_contributions = []
            for metadata in guideline_store.get_source_metadata():
                if category in metadata.available_categories:
                    source_contributions.append(metadata.name)
            
            if source_contributions:
                lines.append(f"- **Sources**: {', '.join(source_contributions)}")
            lines.append("")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Error listing categories: {str(e)}"


@mcp.tool()
async def sync_sources(source_name: Optional[str] = None) -> str:
    """
    Sync guidelines from sources.
    
    Args:
        source_name: Optional specific source to sync. If not provided, syncs all sources.
    
    Returns:
        Sync results
    """
    try:
        multisource_store = await get_store()
        
        if source_name:
            # Sync specific source
            count = await multisource_store.sync_source(source_name)
            return f"✅ Synced {count} guidelines from source '{source_name}'"
        else:
            # Sync all sources
            results = await multisource_store.sync_all()
            
            lines = ["# Source Sync Results\n"]
            total_synced = 0
            
            for source, count in results.items():
                if count >= 0:
                    lines.append(f"✅ **{source}**: {count} guidelines")
                    total_synced += count
                else:
                    lines.append(f"❌ **{source}**: Sync failed")
            
            lines.append(f"\n**Total**: {total_synced} guidelines synced")
            return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Sync error: {str(e)}"


@mcp.tool()
async def list_sources() -> str:
    """
    List all configured sources with their status.
    
    Returns:
        List of sources with metadata
    """
    try:
        multisource_store = await get_store()
        source_metadata = multisource_store.get_source_metadata()
        
        if not source_metadata:
            return "No sources configured."
        
        lines = ["# Configured Sources\n"]
        
        for metadata in source_metadata:
            lines.append(f"## {metadata.name}")
            lines.append(f"- **Type**: {metadata.type}")
            lines.append(f"- **Guidelines**: {metadata.total_guidelines}")
            lines.append(f"- **Categories**: {len(metadata.available_categories)}")
            lines.append(f"- **Last Sync**: {metadata.last_sync or 'Never'}")
            
            if metadata.error:
                lines.append(f"- **Error**: {metadata.error}")
            
            if metadata.available_categories:
                lines.append(f"- **Available Categories**: {', '.join(metadata.available_categories)}")
            
            lines.append("")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Error listing sources: {str(e)}"


@mcp.tool()
async def show_guideline_source(guideline_id: str) -> str:
    """
    Show which source a specific guideline comes from.
    
    Args:
        guideline_id: ID of the guideline to check
    
    Returns:
        Source information for the guideline
    """
    try:
        multisource_store = await get_store()
        
        guideline = multisource_store.get_guideline_by_id(guideline_id)
        if not guideline:
            return f"❌ Guideline '{guideline_id}' not found"
        
        source_name = multisource_store.get_source_for_guideline(guideline_id)
        if not source_name:
            return f"⚠️ Source information not available for guideline '{guideline_id}'"
        
        return f"""# Guideline Source Information

**Guideline**: {guideline.title}
**ID**: {guideline_id}
**Category**: {guideline.category}
**Source**: {source_name}
**Tags**: {', '.join(guideline.tags) if guideline.tags else 'None'}
"""
        
    except Exception as e:
        return f"❌ Error getting source information: {str(e)}"


def main():
    """Main entry point for the ArchGuide MCP server."""
    print("Starting ArchGuide MCP Server...", flush=True)
    
    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()