"""Formatting utilities for preparing output for AI consumption."""

from typing import List, Dict, Any
from ..models.types import ArchitectureGuideline


def format_guideline_for_ai(guidelines: List[ArchitectureGuideline], 
                           include_examples: bool = True) -> str:
    """Format guidelines for AI consumption."""
    if not guidelines:
        return "No guidelines found."
    
    formatted_parts = []
    
    for guideline in guidelines:
        parts = [f"# {guideline.title}", "", guideline.content]
        
        # Add metadata
        parts.extend(["", "## Metadata"])
        parts.append(f"- **Category**: {guideline.category}")
        if guideline.subcategory:
            parts[-1] += f" > {guideline.subcategory}"
        parts.append(f"- **Version**: {guideline.version}")
        parts.append(f"- **Tags**: {', '.join(guideline.tags)}")
        parts.append(f"- **Applicable for**: {', '.join(guideline.metadata.applicability)}")
        
        if guideline.metadata.tech_stack:
            parts.append(f"- **Tech Stack**: {', '.join(guideline.metadata.tech_stack)}")
        
        # Add patterns
        if guideline.patterns:
            parts.extend(["", "## Patterns"])
            for pattern in guideline.patterns:
                parts.extend([
                    f"### Pattern: {pattern.name}",
                    f"**Description**: {pattern.description}",
                    f"**When to use**: {pattern.when}",
                    f"**Implementation**: {pattern.implementation}"
                ])
                
                if pattern.consequences:
                    parts.append("**Consequences**:")
                    parts.extend([f"- {consequence}" for consequence in pattern.consequences])
                
                parts.append("")  # Empty line between patterns
        
        # Add anti-patterns
        if guideline.anti_patterns:
            parts.extend(["", "## Anti-patterns to Avoid"])
            for anti_pattern in guideline.anti_patterns:
                parts.extend([
                    f"### ❌ {anti_pattern.name}",
                    f"**Why it's bad**: {anti_pattern.why}",
                    f"**Instead**: {anti_pattern.instead}",
                    ""
                ])
        
        # Add code examples
        if include_examples and guideline.examples:
            parts.extend(["", "## Code Examples"])
            for example in guideline.examples:
                parts.extend([
                    f"### Example: {example.title}",
                    example.description,
                    "",
                    f"```{example.language}",
                    example.code,
                    "```"
                ])
                
                if example.explanation:
                    parts.extend(["", f"**Explanation**: {example.explanation}"])
                
                parts.append("")  # Empty line between examples
        
        # Add related guidelines
        if guideline.metadata.related_guidelines:
            parts.extend(["", "## Related Guidelines"])
            parts.extend([f"- {related}" for related in guideline.metadata.related_guidelines])
        
        formatted_parts.append("\n".join(parts))
    
    return "\n\n---\n\n".join(formatted_parts)


def format_search_results(guidelines: List[ArchitectureGuideline]) -> str:
    """Format search results for AI consumption."""
    if not guidelines:
        return "No search results found."
    
    parts = [f"# Search Results ({len(guidelines)} found)", ""]
    
    for i, guideline in enumerate(guidelines, 1):
        # Get first line of content as summary
        content_lines = guideline.content.split('\n')
        summary = next((line.strip() for line in content_lines if line.strip()), "")
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        pattern_names = [p.name for p in guideline.patterns]
        
        parts.extend([
            f"## {i}. {guideline.title}",
            f"- **Category**: {guideline.category}",
            f"- **Tags**: {', '.join(guideline.tags)}",
            f"- **Summary**: {summary}",
            f"- **Patterns**: {', '.join(pattern_names) if pattern_names else 'None'}",
            ""
        ])
    
    parts.append("Use `get-architecture-guideline` with the specific topic to see full details.")
    
    return "\n".join(parts)


def format_compliance_report(guidelines: List[ArchitectureGuideline], 
                           design: str) -> str:
    """Format compliance check report."""
    if not guidelines:
        return "No guidelines provided for compliance check."
    
    parts = ["## Architecture Compliance Report", ""]
    
    for guideline in guidelines:
        parts.append(f"### {guideline.title}")
        
        # Find compliant patterns (simple keyword matching)
        compliant_patterns = []
        for pattern in guideline.patterns:
            if pattern.name.lower() in design.lower():
                compliant_patterns.append(pattern.name)
        
        # Find violations (anti-patterns)
        violations = []
        for anti_pattern in guideline.anti_patterns:
            if anti_pattern.name.lower() in design.lower():
                violations.append({
                    'pattern': anti_pattern.name,
                    'reason': anti_pattern.why,
                    'suggestion': anti_pattern.instead
                })
        
        # Format compliant patterns
        parts.append("**Compliant Patterns Found:**")
        if compliant_patterns:
            parts.extend([f"- ✅ {pattern}" for pattern in compliant_patterns])
        else:
            parts.append("- None detected")
        
        # Format violations
        parts.extend(["", "**Potential Violations:**"])
        if violations:
            for violation in violations:
                parts.extend([
                    f"- ❌ {violation['pattern']}",
                    f"  - Reason: {violation['reason']}",
                    f"  - Suggestion: {violation['suggestion']}"
                ])
        else:
            parts.append("- None detected")
        
        parts.append("")  # Empty line between guidelines
    
    return "\n".join(parts)


def format_categories(categories: List[str]) -> str:
    """Format available categories list."""
    if not categories:
        return "No categories available."
    
    parts = ["Available architecture guideline categories:", ""]
    parts.extend([f"- {category}" for category in sorted(categories)])
    
    return "\n".join(parts)