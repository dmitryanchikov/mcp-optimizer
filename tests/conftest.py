"""Test configuration and fixtures."""

import pytest
from fastmcp import FastMCP

from mcp_optimizer.mcp_server import create_mcp_server


@pytest.fixture
def mcp_server() -> FastMCP:
    """Create MCP server for testing."""
    return create_mcp_server()


@pytest.fixture
def sample_linear_program():
    """Sample linear programming problem data."""
    return {
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


@pytest.fixture
def sample_assignment_problem():
    """Sample assignment problem data."""
    return {
        "workers": ["Alice", "Bob", "Charlie"],
        "tasks": ["Task1", "Task2", "Task3"],
        "costs": [[90, 80, 75], [35, 85, 55], [125, 95, 90]],
    }
