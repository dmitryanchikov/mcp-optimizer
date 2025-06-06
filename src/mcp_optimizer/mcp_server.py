"""MCP server implementation for optimization tools."""

import logging
import time
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
from mcp_optimizer.utils.resource_monitor import (
    get_resource_status,
    reset_resource_stats,
    resource_monitor,
)

logger = logging.getLogger(__name__)

# Server start time for uptime calculation
_server_start_time = time.time()


def create_mcp_server() -> FastMCP[dict[str, str]]:
    """Create and configure the MCP server with optimization tools."""

    # Create MCP server
    mcp: FastMCP[dict[str, str]] = FastMCP(
        "MCP Optimizer",
        description="Mathematical optimization server providing linear programming, "
        "integer programming, routing, scheduling, and other optimization tools",
    )

    # Register all optimization tools
    register_linear_programming_tools(mcp)
    register_integer_programming_tools(mcp)
    register_assignment_tools(mcp)
    register_knapsack_tools(mcp)
    register_routing_tools(mcp)
    register_scheduling_tools(mcp)
    register_financial_tools(mcp)
    register_production_tools(mcp)
    register_validation_tools(mcp)

    # Health check resource
    @mcp.resource("resource://health")
    def get_health() -> dict[str, Any]:
        """Get server health status and resource information."""
        try:
            resource_status = get_resource_status()

            status = "healthy"
            messages = []

            # Check memory usage
            current_memory = resource_status.get("current_memory_mb", 0)
            max_memory = resource_status.get("max_memory_mb", 1024)
            memory_usage_pct = (current_memory / max_memory) * 100 if max_memory > 0 else 0

            if memory_usage_pct > 90:
                status = "critical"
                messages.append(f"High memory usage: {memory_usage_pct:.1f}%")
            elif memory_usage_pct > 75:
                status = "warning"
                messages.append(f"Elevated memory usage: {memory_usage_pct:.1f}%")

            # Check active requests
            active_requests = resource_status.get("active_requests", 0)
            max_requests = resource_status.get("max_concurrent_requests", 10)

            if active_requests >= max_requests:
                status = "warning"
                messages.append("At maximum concurrent request limit")

            health_info = {
                "status": status,
                "version": get_version("mcp-optimizer"),
                "uptime": time.time() - _server_start_time,
                "requests_processed": resource_monitor.total_requests,
                "resource_stats": resource_monitor.get_stats(),
            }

            return {
                "status": status,
                "version": get_version("mcp-optimizer"),
                "uptime": time.time() - _server_start_time,
                "message": "; ".join(messages),
                "resource_status": resource_status,
                "health_info": health_info,
            }
        except ImportError as e:
            return {
                "status": "error",
                "message": f"Health check failed: {e}",
                "resource_status": {},
            }

    # Resource monitoring endpoints
    @mcp.resource("resource://resource-stats")
    def get_resource_stats() -> dict[str, Any]:
        """Get detailed resource usage statistics."""
        return get_resource_status()

    @mcp.resource("resource://resource-reset")
    def reset_resource_statistics() -> dict[str, str]:
        """Reset resource monitoring statistics."""
        reset_resource_stats()
        return {"status": "reset", "message": "Resource statistics have been reset"}

    # Server info resource
    @mcp.resource("resource://server-info")
    def get_server_info() -> dict[str, Any]:
        """Get comprehensive server information."""
        return {
            "name": "MCP Optimizer",
            "version": get_version("mcp-optimizer"),
            "description": "Mathematical optimization server with multiple solvers",
            "uptime": time.time() - _server_start_time,
            "capabilities": {
                "linear_programming": True,
                "integer_programming": True,
                "mixed_integer_programming": True,
                "assignment_problems": True,
                "transportation_problems": True,
                "knapsack_problems": True,
                "routing_problems": True,
                "scheduling_problems": True,
                "portfolio_optimization": True,
                "production_planning": True,
                "input_validation": True,
            },
            "solvers": {
                "pulp": "Linear/Integer Programming",
                "ortools": "Routing, Scheduling, Assignment",
                "native": "Portfolio, Production Planning",
            },
            "configuration": {
                "max_solve_time": settings.max_solve_time,
                "max_memory_mb": settings.max_memory_mb,
                "max_concurrent_requests": settings.max_concurrent_requests,
                "log_level": settings.log_level.value,
                "debug": settings.debug,
            },
        }

    logger.info("MCP Optimizer server created and configured")
    logger.info(
        f"Configuration: max_solve_time={settings.max_solve_time}s, "
        f"max_memory={settings.max_memory_mb}MB, "
        f"max_concurrent={settings.max_concurrent_requests}"
    )

    return mcp
