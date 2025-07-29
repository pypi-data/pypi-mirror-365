"""Tests for the content parser."""

import pytest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from archguide_mcp_python.parsers.content import ContentParser


class TestContentParser:
    """Test cases for ContentParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ContentParser()
    
    def test_extract_code_examples(self):
        """Test extraction of code examples from markdown."""
        markdown = """
# Test Guideline

Some content here.

### Example: Simple Python Function
This example shows a basic function.

```python
def hello_world():
    return "Hello, World!"
```

### Example: Another Example
This shows something else.

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
```
"""
        
        examples, _, _ = self.parser.parse_content(markdown)
        
        assert len(examples) == 2
        
        # Test first example
        assert examples[0].title == "Simple Python Function"
        assert examples[0].description == "This example shows a basic function."
        assert examples[0].language == "python"
        assert 'def hello_world():' in examples[0].code
        
        # Test second example
        assert examples[1].title == "Another Example"
        assert examples[1].language == "javascript"
        assert 'function greet(name)' in examples[1].code
    
    def test_extract_patterns(self):
        """Test extraction of patterns from markdown."""
        markdown = """
# Test Guideline

## Pattern: Database per Service

### Description
Each service owns its database.

### When to use
- When you need service autonomy
- For microservices architecture

### Implementation
Use separate databases for each service.

### Consequences
- Service independence
- Data consistency challenges

## Pattern: Event Sourcing

### Description
Store events instead of state.

### When to use
- When you need audit trail

### Implementation
Store all changes as events.

### Consequences
- Complete history
- Complex queries
"""
        
        _, patterns, _ = self.parser.parse_content(markdown)
        
        assert len(patterns) == 2
        
        # Test first pattern
        assert patterns[0].name == "Database per Service"
        assert patterns[0].description == "Each service owns its database."
        assert patterns[0].when == "- When you need service autonomy\n- For microservices architecture"
        assert patterns[0].implementation == "Use separate databases for each service."
        assert len(patterns[0].consequences) == 2
        assert "Service independence" in patterns[0].consequences
        
        # Test second pattern
        assert patterns[1].name == "Event Sourcing"
        assert patterns[1].description == "Store events instead of state."
    
    def test_extract_anti_patterns(self):
        """Test extraction of anti-patterns from markdown."""
        markdown = """
# Test Guideline

## Anti-pattern: Shared Database

### Description
Multiple services sharing the same database.

### Why it's bad
Creates tight coupling between services.

### Instead
Use separate databases for each service.

## Anti-pattern: God Object

### Description
A single class that does too much.

### Why it's bad
Hard to maintain and test.

### Instead
Break into smaller, focused classes.
"""
        
        _, _, anti_patterns = self.parser.parse_content(markdown)
        
        assert len(anti_patterns) == 2
        
        # Test first anti-pattern
        assert anti_patterns[0].name == "Shared Database"
        assert anti_patterns[0].description == "Multiple services sharing the same database."
        assert anti_patterns[0].why == "Creates tight coupling between services."
        assert anti_patterns[0].instead == "Use separate databases for each service."
        
        # Test second anti-pattern
        assert anti_patterns[1].name == "God Object"
        assert "A single class" in anti_patterns[1].description
    
    def test_extract_empty_content(self):
        """Test parsing empty or minimal content."""
        markdown = "# Simple Guideline\n\nJust some basic content."
        
        examples, patterns, anti_patterns = self.parser.parse_content(markdown)
        
        assert len(examples) == 0
        assert len(patterns) == 0
        assert len(anti_patterns) == 0
    
    def test_extract_section_not_found(self):
        """Test section extraction when section doesn't exist."""
        content = "Some content without the requested section."
        
        result = self.parser._extract_section(content, "Nonexistent Section")
        assert result is None
    
    def test_extract_list_items(self):
        """Test extraction of list items from content."""
        content = """
Some text here.

### Consequences
- First consequence
- Second consequence
* Third consequence with asterisk
- Fourth consequence

More text.
"""
        
        items = self.parser._extract_list(content, "Consequences")
        
        assert len(items) == 4
        assert "First consequence" in items
        assert "Second consequence" in items
        assert "Third consequence with asterisk" in items
        assert "Fourth consequence" in items