"""Main entry point for MCP Optimizer server."""

import argparse
import asyncio
import logging
import sys

import uvicorn

from mcp_optimizer.config import MCPTransport, settings
from mcp_optimizer.mcp_server import create_mcp_server


def setup_logging() -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, settings.log_level.value)

    if settings.log_format.value == "json":
        # For production, use structured JSON logging
        logging.basicConfig(
            level=log_level,
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        # For development, use human-readable format
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


async def run_stdio_server() -> None:
    """Run MCP server with stdio transport."""
    logging.info("Starting MCP Optimizer server with stdio transport")

    mcp_server = create_mcp_server()

    # Run the server with stdio transport using async method
    await mcp_server.run_async(
        transport="stdio",
        capture_exceptions=not settings.debug,
    )


async def run_sse_server() -> None:
    """Run MCP server with SSE transport."""
    logging.info(
        f"Starting MCP Optimizer server with SSE transport on {settings.mcp_host}:{settings.mcp_port}"
    )

    mcp_server = create_mcp_server()

    # Create FastAPI app with SSE transport
    app = mcp_server.sse_app

    # Run with uvicorn
    config = uvicorn.Config(
        app,
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level=settings.log_level.value.lower(),
        reload=settings.reload,
        access_log=settings.debug,
    )

    server = uvicorn.Server(config)
    await server.serve()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP Optimizer Server - Mathematical optimization via MCP protocol"
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=settings.mcp_transport.value,
        help="MCP transport protocol (default: %(default)s)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=settings.mcp_port,
        help="Port for SSE transport (default: %(default)s)",
    )

    parser.add_argument(
        "--host",
        default=settings.mcp_host,
        help="Host for SSE transport (default: %(default)s)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=settings.debug,
        help="Enable debug mode",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.reload,
        help="Enable auto-reload for development",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=settings.log_level.value,
        help="Logging level (default: %(default)s)",
    )

    return parser.parse_args()


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Update settings from command line arguments
    settings.mcp_transport = MCPTransport(args.transport)
    settings.mcp_port = args.port
    settings.mcp_host = args.host
    settings.debug = args.debug
    settings.reload = args.reload
    if isinstance(args.log_level, str):
        from mcp_optimizer.config import LogLevel

        settings.log_level = LogLevel(args.log_level)
    else:
        settings.log_level = args.log_level

    # Setup logging
    setup_logging()

    try:
        if settings.mcp_transport == MCPTransport.STDIO:
            await run_stdio_server()
        else:
            await run_sse_server()
    except KeyboardInterrupt:
        logging.info("Server shutdown requested")
    except Exception as e:
        logging.error(f"Server error: {e}")
        if settings.debug:
            raise
        sys.exit(1)


def cli_main() -> None:
    """CLI entry point for setuptools."""
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we get here, there's already a running loop
            logging.info("Detected running event loop, applying nest_asyncio patch")
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(main())
        except RuntimeError:
            # No running loop, we can use asyncio.run normally
            asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli_main()
