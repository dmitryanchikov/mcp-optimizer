"""MCP server implementation for optimization tools."""

import logging
from importlib.metadata import version as get_version
from typing import Any

from fastmcp import FastMCP

from mcp_optimizer.config import settings
from mcp_optimizer.tools.assignment import register_assignment_tools
from mcp_optimizer.tools.financial import register_financial_tools
from mcp_optimizer.tools.integer_programming import register_integer_programming_tools
from mcp_optimizer.tools.knapsack import register_knapsack_tools
from mcp_optimizer.tools.linear_programming import register_linear_programming_tools
from mcp_optimizer.tools.production import register_production_tools
from mcp_optimizer.tools.routing import register_routing_tools
from mcp_optimizer.tools.scheduling import register_scheduling_tools
from mcp_optimizer.tools.validation import register_validation_tools

logger = logging.getLogger(__name__)

# Get package version dynamically
try:
    __version__ = get_version("mcp-optimizer")
except Exception:
    __version__ = "unknown"


def create_mcp_server() -> FastMCP[Any]:
    """Create and configure MCP server with optimization tools."""

    # Create FastMCP server instance
    mcp: FastMCP[Any] = FastMCP(
        name="mcp-optimizer",
        version=__version__,
        description="Mathematical optimization server using PuLP and OR-Tools",
    )

    # Add server info endpoint
    @mcp.tool()
    def get_server_info() -> dict[str, Any]:
        """Get information about the MCP Optimizer server.

        Returns:
            Server information including version, capabilities, and configuration.
        """
        return {
            "name": "MCP Optimizer",
            "version": __version__,
            "description": "Mathematical optimization server using PuLP and OR-Tools",
            "capabilities": [
                "linear_programming",
                "integer_programming",
                "assignment_problems",
                "transportation_problems",
                "knapsack_problems",
                "traveling_salesman",
                "vehicle_routing",
                "job_scheduling",
                "shift_scheduling",
                "portfolio_optimization",
                "production_planning",
                "input_validation",
            ],
            "solvers": {
                "pulp": ["CBC", "GLPK", "GUROBI", "CPLEX"],
                "ortools": ["CP-SAT", "SCIP", "Linear Solver"],
            },
            "configuration": {
                "default_solver": settings.default_solver.value,
                "max_solve_time": settings.max_solve_time,
                "max_memory_mb": settings.max_memory_mb,
                "max_concurrent_requests": settings.max_concurrent_requests,
            },
        }

    # Add health check endpoint
    @mcp.tool()
    def health_check() -> dict[str, str]:
        """Check server health status.

        Returns:
            Health status information.
        """
        try:
            # Test basic imports
            import ortools
            import pulp

            return {
                "status": "healthy",
                "pulp_version": getattr(pulp, "__version__", "unknown"),
                "ortools_version": getattr(ortools, "__version__", "unknown"),
                "message": "All optimization libraries are available",
            }
        except ImportError as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Required optimization libraries are not available",
            }

    # Register all optimization tools
    register_validation_tools(mcp)
    register_linear_programming_tools(mcp)
    register_integer_programming_tools(mcp)
    register_assignment_tools(mcp)
    register_knapsack_tools(mcp)
    register_routing_tools(mcp)
    register_scheduling_tools(mcp)
    register_financial_tools(mcp)
    register_production_tools(mcp)

    logger.info("MCP server created with all optimization tools")
    return mcp
