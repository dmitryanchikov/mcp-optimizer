#!/usr/bin/env python3
"""Minimal test for FastMCP."""

import asyncio
import logging
from mcp_optimizer.mcp_server import create_mcp_server

logging.basicConfig(level=logging.INFO)

async def test_server():
    """Test server creation and startup."""
    print("Creating MCP server...")
    mcp = create_mcp_server()
    
    print("Testing run_async with stdio...")
    try:
        # This should work
        await asyncio.wait_for(mcp.run_async(transport="stdio"), timeout=2.0)
    except asyncio.TimeoutError:
        print("Server started successfully (timeout expected)")
    except Exception as e:
        print(f"Error: {e}")
        
    print("Testing run_stdio_async directly...")
    try:
        # This should also work
        await asyncio.wait_for(mcp.run_stdio_async(), timeout=2.0)
    except asyncio.TimeoutError:
        print("Direct run_stdio_async started successfully (timeout expected)")
    except Exception as e:
        print(f"Error in run_stdio_async: {e}")

if __name__ == "__main__":
    asyncio.run(test_server()) 