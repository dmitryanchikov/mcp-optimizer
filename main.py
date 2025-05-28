#!/usr/bin/env python3
"""Main entry point for MCP Optimizer server."""

import asyncio
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


async def run_server_async() -> None:
    """Run server in async context."""
    logger = logging.getLogger(__name__)
    
    try:
        # Create MCP server with all optimization tools
        mcp = create_mcp_server()
        
        logger.info("Starting MCP Optimizer server with stdio transport")
        
        # Run the server asynchronously
        await mcp.run_async()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the MCP server."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we get here, there's already a running loop
            logger.info("Detected running event loop, using async mode")
            # Create a task to run the server
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(run_server_async())
        except RuntimeError:
            # No running loop, we can use the synchronous run method
            logger.info("No running event loop detected, using sync mode")
            mcp = create_mcp_server()
            logger.info("Starting MCP Optimizer server with stdio transport")
            mcp.run()
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
