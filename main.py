#!/usr/bin/env python3
"""Main entry point for MCP Optimizer server."""

import logging
import sys

from mcp_optimizer.mcp_server import create_mcp_server


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )


def main() -> None:
    """Main entry point for the MCP server."""
    setup_logging()
    
    try:
        # Create MCP server with all optimization tools
        mcp = create_mcp_server()
        
        # Run the server with stdio transport (default)
        # This is the recommended pattern from FastMCP documentation
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


# Export mcp object for FastMCP CLI compatibility
mcp = create_mcp_server()

if __name__ == "__main__":
    main()
