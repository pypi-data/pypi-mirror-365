"""Content parser for extracting patterns and examples from markdown files."""

import re
from typing import List, Tuple, Optional
from ..models.types import CodeExample, Pattern, AntiPattern


class ContentParser:
    """Parser for extracting structured content from markdown guidelines."""
    
    def parse_content(self, markdown: str) -> Tuple[List[CodeExample], List[Pattern], List[AntiPattern]]:
        """Parse markdown content and extract examples, patterns, and anti-patterns."""
        examples = self._extract_code_examples(markdown)
        patterns = self._extract_patterns(markdown)
        anti_patterns = self._extract_anti_patterns(markdown)
        
        return examples, patterns, anti_patterns
    
    def _extract_code_examples(self, markdown: str) -> List[CodeExample]:
        """Extract code examples from markdown."""
        examples = []
        
        # Pattern to match: ### Example: Title\nDescription\n```language\ncode\n```
        pattern = r'### Example:?\s*([^\n]*)\n([^`]*)\n```(\w+)\n(.*?)```'
        
        matches = re.finditer(pattern, markdown, re.DOTALL | re.MULTILINE)
        
        for match in matches:
            title = match.group(1).strip() or 'Code Example'
            description = match.group(2).strip()
            language = match.group(3)
            code = match.group(4).strip()
            
            examples.append(CodeExample(
                title=title,
                description=description,
                language=language,
                code=code
            ))
        
        return examples
    
    def _extract_patterns(self, markdown: str) -> List[Pattern]:
        """Extract architecture patterns from markdown."""
        patterns = []
        
        # Split the markdown by ## Pattern: and ## Anti-pattern: headers
        # This gives us sections that start with pattern definitions
        sections = re.split(r'\n## (Pattern|Anti-pattern):\s*', markdown)
        
        # Process sections in pairs (type, content)
        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break
                
            section_type = sections[i]  # "Pattern" or "Anti-pattern"
            section_content = sections[i + 1]
            
            # Only process Pattern sections
            if section_type == "Pattern":
                # Extract pattern name (first line) and content
                lines = section_content.split('\n', 1)
                if len(lines) < 2:
                    continue
                    
                name = lines[0].strip()
                content = lines[1] if len(lines) > 1 else ""
                
                description = self._extract_section(content, 'Description') or ''
                when = self._extract_section(content, 'When to use') or ''
                implementation = self._extract_section(content, 'Implementation') or ''
                consequences = self._extract_list(content, 'Consequences')
                
                patterns.append(Pattern(
                    name=name,
                    description=description,
                    when=when,
                    implementation=implementation,
                    consequences=consequences
                ))
        
        return patterns
    
    def _extract_anti_patterns(self, markdown: str) -> List[AntiPattern]:
        """Extract anti-patterns from markdown."""
        anti_patterns = []
        
        # Split the markdown by ## Pattern: and ## Anti-pattern: headers
        # This gives us sections that start with pattern definitions
        sections = re.split(r'\n## (Pattern|Anti-pattern):\s*', markdown)
        
        # Process sections in pairs (type, content)
        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break
                
            section_type = sections[i]  # "Pattern" or "Anti-pattern"
            section_content = sections[i + 1]
            
            # Only process Anti-pattern sections
            if section_type == "Anti-pattern":
                # Extract anti-pattern name (first line) and content
                lines = section_content.split('\n', 1)
                if len(lines) < 2:
                    continue
                    
                name = lines[0].strip()
                content = lines[1] if len(lines) > 1 else ""
                
                description = self._extract_section(content, 'Description') or ''
                why = self._extract_section(content, "Why it's bad") or ''
                instead = self._extract_section(content, 'Instead') or ''
                
                anti_patterns.append(AntiPattern(
                    name=name,
                    description=description,
                    why=why,
                    instead=instead
                ))
        
        return anti_patterns
    
    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a specific section from content."""
        pattern = rf'### {re.escape(section_name)}\s*\n(.*?)(?=\n###|\n##|$)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_list(self, content: str, section_name: str) -> List[str]:
        """Extract a list from a section."""
        section = self._extract_section(content, section_name)
        if not section:
            return []
        
        # Find list items (lines starting with - or *)
        items = re.findall(r'^\s*[-*]\s*(.+)$', section, re.MULTILINE)
        return [item.strip() for item in items]