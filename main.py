#!/usr/bin/env python3
"""Main entry point for MCP Optimizer server."""

import logging
import sys

from mcp_optimizer.mcp_server import create_mcp_server


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )


def main() -> None:
    """Main entry point for the MCP server."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Create MCP server with all optimization tools
        mcp = create_mcp_server()

        logger.info("Starting MCP Optimizer server...")
        logger.info("Server created successfully with all optimization tools")

        # Run the server (FastMCP handles asyncio internally)
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
