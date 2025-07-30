"""Source provider registry and factory."""

from typing import Dict, Type, Optional

from .base import SourceProvider
from .local import LocalSourceProvider
from .git import GitSourceProvider
from ..config.models import GuidelineSourceConfig, SourceType


class SourceRegistry:
    """Registry for source provider types."""
    
    _providers: Dict[SourceType, Type[SourceProvider]] = {
        SourceType.LOCAL: LocalSourceProvider,
        SourceType.GIT: GitSourceProvider,
        # SourceType.PACKAGE: PackageSourceProvider,  # TODO: Implement
        # SourceType.API: ApiSourceProvider,  # TODO: Implement
    }
    
    @classmethod
    def register_provider(cls, source_type: SourceType, provider_class: Type[SourceProvider]):
        """Register a new source provider type.
        
        Args:
            source_type: The source type identifier
            provider_class: The provider class to register
        """
        cls._providers[source_type] = provider_class
    
    @classmethod
    def create_provider(cls, config: GuidelineSourceConfig) -> SourceProvider:
        """Create a source provider from configuration.
        
        Args:
            config: Source configuration
            
        Returns:
            Configured source provider instance
            
        Raises:
            ValueError: If source type is not supported
        """
        if config.type not in cls._providers:
            raise ValueError(f"Unsupported source type: {config.type}")
        
        provider_class = cls._providers[config.type]
        return provider_class(config)
    
    @classmethod
    def get_supported_types(cls) -> list[SourceType]:
        """Get list of supported source types."""
        return list(cls._providers.keys())
    
    @classmethod
    def is_supported(cls, source_type: SourceType) -> bool:
        """Check if a source type is supported."""
        return source_type in cls._providers