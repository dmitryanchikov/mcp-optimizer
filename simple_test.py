#!/usr/bin/env python3
"""Simple test for FastMCP without our tools."""

import asyncio
import logging
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)

async def test_simple_server():
    """Test simple FastMCP server."""
    print("Creating simple FastMCP server...")
    mcp = FastMCP("test-server")
    
    @mcp.tool()
    def hello() -> str:
        """Say hello."""
        return "Hello from MCP!"
    
    print("Testing run_async with stdio...")
    try:
        await asyncio.wait_for(mcp.run_async(transport="stdio"), timeout=2.0)
    except asyncio.TimeoutError:
        print("Simple server started successfully (timeout expected)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_server())
