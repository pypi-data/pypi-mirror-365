"""ArchGuide MCP Server - Architecture Guidelines for AI Workflows."""

__version__ = "0.4.0"
__author__ = "Ioan Salau"
__description__ = "Architecture Guidelines MCP Server - Inject architectural best practices into AI workflows"

def main():
    """Main entry point for the ArchGuide MCP server."""
    from .server import main as server_main
    return server_main()

# Export main function for CLI entry point
__all__ = ["main"]
