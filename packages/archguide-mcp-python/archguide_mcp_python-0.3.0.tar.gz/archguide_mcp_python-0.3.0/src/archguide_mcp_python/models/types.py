"""Core data models for the ArchGuide MCP Server."""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class CodeExample(BaseModel):
    """Represents a code example within a guideline."""
    title: str
    description: str
    language: str
    code: str
    explanation: Optional[str] = None


class Pattern(BaseModel):
    """Represents an architecture pattern."""
    name: str
    description: str
    when: str = Field(description="When to use this pattern")
    implementation: str
    consequences: List[str] = Field(default_factory=list)


class AntiPattern(BaseModel):
    """Represents an anti-pattern to avoid."""
    name: str
    description: str
    why: str = Field(description="Why this is bad")
    instead: str = Field(description="What to do instead")


class GuidelineMetadata(BaseModel):
    """Metadata for architecture guidelines."""
    author: str
    reviewers: Optional[List[str]] = None
    created: datetime
    last_updated: datetime
    applicability: List[str] = Field(default_factory=list)
    tech_stack: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    related_guidelines: Optional[List[str]] = None


class ArchitectureGuideline(BaseModel):
    """Main architecture guideline model."""
    id: str
    title: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    content: str
    examples: List[CodeExample] = Field(default_factory=list)
    patterns: List[Pattern] = Field(default_factory=list)
    anti_patterns: List[AntiPattern] = Field(default_factory=list)
    version: str = "1.0.0"
    metadata: GuidelineMetadata

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class SearchFilters(BaseModel):
    """Filters for searching guidelines."""
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    version: Optional[str] = None


class GuidelineRequest(BaseModel):
    """Request model for getting guidelines."""
    topic: str
    context: Optional[dict] = None
    version: Optional[str] = None
    include_examples: bool = True


class SearchRequest(BaseModel):
    """Request model for searching patterns."""
    query: str
    filters: Optional[SearchFilters] = None
    limit: int = 10


class ComplianceRequest(BaseModel):
    """Request model for compliance checking."""
    design: str
    guidelines: Optional[List[str]] = None


class ContextFilters(BaseModel):
    """Context filters for guideline filtering."""
    tech_stack: Optional[List[str]] = None
    scale: Optional[str] = None
    domain: Optional[str] = None

    model_config = ConfigDict(
        use_enum_values=True
    )


class CreateGuidelineRequest(BaseModel):
    """Request model for creating new guidelines dynamically."""
    title: str = Field(description="Title of the guideline")
    category: str = Field(description="Category (e.g., 'microservices', 'security')")
    subcategory: Optional[str] = None
    content: str = Field(description="Main content in markdown format")
    tags: Optional[List[str]] = Field(default_factory=list)
    patterns: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="List of patterns with name, description, etc.")
    anti_patterns: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="List of anti-patterns")
    examples: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Code examples")
    tech_stack: Optional[List[str]] = Field(default_factory=list)
    applicability: Optional[List[str]] = Field(default_factory=list)
    author: str = Field(default="Claude Code User")


class UpdateGuidelineRequest(BaseModel):
    """Request model for updating existing guidelines."""
    guideline_id: str = Field(description="ID of the guideline to update")
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    patterns: Optional[List[Dict[str, str]]] = None
    anti_patterns: Optional[List[Dict[str, str]]] = None
    examples: Optional[List[Dict[str, str]]] = None