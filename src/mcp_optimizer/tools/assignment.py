"""Assignment problem tools for MCP server."""

import logging
from typing import Any

from fastmcp import FastMCP

from mcp_optimizer.solvers.ortools_solver import ORToolsSolver
from mcp_optimizer.utils.resource_monitor import with_resource_limits

logger = logging.getLogger(__name__)


# Define functions that can be imported directly
@with_resource_limits(timeout_seconds=60.0, estimated_memory_mb=80.0)
def solve_assignment_problem(
    workers: list[str],
    tasks: list[str],
    costs: list[list[float]],
    maximize: bool = False,
    max_tasks_per_worker: int | None = None,
    min_tasks_per_worker: int | None = None,
) -> dict[str, Any]:
    """Solve assignment problem using OR-Tools."""
    try:
        # Validate input
        if not workers:
            return {
                "status": "error",
                "total_cost": None,
                "assignments": [],
                "execution_time": 0.0,
                "error_message": "No workers provided",
            }

        if not tasks:
            return {
                "status": "error",
                "total_cost": None,
                "assignments": [],
                "execution_time": 0.0,
                "error_message": "No tasks provided",
            }

        if len(costs) != len(workers):
            return {
                "status": "error",
                "total_cost": None,
                "assignments": [],
                "execution_time": 0.0,
                "error_message": f"Cost matrix rows ({len(costs)}) must match workers count ({len(workers)})",
            }

        for i, row in enumerate(costs):
            if len(row) != len(tasks):
                return {
                    "status": "error",
                    "total_cost": None,
                    "assignments": [],
                    "execution_time": 0.0,
                    "error_message": f"Cost matrix row {i} length ({len(row)}) must match tasks count ({len(tasks)})",
                }

        # Create solver and solve
        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            maximize=maximize,
            max_tasks_per_worker=max_tasks_per_worker,
            min_tasks_per_worker=min_tasks_per_worker,
        )

        logger.info(f"Assignment problem solved with status: {result.get('status')}")
        return result

    except Exception as e:
        logger.error(f"Error in solve_assignment_problem: {e}")
        return {
            "status": "error",
            "total_cost": None,
            "assignments": [],
            "execution_time": 0.0,
            "error_message": f"Failed to solve assignment problem: {str(e)}",
        }


def solve_transportation_problem(
    suppliers: list[dict[str, Any]],
    consumers: list[dict[str, Any]],
    costs: list[list[float]],
) -> dict[str, Any]:
    """Solve transportation problem using OR-Tools."""
    try:
        # Validate input
        if not suppliers:
            return {
                "status": "error",
                "total_cost": None,
                "flows": [],
                "execution_time": 0.0,
                "error_message": "No suppliers provided",
            }

        if not consumers:
            return {
                "status": "error",
                "total_cost": None,
                "flows": [],
                "execution_time": 0.0,
                "error_message": "No consumers provided",
            }

        # Validate supplier format
        for i, supplier in enumerate(suppliers):
            if not isinstance(supplier, dict):
                return {
                    "status": "error",
                    "total_cost": None,
                    "flows": [],
                    "execution_time": 0.0,
                    "error_message": f"Supplier {i} must be a dictionary",
                }
            if "name" not in supplier or "supply" not in supplier:
                return {
                    "status": "error",
                    "total_cost": None,
                    "flows": [],
                    "execution_time": 0.0,
                    "error_message": f"Supplier {i} must have 'name' and 'supply' fields",
                }

        # Validate consumer format  # type: ignore[unreachable]
        for i, consumer in enumerate(consumers):
            if not isinstance(consumer, dict):
                return {
                    "status": "error",
                    "total_cost": None,
                    "flows": [],
                    "execution_time": 0.0,
                    "error_message": f"Consumer {i} must be a dictionary",
                }
            if "name" not in consumer or "demand" not in consumer:
                return {
                    "status": "error",
                    "total_cost": None,
                    "flows": [],
                    "execution_time": 0.0,
                    "error_message": f"Consumer {i} must have 'name' and 'demand' fields",
                }

        # Validate cost matrix dimensions  # type: ignore[unreachable]
        if len(costs) != len(suppliers):
            return {
                "status": "error",
                "total_cost": None,
                "flows": [],
                "execution_time": 0.0,
                "error_message": f"Cost matrix rows ({len(costs)}) must match suppliers count ({len(suppliers)})",
            }

        for i, row in enumerate(costs):
            if len(row) != len(consumers):
                return {
                    "status": "error",
                    "total_cost": None,
                    "flows": [],
                    "execution_time": 0.0,
                    "error_message": f"Cost matrix row {i} length ({len(row)}) must match consumers count ({len(consumers)})",
                }

        # Check supply-demand balance
        total_supply = sum(supplier["supply"] for supplier in suppliers)
        total_demand = sum(consumer["demand"] for consumer in consumers)

        if abs(total_supply - total_demand) > 1e-6:
            return {
                "status": "error",
                "total_cost": None,
                "flows": [],
                "execution_time": 0.0,
                "error_message": f"Total supply ({total_supply}) must equal total demand ({total_demand})",
            }

        # Create solver and solve
        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(
            suppliers=suppliers,
            consumers=consumers,
            costs=costs,
        )

        logger.info(f"Transportation problem solved with status: {result.get('status')}")
        return result

    except Exception as e:
        logger.error(f"Error in solve_transportation_problem: {e}")
        return {
            "status": "error",
            "total_cost": None,
            "flows": [],
            "execution_time": 0.0,
            "error_message": f"Failed to solve transportation problem: {str(e)}",
        }


def register_assignment_tools(mcp: FastMCP[Any]) -> None:
    """Register assignment and transportation problem tools."""

    @mcp.tool()
    def solve_assignment_problem_tool(
        workers: list[str],
        tasks: list[str],
        costs: list[list[float]],
        maximize: bool = False,
        max_tasks_per_worker: int | None = None,
        min_tasks_per_worker: int | None = None,
    ) -> dict[str, Any]:
        """
        Solve assignment problem using OR-Tools Hungarian algorithm.

        Args:
            workers: List of worker names
            tasks: List of task names
            costs: 2D cost matrix where costs[i][j] is cost of assigning worker i to task j
            maximize: Whether to maximize instead of minimize (default: False)
            max_tasks_per_worker: Maximum tasks per worker (optional)
            min_tasks_per_worker: Minimum tasks per worker (optional)

        Returns:
            Dictionary with solution status, assignments, total cost, and execution time
        """
        result = solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            maximize=maximize,
            max_tasks_per_worker=max_tasks_per_worker,
            min_tasks_per_worker=min_tasks_per_worker,
        )
        result_dict: dict[str, Any] = result
        return result_dict

    @mcp.tool()
    def solve_transportation_problem_tool(
        suppliers: list[dict[str, Any]],
        consumers: list[dict[str, Any]],
        costs: list[list[float]],
    ) -> dict[str, Any]:
        """
        Solve transportation problem using OR-Tools.

        Args:
            suppliers: List of supplier dictionaries with 'name' and 'supply' keys
            consumers: List of consumer dictionaries with 'name' and 'demand' keys
            costs: 2D cost matrix where costs[i][j] is cost of shipping from supplier i to consumer j

        Returns:
            Dictionary with solution status, flows, total cost, and execution time
        """
        return solve_transportation_problem(
            suppliers=suppliers,
            consumers=consumers,
            costs=costs,
        )

    logger.info("Registered assignment and transportation tools")
