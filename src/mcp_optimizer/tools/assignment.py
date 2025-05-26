"""Assignment problem tools for MCP server."""

import logging
from typing import Any

from fastmcp import FastMCP

from mcp_optimizer.solvers.ortools_solver import ORToolsSolver

logger = logging.getLogger(__name__)

# Define functions that can be imported directly
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

        # Validate consumer format
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

        # Validate cost matrix dimensions
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
    """Register assignment problem tools with the MCP server."""

    @mcp.tool()
    def solve_assignment_problem_tool(
        workers: list[str],
        tasks: list[str],
        costs: list[list[float]],
        maximize: bool = False,
        max_tasks_per_worker: int | None = None,
        min_tasks_per_worker: int | None = None,
    ) -> dict[str, Any]:
        """Solve assignment problem using OR-Tools.

        This tool solves assignment problems where workers need to be assigned
        to tasks optimally. It uses the Hungarian algorithm for simple 1:1
        assignments and linear programming for complex constraints.

        Use cases:
        - Task assignment: Assign employees to projects based on skills and workload
        - Machine scheduling: Assign jobs to machines to minimize completion time
        - Course scheduling: Assign teachers to classes considering preferences
        - Delivery routing: Assign delivery drivers to routes optimally
        - Resource matching: Match available resources to requirements
        - Partner matching: Pair people or entities based on compatibility scores

        Args:
            workers: List of worker names
            tasks: List of task names
            costs: Cost matrix where costs[i][j] is the cost of assigning worker i to task j
            maximize: Whether to maximize instead of minimize the objective (default: False)
            max_tasks_per_worker: Maximum number of tasks per worker (optional)
            min_tasks_per_worker: Minimum number of tasks per worker (optional)

        Returns:
            Assignment result with total cost and individual assignments

        Example:
            # Assign 3 workers to 3 tasks to minimize total cost
            solve_assignment_problem(
                workers=["Alice", "Bob", "Charlie"],
                tasks=["Task1", "Task2", "Task3"],
                costs=[
                    [9, 2, 7],  # Alice's costs for each task
                    [6, 4, 3],  # Bob's costs for each task
                    [5, 8, 1]   # Charlie's costs for each task
                ]
            )
        """
        return solve_assignment_problem(workers, tasks, costs, maximize, max_tasks_per_worker, min_tasks_per_worker)

    @mcp.tool()
    def solve_transportation_problem_tool(
        suppliers: list[dict[str, Any]],
        consumers: list[dict[str, Any]],
        costs: list[list[float]],
    ) -> dict[str, Any]:
        """Solve transportation problem using OR-Tools.

        This tool solves transportation problems where goods need to be moved
        from suppliers to consumers at minimum cost while satisfying supply
        and demand constraints.

        Use cases:
        - Supply chain logistics: Move goods from warehouses to retail locations
        - Distribution planning: Optimize product distribution to minimize shipping costs
        - Emergency response: Allocate emergency supplies from depots to affected areas
        - Raw material sourcing: Transport materials from suppliers to manufacturing plants
        - Waste management: Route waste from collection points to processing facilities
        - Food distribution: Distribute perishable goods from farms to markets efficiently

        Args:
            suppliers: List of suppliers, each with 'name' and 'supply' amount
            consumers: List of consumers, each with 'name' and 'demand' amount
            costs: Transportation cost matrix where costs[i][j] is the cost per unit
                  from supplier i to consumer j

        Returns:
            Transportation result with total cost and individual flows

        Example:
            # Transport goods from 2 suppliers to 3 consumers
            solve_transportation_problem(
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
        """
        return solve_transportation_problem(suppliers, consumers, costs)

    logger.info("Registered assignment and transportation tools") 