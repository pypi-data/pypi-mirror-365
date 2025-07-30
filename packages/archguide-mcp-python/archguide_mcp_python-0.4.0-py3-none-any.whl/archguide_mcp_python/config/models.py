"""Configuration models for multi-source guideline management."""

import os
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
import yaml


class SourceType(str, Enum):
    """Types of guideline sources."""
    GIT = "git"
    PACKAGE = "package"
    API = "api"
    LOCAL = "local"


class AuthType(str, Enum):
    """Authentication types for sources."""
    NONE = "none"
    TOKEN = "token"
    BASIC = "basic"
    SSH = "ssh"
    OAUTH = "oauth"


class MergeStrategy(str, Enum):
    """Strategies for merging guidelines from multiple sources."""
    OVERRIDE = "override"  # Higher priority completely replaces lower
    COMBINE = "combine"    # All guidelines available, conflicts favor higher priority
    LAYERED = "layered"    # Guidelines inherit and extend from lower layers


class AuthConfig(BaseModel):
    """Authentication configuration for a source."""
    type: AuthType = AuthType.NONE
    token: Optional[str] = None
    token_env: Optional[str] = None  # Environment variable containing token
    username: Optional[str] = None
    password: Optional[str] = None
    password_env: Optional[str] = None
    ssh_key_path: Optional[str] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_token_url: Optional[str] = None

    @validator('token', always=True)
    def resolve_token(cls, v, values):
        """Resolve token from environment if specified."""
        if not v and values.get('token_env'):
            return os.getenv(values['token_env'])
        return v

    @validator('password', always=True)
    def resolve_password(cls, v, values):
        """Resolve password from environment if specified."""
        if not v and values.get('password_env'):
            return os.getenv(values['password_env'])
        return v


class GuidelineSourceConfig(BaseModel):
    """Configuration for a single guideline source."""
    name: str = Field(description="Name of the source for identification")
    type: SourceType
    url: Optional[str] = Field(None, description="URL for git/api/package sources")
    path: Optional[str] = Field(None, description="Path for local sources")
    branch: Optional[str] = Field("main", description="Git branch to use")
    tag: Optional[str] = Field(None, description="Git tag to use (overrides branch)")
    package_version: Optional[str] = Field(None, description="Package version to use")
    auth: Optional[AuthConfig] = None
    priority: int = Field(1, ge=1, le=100, description="Priority (1=lowest, 100=highest)")
    cache_ttl: Optional[int] = Field(3600, description="Cache TTL in seconds")
    enabled: bool = Field(True, description="Whether this source is enabled")
    
    # Filtering options
    include_categories: Optional[List[str]] = Field(None, description="Only include these categories")
    exclude_categories: Optional[List[str]] = Field(None, description="Exclude these categories")
    include_tags: Optional[List[str]] = Field(None, description="Only include guidelines with these tags")
    exclude_tags: Optional[List[str]] = Field(None, description="Exclude guidelines with these tags")

    @validator('url')
    def validate_url(cls, v, values):
        """Validate URL is provided for non-local sources."""
        if values.get('type') != SourceType.LOCAL and not v:
            raise ValueError(f"URL is required for source type {values.get('type')}")
        return v

    @validator('path')
    def validate_path(cls, v, values):
        """Validate path is provided for local sources."""
        if values.get('type') == SourceType.LOCAL and not v:
            raise ValueError("Path is required for local sources")
        return v


class CacheConfig(BaseModel):
    """Cache configuration."""
    type: Literal["memory", "redis", "file"] = "memory"
    ttl: int = Field(3600, description="Default TTL in seconds")
    max_size: Optional[int] = Field(1000, description="Max items in cache")
    redis_url: Optional[str] = None
    file_path: Optional[str] = Field(".archguide_cache", description="Path for file-based cache")


class ArchGuideConfig(BaseModel):
    """Main configuration for ArchGuide MCP Server."""
    sources: List[GuidelineSourceConfig] = Field(default_factory=list)
    merge_strategy: MergeStrategy = MergeStrategy.LAYERED
    cache: CacheConfig = Field(default_factory=CacheConfig)
    offline_mode: bool = Field(False, description="Work offline with cached data")
    auto_sync: bool = Field(True, description="Automatically sync sources on startup")
    sync_interval: Optional[int] = Field(None, description="Auto-sync interval in seconds")
    
    # Global filtering
    mandatory_guidelines: List[str] = Field(default_factory=list, description="Guidelines that cannot be overridden")
    blocked_guidelines: List[str] = Field(default_factory=list, description="Guidelines to always exclude")
    
    # Performance
    parallel_fetch: bool = Field(True, description="Fetch from sources in parallel")
    max_workers: int = Field(4, description="Max parallel workers")
    
    @validator('sources')
    def validate_unique_names(cls, v):
        """Ensure source names are unique."""
        names = [s.name for s in v]
        if len(names) != len(set(names)):
            raise ValueError("Source names must be unique")
        return v

    def get_sources_by_priority(self) -> List[GuidelineSourceConfig]:
        """Get sources sorted by priority (highest first)."""
        return sorted(self.sources, key=lambda s: s.priority, reverse=True)


def load_config(config_path: Optional[str] = None) -> ArchGuideConfig:
    """Load configuration from file or environment."""
    # Priority order:
    # 1. Specified config_path
    # 2. ARCHGUIDE_CONFIG environment variable
    # 3. .archguide.yaml in current directory
    # 4. archguide.yaml in current directory
    # 5. ~/.archguide/config.yaml
    # 6. Default configuration
    
    config_paths = []
    
    if config_path:
        config_paths.append(config_path)
    
    if env_config := os.getenv("ARCHGUIDE_CONFIG"):
        config_paths.append(env_config)
    
    config_paths.extend([
        ".archguide.yaml",
        "archguide.yaml",
        os.path.expanduser("~/.archguide/config.yaml")
    ])
    
    for path in config_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return ArchGuideConfig(**data)
    
    # Return default configuration
    return get_default_config()


def get_default_config() -> ArchGuideConfig:
    """Get default configuration."""
    return ArchGuideConfig(
        sources=[
            GuidelineSourceConfig(
                name="local",
                type=SourceType.LOCAL,
                path="./guidelines",
                priority=2
            ),
            GuidelineSourceConfig(
                name="bundled",
                type=SourceType.LOCAL,
                path=str(Path(__file__).parent.parent / "guidelines"),
                priority=1,
                enabled=True
            )
        ],
        merge_strategy=MergeStrategy.LAYERED
    )


def save_config(config: ArchGuideConfig, path: str = ".archguide.yaml"):
    """Save configuration to file."""
    with open(path, 'w') as f:
        yaml.dump(config.model_dump(exclude_none=True), f, default_flow_style=False)