# ArchGuide MCP Server - Comprehensive User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Core Concepts](#core-concepts)
6. [MCP Tools Reference](#mcp-tools-reference)
7. [Dynamic Guideline Management](#dynamic-guideline-management)
8. [Writing Guidelines](#writing-guidelines)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)
12. [Examples & Workflows](#examples--workflows)

---

## Introduction

The ArchGuide MCP Server is a Model Context Protocol (MCP) server that provides architecture guidelines, design patterns, and best practices directly within your AI development workflows. Built with Python, FastMCP, and modern tooling, it enables you to access and create architectural knowledge seamlessly during development.

### Key Features

- **Instant Access**: Get architecture guidelines without leaving your development environment
- **Smart Search**: Full-text search across all patterns and guidelines
- **Dynamic Creation**: Add new guidelines on-the-fly during development
- **Context-Aware**: Filter guidelines by tech stack, scale, and domain
- **Living Documentation**: Guidelines that evolve with your team's knowledge

### What You Can Do

- Retrieve architecture patterns for specific technologies
- Search for best practices and solutions
- Create team-specific guidelines during development
- Validate designs against architectural standards
- Build a knowledge base that grows with your projects

---

## Quick Start

### 1. Install and Setup
```bash
# Clone the repository
git clone <repository-url>
cd archguide-mcp-python

# Install with uv
uv sync

# Test the installation
uv run pytest
```

### 2. Add to Claude Code
Add to your Claude Code configuration (`~/.claude/config.json`):

```json
{
  "mcpServers": {
    "archguide": {
      "command": "uv",
      "args": ["run", "archguide-mcp"],
      "cwd": "/path/to/archguide-mcp-python"
    }
  }
}
```

### 3. Start Using
In Claude Code, you can now:

```
Show me microservices patterns for Python FastAPI applications

Add a new guideline about our team's error handling conventions

Search for security patterns related to JWT authentication
```

---

## Installation & Setup

### Prerequisites

- **Python 3.12+**: Modern Python version
- **uv**: Fast Python package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Claude Code**: AI development environment with MCP support

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/archguide-mcp-python.git
cd archguide-mcp-python
```

#### 2. Install Dependencies
```bash
# Install all dependencies
uv sync

# Install with development dependencies
uv sync --dev
```

#### 3. Verify Installation
```bash
# Run tests to verify everything works
uv run pytest

# Check server can start
uv run archguide-mcp --help
```

#### 4. Configure Claude Code

Create or edit `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "archguide": {
      "command": "uv",
      "args": ["run", "archguide-mcp"],
      "cwd": "/absolute/path/to/archguide-mcp-python",
      "env": {
        "GUIDELINES_PATH": "/path/to/your/guidelines"
      }
    }
  }
}
```

#### 5. Restart Claude Code
Restart Claude Code to load the new MCP server.

---

## Configuration

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `GUIDELINES_PATH` | Path to guidelines directory | `./guidelines` | `/home/user/my-guidelines` |
| `INDEX_DIR` | Search index directory | Auto-generated | `/tmp/search_index` |
| `CACHE_TTL` | Cache time-to-live (seconds) | `300` | `600` |

### Guidelines Directory Structure

```
guidelines/
├── microservices/
│   ├── data-management.md
│   ├── communication-patterns.md
│   └── service-discovery.md
├── cloud-native/
│   ├── api-design.md
│   ├── containerization.md
│   └── observability.md
├── security/
│   ├── authentication.md
│   ├── authorization.md
│   └── data-protection.md
└── performance/
    ├── caching-strategies.md
    ├── database-optimization.md
    └── scaling-patterns.md
```

### Custom Configuration

Create a `.env` file in the project root:

```env
GUIDELINES_PATH=/path/to/your/guidelines
CACHE_TTL=600
INDEX_DIR=/custom/search/index
```

---

## Core Concepts

### Guidelines

**Architecture Guidelines** are structured documents containing:
- **Patterns**: Recommended approaches with implementation details
- **Anti-patterns**: Approaches to avoid with explanations
- **Examples**: Code samples and implementations
- **Metadata**: Author, tech stack, applicability, etc.

### Categories

Guidelines are organized into categories:
- **microservices**: Service-oriented architecture patterns
- **cloud-native**: Cloud deployment and scaling patterns
- **security**: Authentication, authorization, and protection patterns
- **performance**: Optimization and scaling strategies
- **data-patterns**: Database design and data management

### Context Filtering

Filter guidelines by:
- **Tech Stack**: `["python", "fastapi", "postgresql"]`
- **Scale**: `"startup"`, `"growth"`, `"enterprise"`
- **Domain**: `"e-commerce"`, `"fintech"`, `"healthcare"`

### Search Capabilities

Full-text search across:
- Guideline titles and content
- Pattern names and descriptions
- Code examples and implementations
- Tags and metadata

---

## MCP Tools Reference

### Core Retrieval Tools

#### `get-architecture-guideline`

Fetch guidelines for specific topics with context filtering.

**Parameters:**
- `topic` (string, required): Architecture topic
- `context` (object, optional): Filtering context
  - `tech_stack` (array): Technology stack
  - `scale` (string): System scale
  - `domain` (string): Business domain
- `version` (string, optional): Guideline version
- `include_examples` (boolean, optional): Include code examples (default: true)

**Example:**
```json
{
  "topic": "microservices",
  "context": {
    "tech_stack": ["python", "fastapi"],
    "scale": "startup",
    "domain": "e-commerce"
  },
  "include_examples": true
}
```

#### `search-patterns`

Search for patterns and best practices.

**Parameters:**
- `query` (string, required): Search query
- `filters` (object, optional): Search filters
  - `category` (string): Filter by category
  - `tags` (array): Filter by tags
  - `tech_stack` (array): Filter by technology
- `limit` (number, optional): Maximum results (default: 10)

**Example:**
```json
{
  "query": "database transaction patterns",
  "filters": {
    "category": "microservices",
    "tech_stack": ["python", "postgresql"]
  },
  "limit": 5
}
```

#### `list-categories`

Get all available guideline categories.

**Parameters:** None

**Returns:** List of available categories with counts.

#### `check-compliance`

Validate designs against architectural guidelines.

**Parameters:**
- `design` (string, required): Design description or code
- `guidelines` (array, optional): Specific guideline IDs

**Example:**
```json
{
  "design": "I'm planning to use shared database across microservices",
  "guidelines": ["microservices-data-management"]
}
```

#### `get-server-stats`

Get server statistics and health information.

**Returns:** Server stats including guideline counts, categories, and cache status.

---

## Dynamic Guideline Management

### Creating Guidelines On-the-Fly

#### `add-guideline`

Create new guidelines during development.

**Parameters:**
- `title` (string, required): Guideline title
- `category` (string, required): Category name
- `content` (string, required): Markdown content
- `subcategory` (string, optional): Subcategory
- `tags` (array, optional): Tags for categorization
- `patterns` (array, optional): Pattern definitions
- `anti_patterns` (array, optional): Anti-pattern definitions
- `examples` (array, optional): Code examples
- `tech_stack` (array, optional): Technology stack
- `applicability` (array, optional): Applicable contexts
- `author` (string, optional): Author name

**Pattern Object Structure:**
```json
{
  "name": "Pattern Name",
  "description": "What this pattern does",
  "when": "When to use this pattern",
  "implementation": "How to implement",
  "consequences": "Pros and cons separated by newlines"
}
```

**Example Object Structure:**
```json
{
  "title": "Example Title",
  "description": "What this example demonstrates",
  "language": "python",
  "code": "def example():\n    return 'Hello, World!'"
}
```

### Updating Existing Guidelines

#### `update-guideline`

Modify existing guidelines with partial updates.

**Parameters:**
- `guideline_id` (string, required): ID of guideline to update
- `title` (string, optional): New title
- `content` (string, optional): New content
- `tags` (array, optional): New tags
- `patterns` (array, optional): New patterns (replaces existing)
- `anti_patterns` (array, optional): New anti-patterns (replaces existing)
- `examples` (array, optional): New examples (replaces existing)

### Managing Guidelines

#### `delete-guideline`

Remove guidelines from the system.

**Parameters:**
- `guideline_id` (string, required): ID of guideline to delete

#### `reload-guidelines`

Refresh guidelines from filesystem.

**Use Cases:**
- After manual edits to .md files
- When teammates add new guidelines
- To pick up external changes

---

## Writing Guidelines

### Guideline Format

Guidelines use Markdown with YAML frontmatter:

```markdown
---
id: unique-guideline-id
title: Guideline Title
category: main-category
subcategory: sub-category
tags: [tag1, tag2, tag3]
version: 1.0.0
author: Author Name
created: 2024-01-01
lastUpdated: 2024-01-02
applicability: [startup, enterprise, cloud-native]
techStack: [python, fastapi, postgresql]
prerequisites: [http-basics, api-design]
relatedGuidelines: [other-guideline-id]
---

# Guideline Content

Your guideline content here using standard Markdown.

## Pattern: Pattern Name

### Description
Pattern description explaining what it does.

### When to use
- Condition 1
- Condition 2
- Specific scenarios

### Implementation
Step-by-step implementation details.

### Consequences
- **Pros**: Benefits of using this pattern
- **Cons**: Potential drawbacks or limitations

## Anti-pattern: Anti-pattern Name

### Description
Description of the problematic approach.

### Why it's bad
Explanation of why this approach is problematic.

### Instead
What to do instead of this anti-pattern.

## Example: Code Example

Description of the example.

```python
def example_function():
    """This is an example function."""
    return "Hello, World!"
```
```

### Content Structure Best Practices

#### 1. Clear Hierarchy
```markdown
# Main Topic
## Pattern: Specific Pattern
### Implementation Details
#### Code Examples
```

#### 2. Actionable Content
- Use imperative language ("Use X when Y")
- Provide concrete examples
- Include implementation steps
- Explain trade-offs

#### 3. Rich Metadata
```yaml
---
# Essential metadata
id: database-per-service-pattern
title: Database per Service Pattern
category: microservices
tags: [database, isolation, scalability]

# Context metadata
techStack: [postgresql, mongodb, redis]
applicability: [startup, enterprise]
prerequisites: [microservices-basics]

# Maintenance metadata
author: Team Lead
version: 2.1.0
created: 2024-01-15
lastUpdated: 2024-03-20
---
```

---

## Best Practices

### Guideline Creation

#### 1. Start Simple
```
Add a basic guideline about error handling in our Python services
```

#### 2. Iterate and Improve
```
Update the error-handling guideline to include the new structured logging pattern we adopted
```

#### 3. Include Real Examples
```python
# Good: Real, working code
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )
```

#### 4. Document Context
```markdown
### When to use
- In FastAPI applications with Pydantic validation
- When you need structured error responses
- For APIs consumed by frontend applications
```

### Team Workflow

#### 1. Collaborative Creation
```
# During code review
"This error handling pattern we just implemented should be documented"
→ Add guideline about structured error responses

# During architecture discussions  
"Let's document this distributed caching strategy"
→ Create guideline with implementation details
```

#### 2. Knowledge Sharing
```
# Team member discovers pattern
Add a guideline about the database connection pooling strategy from the performance optimization ticket

# After incident resolution
Document the circuit breaker pattern we implemented to prevent cascade failures
```

#### 3. Living Documentation
```
# Regular updates
Update the authentication guideline to include the new JWT refresh token strategy

# Deprecation
Delete the legacy-auth-guid-123 guideline as we've migrated to OAuth2
```

---

## Troubleshooting

### Common Issues

#### 1. Server Not Starting

**Symptoms:**
- Claude Code can't connect to ArchGuide
- "Server not available" errors

**Solutions:**
```bash
# Check server can start
uv run archguide-mcp

# Verify dependencies
uv sync

# Check Python version
python --version  # Should be 3.12+
```

#### 2. Guidelines Not Loading

**Symptoms:**
- Empty search results
- "No guidelines found" messages

**Solutions:**
```bash
# Check guidelines directory
ls -la guidelines/

# Verify environment variable
echo $GUIDELINES_PATH

# Reload guidelines
# In Claude Code: "Reload guidelines from filesystem"
```

#### 3. Search Not Working

**Symptoms:**
- Search returns no results
- Search index errors

**Solutions:**
```bash
# Clear search index
rm -rf .search_index/

# Restart server to rebuild index
# Guidelines will be re-indexed automatically
```

#### 4. Permission Errors

**Symptoms:**
- Can't save new guidelines
- File system errors

**Solutions:**
```bash
# Check directory permissions
ls -la guidelines/

# Fix permissions
chmod -R 755 guidelines/

# Check disk space
df -h
```

### Debugging

#### Enable Debug Logging

Set environment variable:
```bash
export ARCHGUIDE_DEBUG=1
```

#### Verbose Output

Run server with verbose logging:
```bash
uv run archguide-mcp --verbose
```

#### Test Individual Components

```bash
# Test content parser
uv run python -c "
from src.archguide_mcp_python.parsers.content import ContentParser
parser = ContentParser()
# Test parsing...
"

# Test search index
uv run python -c "
from src.archguide_mcp_python.storage.search import SearchIndex
index = SearchIndex()
# Test search...
"
```

---

## Advanced Usage

### Custom Categories

Create new categories by adding directories:

```bash
mkdir guidelines/devops
mkdir guidelines/frontend
mkdir guidelines/mobile
```

Then add guidelines in these categories:
```
Add a guideline about Kubernetes deployment patterns in the devops category
```

### Guideline Templates

Create template guidelines for consistency:

```markdown
---
id: template-pattern-guid
title: "[TEMPLATE] Pattern Name"
category: templates
tags: [template]
---

# Pattern Name

## Overview
Brief description of what this pattern solves.

## Pattern: Main Pattern

### Description
Detailed description of the pattern.

### When to use
- Condition 1
- Condition 2

### Implementation
Step-by-step implementation.

### Consequences
- **Pros**: Benefits
- **Cons**: Drawbacks

## Example: Implementation Example

```language
// Code example here
```

## Related Patterns
- [Related Pattern 1](link)
- [Related Pattern 2](link)
```

### Batch Operations

Create multiple related guidelines:

```
Add three related guidelines about microservices communication: 
1. Synchronous communication patterns with REST and gRPC
2. Asynchronous messaging with event-driven architecture  
3. Hybrid communication strategies for different use cases
```

### Integration with External Systems

#### Export Guidelines

```bash
# Export to JSON
uv run python -c "
from src.archguide_mcp_python.storage.store import GuidelineStore
store = GuidelineStore()
# Export logic...
"
```

#### Import from External Sources

```bash
# Import from existing documentation
uv run python scripts/import_guidelines.py --source /path/to/docs
```

### Performance Optimization

#### 1. Index Tuning

Monitor search performance:
```
Get server stats to see search index performance
```

#### 2. Cache Configuration

Adjust cache settings:
```bash
export CACHE_TTL=3600  # 1 hour cache
```

#### 3. Guideline Organization

- Keep guidelines focused and atomic
- Use clear, searchable titles
- Include relevant tags
- Maintain reasonable file sizes

---

## Examples & Workflows

### Workflow 1: API Design Session

**Scenario:** Designing a new REST API for an e-commerce platform.

```
# Get existing patterns
Get architecture guidelines for API design with context for e-commerce and Python FastAPI

# Find specific patterns
Search for REST API versioning patterns and pagination strategies

# Document new pattern discovered during design
Add a guideline about our API error response standardization pattern with examples showing error codes, messages, and correlation IDs for e-commerce APIs

# Validate approach
Check compliance of our new API design against existing REST guidelines
```

### Workflow 2: Microservices Refactoring

**Scenario:** Breaking down a monolith into microservices.

```
# Research decomposition strategies
Search for microservices decomposition patterns and bounded context identification

# Get data management guidance  
Get architecture guidelines for microservices data management with context for enterprise scale and PostgreSQL

# Document lessons learned
Add a guideline about database migration strategies during monolith decomposition with anti-patterns about shared databases and examples of the Strangler Fig pattern

# Update existing guidelines
Update the microservices-communication guideline to include our experience with event sourcing and CQRS patterns
```

### Workflow 3: Security Review

**Scenario:** Implementing authentication for a new service.

```
# Find security patterns
Search for JWT authentication patterns and OAuth2 implementation strategies

# Get comprehensive security guidance
Get architecture guidelines for security with context for fintech domain and enterprise scale

# Document security decisions
Add a guideline about our multi-factor authentication implementation with examples of TOTP integration and anti-patterns about security question fallbacks

# Compliance check
Check compliance of our authentication flow against security guidelines and industry standards
```

### Workflow 4: Performance Optimization

**Scenario:** Optimizing a slow database-heavy application.

```
# Research performance patterns
Search for database optimization patterns and caching strategies for high-traffic applications

# Get performance guidelines
Get architecture guidelines for performance with context for Python FastAPI and PostgreSQL at enterprise scale

# Document optimization technique
Add a guideline about connection pooling and query optimization strategies with examples showing pgBouncer configuration and N+1 query solutions

# Share with team
Add a guideline about our Redis caching layer implementation with patterns for cache invalidation and examples of cache-aside and write-through strategies
```

### Workflow 5: Team Onboarding

**Scenario:** New team member needs to understand architecture decisions.

```
# Overview of guidelines
List all available guideline categories to understand our architectural landscape

# Specific technology guidance
Get architecture guidelines for microservices with context for our Python and Kubernetes tech stack

# Search for specific patterns
Search for service discovery patterns and inter-service communication strategies we use

# Get current stats
Get server statistics to see what architectural knowledge is available
```

### Workflow 6: Code Review Integration

**Scenario:** Using guidelines during code reviews.

```
# During code review, question about pattern usage
Search for singleton pattern implementation and why it might be considered an anti-pattern in microservices

# Reviewer suggests documentation
Add a guideline about the dependency injection pattern we're using consistently across services with examples of FastAPI Depends usage

# Follow-up on review feedback
Update the error-handling guideline to include the structured logging approach the team agreed on during the review
```

### Workflow 7: Architecture Decision Records (ADR)

**Scenario:** Documenting architectural decisions as guidelines.

```
# Document decision
Add a guideline about our decision to use event-driven architecture for order processing with patterns for event sourcing and anti-patterns for synchronous processing across service boundaries

# Link related decisions
Update the microservices-data-management guideline to reference our event sourcing decision and include examples of event store implementation

# Historical context
Add a guideline documenting why we moved away from shared databases in microservices with anti-patterns showing the problems we experienced and patterns for data synchronization
```

---

## Conclusion

The ArchGuide MCP Server transforms architectural knowledge from static documentation into a living, searchable, and continuously evolving resource. By integrating directly with your development workflow through Claude Code, it ensures that architectural wisdom is always at your fingertips.

### Key Benefits

- **Immediate Access**: No context switching to find architectural guidance
- **Living Documentation**: Guidelines that grow with your team's experience  
- **Team Knowledge Sharing**: Capture and share architectural insights in real-time
- **Consistency**: Ensure architectural decisions align with established patterns
- **Searchable Wisdom**: Find relevant patterns quickly through intelligent search

### Getting Started

1. Install and configure the server
2. Start with existing sample guidelines
3. Begin creating team-specific guidelines during development
4. Build a comprehensive knowledge base over time

### Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: This guide and README.md
- **Examples**: Sample guidelines included with the server

---

*Built with ❤️ using FastMCP, Pydantic, and modern Python tooling.*