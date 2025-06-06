#!/usr/bin/env python3
"""Main entry point for MCP Optimizer server."""

import asyncio
import logging
import sys

from mcp_optimizer.config import TransportMode, settings
from mcp_optimizer.mcp_server import create_mcp_server


def setup_logging() -> None:
    """Setup logging configuration."""
    # Use centralized settings instead of direct os.getenv
    log_level = settings.log_level.value

    if settings.log_format.value == "json":
        log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )


async def run_mcp_sse() -> None:
    """Run MCP server with SSE transport."""
    logging.info(f"Starting MCP SSE server on {settings.server_host}:{settings.server_port}")
    mcp = create_mcp_server()

    # FastMCP SSE mode is actually async
    await asyncio.get_event_loop().run_in_executor(
        None, lambda: mcp.run(transport="sse", host=settings.server_host, port=settings.server_port)
    )


def run_mcp_stdio() -> None:
    """Run MCP server with stdio transport."""
    logging.info("Starting MCP stdio server for local MCP clients")
    mcp = create_mcp_server()
    mcp.run(transport="stdio")


async def main() -> None:
    """Main entry point for the MCP server."""
    setup_logging()

    try:
        if settings.transport_mode == TransportMode.SSE:
            # MCP over HTTP SSE - proper MCP protocol via HTTP Server-Sent Events
            await run_mcp_sse()
        else:
            # Default: MCP over stdio - for local MCP clients (Claude Desktop, VS Code, etc.)
            run_mcp_stdio()

    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


# Export mcp object for FastMCP CLI compatibility
mcp = create_mcp_server()

if __name__ == "__main__":
    # Run async main if needed for SSE, otherwise sync for stdio
    if settings.transport_mode == TransportMode.SSE:
        asyncio.run(main())
    else:
        # For stdio mode, run sync
        run_mcp_stdio()
