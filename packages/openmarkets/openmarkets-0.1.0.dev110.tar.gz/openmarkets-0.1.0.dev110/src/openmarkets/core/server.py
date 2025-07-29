"""Open Markets Server"""

import logging

from mcp.server import FastMCP

from openmarkets.core.registry import ToolRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server():
    """Factory function to create and configure the MCP server."""
    logger.info("Initializing ToolRegistry and registering tools...")
    mcp = FastMCP("Open Markets Server", "0.0.1")
    try:
        registry = ToolRegistry()
        registry.register_all_tools(mcp)
        logger.info("Tool registration process completed.")
    except Exception:
        logger.exception("Failed to initialize ToolRegistry or register tools.")
        raise
    return mcp


def main():
    """Main function to start the MCP server."""
    logger.info("Starting Open Markets Server...")
    server = create_server()
    try:
        server.run()
    except Exception:
        logger.exception("Server encountered an error during runtime.")
        raise


if __name__ == "__main__":
    main()
