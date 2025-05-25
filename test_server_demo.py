#!/usr/bin/env python3
"""Demo script to test MCP Optimizer server functionality."""

import asyncio
import json
import sys
from typing import Any, Dict

from mcp_optimizer.mcp_server import create_mcp_server


async def test_server_tools():
    """Test the MCP server tools."""
    print("🚀 Testing MCP Optimizer Server")
    print("=" * 50)
    
    # Create server
    server = create_mcp_server()
    
    # Get available tools
    # For demo purposes, we'll test the tools directly
    print("📋 Available tools:")
    print("  - get_server_info")
    print("  - health_check")
    print("  - validate_optimization_input")
    print("  - solve_linear_program")
    print("  - solve_integer_program")
    print("  - solve_assignment_problem")
    print("  - solve_transportation_problem")
    
    print("\n" + "=" * 50)
    
    # Test server info
    print("🔍 Testing get_server_info...")
    try:
        if "get_server_info" in tools_dict:
            # Call the tool function directly
            tool_func = tools_dict["get_server_info"]
            result = tool_func()
            print("✅ Server info:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ get_server_info tool not found")
    except Exception as e:
        print(f"❌ Error testing server info: {e}")
    
    print("\n" + "=" * 50)
    
    # Test health check
    print("🏥 Testing health_check...")
    try:
        if "health_check" in tools_dict:
            tool_func = tools_dict["health_check"]
            result = tool_func()
            print("✅ Health check:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ health_check tool not found")
    except Exception as e:
        print(f"❌ Error testing health check: {e}")
    
    print("\n" + "=" * 50)
    
    # Test validation
    print("🔍 Testing validate_optimization_input...")
    try:
        if "validate_optimization_input" in tools_dict:
            # Test valid linear program
            test_data = {
                "objective": {"sense": "maximize", "coefficients": {"x": 3, "y": 2}},
                "variables": {
                    "x": {"type": "continuous", "lower": 0},
                    "y": {"type": "continuous", "lower": 0},
                },
                "constraints": [
                    {"expression": {"x": 2, "y": 1}, "operator": "<=", "rhs": 20},
                    {"expression": {"x": 1, "y": 3}, "operator": "<=", "rhs": 30},
                ],
            }
            
            tool_func = tools_dict["validate_optimization_input"]
            result = tool_func(
                problem_type="linear_program",
                input_data=test_data
            )
            print("✅ Validation result:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ validate_optimization_input tool not found")
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
    
    print("\n" + "=" * 50)
    
    # Test linear programming
    print("🧮 Testing solve_linear_program...")
    try:
        if "solve_linear_program" in tools_dict:
            # Simple linear program: maximize 3x + 2y subject to constraints
            tool_func = tools_dict["solve_linear_program"]
            result = tool_func(
                objective={"sense": "maximize", "coefficients": {"x": 3, "y": 2}},
                variables={
                    "x": {"type": "continuous", "lower": 0},
                    "y": {"type": "continuous", "lower": 0},
                },
                constraints=[
                    {"expression": {"x": 2, "y": 1}, "operator": "<=", "rhs": 20},
                    {"expression": {"x": 1, "y": 3}, "operator": "<=", "rhs": 30},
                ],
                solver="CBC"
            )
            print("✅ Linear program result:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ solve_linear_program tool not found")
    except Exception as e:
        print(f"❌ Error testing linear program: {e}")
    
    print("\n" + "=" * 50)
    
    # Test integer programming
    print("🔢 Testing solve_integer_program...")
    try:
        if "solve_integer_program" in tools_dict:
            # Binary knapsack problem
            tool_func = tools_dict["solve_integer_program"]
            result = tool_func(
                objective={"sense": "maximize", "coefficients": {"item1": 10, "item2": 15}},
                variables={
                    "item1": {"type": "binary"},
                    "item2": {"type": "binary"},
                },
                constraints=[
                    {"expression": {"item1": 5, "item2": 8}, "operator": "<=", "rhs": 10}
                ],
                solver="CBC"
            )
            print("✅ Integer program result:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ solve_integer_program tool not found")
    except Exception as e:
        print(f"❌ Error testing integer program: {e}")
    
    print("\n" + "=" * 50)
    
    # Test assignment problem
    print("🔗 Testing solve_assignment_problem...")
    try:
        if "solve_assignment_problem" in tools_dict:
            # Simple 3x3 assignment problem
            tool_func = tools_dict["solve_assignment_problem"]
            result = tool_func(
                workers=["Alice", "Bob", "Charlie"],
                tasks=["Task1", "Task2", "Task3"],
                costs=[
                    [9, 2, 7],  # Alice's costs
                    [6, 4, 3],  # Bob's costs
                    [5, 8, 1]   # Charlie's costs
                ]
            )
            print("✅ Assignment problem result:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ solve_assignment_problem tool not found")
    except Exception as e:
        print(f"❌ Error testing assignment problem: {e}")
    
    print("\n" + "=" * 50)
    
    # Test transportation problem
    print("🚚 Testing solve_transportation_problem...")
    try:
        if "solve_transportation_problem" in tools_dict:
            # Simple transportation problem
            tool_func = tools_dict["solve_transportation_problem"]
            result = tool_func(
                suppliers=[
                    {"name": "Warehouse A", "supply": 100},
                    {"name": "Warehouse B", "supply": 150}
                ],
                consumers=[
                    {"name": "Store 1", "demand": 80},
                    {"name": "Store 2", "demand": 70},
                    {"name": "Store 3", "demand": 100}
                ],
                costs=[
                    [4, 6, 8],  # Costs from Warehouse A
                    [5, 3, 7]   # Costs from Warehouse B
                ]
            )
            print("✅ Transportation problem result:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ solve_transportation_problem tool not found")
    except Exception as e:
        print(f"❌ Error testing transportation problem: {e}")
    
    print("\n" + "🎉 Demo completed!")


if __name__ == "__main__":
    asyncio.run(test_server_tools()) 