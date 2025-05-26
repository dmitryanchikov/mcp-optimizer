#!/usr/bin/env python3
"""Debug script to check tools structure."""

import asyncio

from mcp_optimizer.mcp_server import create_mcp_server


async def debug_tools():
    """Debug tools structure."""
    server = create_mcp_server()
    tools = await server.get_tools()

    print(f"Tools type: {type(tools)}")
    print(f"Tools length: {len(tools)}")

    for i, tool in enumerate(tools):
        print(f"Tool {i}: {type(tool)} = {tool}")
        if hasattr(tool, "__dict__"):
            print(f"  Attributes: {tool.__dict__}")
        print()


if __name__ == "__main__":
    asyncio.run(debug_tools())
