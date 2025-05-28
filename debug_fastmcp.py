#!/usr/bin/env python3
"""Debug script for FastMCP."""

import inspect
import fastmcp
from fastmcp.server.server import FastMCP

print(f"FastMCP version: {fastmcp.__version__}")
print("\nFastMCP methods:")
for name, method in inspect.getmembers(FastMCP):
    if not name.startswith('_'):
        print(f"  {name}")

print("\nChecking run_stdio_async:")
if hasattr(FastMCP, 'run_stdio_async'):
    print("  Found run_stdio_async method")
    print(f"  Signature: {inspect.signature(FastMCP.run_stdio_async)}")
    try:
        source = inspect.getsource(FastMCP.run_stdio_async)
        print("  Source code:")
        print(source)
    except Exception as e:
        print(f"  Error getting source: {e}")
else:
    print("  run_stdio_async method not found")

print("\nChecking run_async method:")
print(f"  Signature: {inspect.signature(FastMCP.run_async)}")
try:
    source = inspect.getsource(FastMCP.run_async)
    print("  Source code:")
    print(source[:1500])
except Exception as e:
    print(f"  Error getting source: {e}")

print("\nChecking run method source:")
try:
    source = inspect.getsource(FastMCP.run)
    print(source[:1000])
except Exception as e:
    print(f"Error getting source: {e}") 