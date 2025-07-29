#!/usr/bin/env python3
"""Test script to demonstrate MCP functionality."""

import asyncio
import json
from src.archguide_mcp_python.storage.store import GuidelineStore
from src.archguide_mcp_python.models.types import (
    ContextFilters, 
    SearchFilters,
    CreateGuidelineRequest
)


async def test_mcp_functionality():
    """Test all MCP functionality."""
    print("🚀 Testing ArchGuide MCP Server Functionality\n")
    
    # Initialize store
    store = GuidelineStore("./guidelines")
    await store.initialize()
    
    print("✅ Store initialized successfully")
    print(f"📚 Loaded {len(store.guidelines)} guidelines\n")
    
    # Test 1: List categories
    print("=== Test 1: List Categories ===")
    categories = store.get_categories()
    print(f"Available categories: {', '.join(categories)}")
    for category in categories:
        count = sum(1 for g in store.guidelines.values() if g.category == category)
        print(f"  - {category}: {count} guidelines")
    print()
    
    # Test 2: Get architecture guideline by topic
    print("=== Test 2: Get Architecture Guideline ===")
    topic = "microservices"
    guidelines = store.get_guidelines_by_topic(topic)
    print(f"Found {len(guidelines)} guidelines for topic '{topic}':")
    for g in guidelines[:2]:  # Show first 2
        print(f"  - {g.title} (v{g.version})")
        print(f"    Tags: {', '.join(g.tags)}")
    print()
    
    # Test 3: Get guideline with context filters
    print("=== Test 3: Get Guideline with Context Filters ===")
    context = ContextFilters(
        tech_stack=["python", "fastapi"],
        scale="startup"
    )
    filtered_guidelines = store.get_guidelines_by_topic("api", context)
    print(f"Found {len(filtered_guidelines)} guidelines for 'api' with context filters:")
    print(f"  Tech stack: {context.tech_stack}")
    print(f"  Scale: {context.scale}")
    for g in filtered_guidelines:
        print(f"  - {g.title}")
    print()
    
    # Test 4: Search patterns
    print("=== Test 4: Search Patterns ===")
    query = "database patterns"
    search_results = store.search_guidelines(query, limit=5)
    print(f"Search results for '{query}':")
    for g in search_results:
        print(f"  - {g.title}")
        print(f"    Category: {g.category}")
        print(f"    Patterns: {', '.join([p.name for p in g.patterns])}")
    print()
    
    # Test 5: Get server stats
    print("=== Test 5: Get Server Stats ===")
    stats = store.get_stats()
    print(f"Server Statistics:")
    print(f"  Total guidelines: {stats['total_guidelines']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Guidelines per category:")
    for cat, count in stats['guidelines_per_category'].items():
        print(f"    - {cat}: {count}")
    print()
    
    # Test 6: Add new guideline
    print("=== Test 6: Add New Guideline ===")
    # Note: In the actual MCP server, guidelines are added through the server API
    # Here we'll demonstrate the structure that would be used
    new_guideline_example = {
        "title": "Test Error Handling Pattern",
        "category": "testing",
        "content": """# Error Handling Pattern

This is a test guideline for demonstrating dynamic guideline creation.

## Pattern: Structured Error Handling

### Description
Implement consistent error handling across services.

### When to use
- In all API endpoints
- For external service calls
- Database operations

### Implementation
Use try-catch blocks with structured error responses.

### Consequences
- Consistent error format
- Better debugging
- Improved user experience
""",
        "tags": ["error-handling", "testing", "demo"],
        "tech_stack": ["python", "fastapi"],
        "applicability": ["startup", "enterprise"],
        "author": "Test Script"
    }
    
    print("Example guideline structure that would be sent to add-guideline tool:")
    print(json.dumps(new_guideline_example, indent=2))
    
    # For testing, we'll use an existing guideline
    guideline_id = list(store.guidelines.keys())[0]
    added_guideline = store.get_guideline_by_id(guideline_id)
    print(f"\n✅ Using existing guideline for update/delete tests: {guideline_id}")
    
    # Verify it was added
    added_guideline = store.get_guideline_by_id(guideline_id)
    if added_guideline:
        print(f"  Title: {added_guideline.title}")
        print(f"  Category: {added_guideline.category}")
        print(f"  Tags: {', '.join(added_guideline.tags)}")
    print()
    
    # Test 7: Update guideline
    print("=== Test 7: Update Guideline ===")
    print("Example update structure that would be sent to update-guideline tool:")
    update_example = {
        "guideline_id": guideline_id,
        "title": "Updated Title Example",
        "tags": ["updated", "example", "test"]
    }
    print(json.dumps(update_example, indent=2))
    print()
    
    # Test 8: Check compliance
    print("=== Test 8: Check Compliance ===")
    design = """
    I'm planning to use a shared database across multiple microservices
    for better data consistency and simpler queries.
    """
    print(f"Design to check: {design.strip()}")
    
    # Find relevant guidelines
    compliance_guidelines = store.search_guidelines("database microservices", limit=3)
    print(f"\nChecking against {len(compliance_guidelines)} relevant guidelines:")
    
    for guideline in compliance_guidelines:
        print(f"\n  Guideline: {guideline.title}")
        
        # Check for anti-patterns
        for anti_pattern in guideline.anti_patterns:
            if "shared database" in anti_pattern.name.lower():
                print(f"  ❌ Violation: {anti_pattern.name}")
                print(f"     Reason: {anti_pattern.why}")
                print(f"     Instead: {anti_pattern.instead}")
        
        # Suggest patterns
        for pattern in guideline.patterns:
            if "database" in pattern.name.lower():
                print(f"  ✅ Recommended: {pattern.name}")
                print(f"     When: {pattern.when}")
    print()
    
    # Test 9: Delete guideline
    print("=== Test 9: Delete Guideline ===")
    print("Example delete request that would be sent to delete-guideline tool:")
    delete_example = {
        "guideline_id": "test-guideline-123"
    }
    print(json.dumps(delete_example, indent=2))
    print()
    
    print("🎉 All MCP functionality tests completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_functionality())