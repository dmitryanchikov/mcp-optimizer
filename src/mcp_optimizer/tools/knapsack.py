"""Knapsack problem tools for MCP server."""

import logging
import time
from typing import Any

from fastmcp import FastMCP
from ortools.algorithms.python import knapsack_solver

from mcp_optimizer.config import settings

logger = logging.getLogger(__name__)


# Define function that can be imported directly
def solve_knapsack_problem(
    items: list[dict[str, Any]],
    capacity: float,
    volume_capacity: float | None = None,
    knapsack_type: str = "0-1",
    max_items_per_type: int | None = None,
) -> dict[str, Any]:
    """Solve knapsack optimization problems using OR-Tools."""
    try:
        # Validate input
        if not items:
            return {
                "status": "error",
                "total_value": None,
                "selected_items": [],
                "execution_time": 0.0,
                "error_message": "No items provided",
            }

        if capacity <= 0:
            return {
                "status": "error",
                "total_value": None,
                "selected_items": [],
                "execution_time": 0.0,
                "error_message": "Capacity must be positive",
            }

        # Validate item format
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                return {
                    "status": "error",
                    "total_value": None,
                    "selected_items": [],
                    "execution_time": 0.0,
                    "error_message": f"Item {i} must be a dictionary",
                }

            required_fields = ["name", "value", "weight"]
            for field in required_fields:
                if field not in item:
                    return {
                        "status": "error",
                        "total_value": None,
                        "selected_items": [],
                        "execution_time": 0.0,
                        "error_message": f"Item {i} missing required field: {field}",
                    }

            if item["value"] < 0 or item["weight"] < 0:
                return {
                    "status": "error",
                    "total_value": None,
                    "selected_items": [],
                    "execution_time": 0.0,
                    "error_message": f"Item {i} value and weight must be non-negative",
                }

        start_time = time.time()

        # Choose appropriate solver based on constraints
        if volume_capacity and any("volume" in item for item in items):
            # Use multidimensional solver for volume constraints
            solver = knapsack_solver.KnapsackSolver(
                knapsack_solver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER,
                "KnapsackSolver",
            )
        else:
            # Use dynamic programming for single dimension
            solver = knapsack_solver.KnapsackSolver(
                knapsack_solver.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "KnapsackSolver"
            )

        # Prepare data
        values = []
        weights = []
        volumes = []
        item_names = []

        for item in items:
            quantity = item.get("quantity", 1)
            if knapsack_type == "unbounded":
                # For unbounded, add multiple copies up to capacity
                max_copies = int(capacity / item["weight"]) + 1
                for _ in range(max_copies):
                    values.append(int(item["value"] * 1000))  # Scale for integer solver
                    weights.append(int(item["weight"] * 1000))
                    if volume_capacity and "volume" in item:
                        volumes.append(int(item["volume"] * 1000))
                    item_names.append(item["name"])
            elif knapsack_type == "bounded":
                # For bounded, add specified quantity
                max_quantity = max_items_per_type or quantity
                for _ in range(max_quantity):
                    values.append(int(item["value"] * 1000))
                    weights.append(int(item["weight"] * 1000))
                    if volume_capacity and "volume" in item:
                        volumes.append(int(item["volume"] * 1000))
                    item_names.append(item["name"])
            else:  # 0-1 knapsack
                values.append(int(item["value"] * 1000))
                weights.append(int(item["weight"] * 1000))
                if volume_capacity and "volume" in item:
                    volumes.append(int(item["volume"] * 1000))
                item_names.append(item["name"])

        # Set up constraints
        capacities = [int(capacity * 1000)]
        if volume_capacity and volumes:
            capacities.append(int(volume_capacity * 1000))
            weight_matrix = [weights, volumes]
        else:
            weight_matrix = [weights]

        solver.init(values, weight_matrix, capacities)

        # Set time limit
        solver.set_time_limit(int(settings.max_solve_time))

        # Solve
        computed_value = solver.solve()

        execution_time = time.time() - start_time

        if computed_value > 0:
            # Extract solution
            selected_items = []
            total_value = 0.0
            item_counts: dict[str, int] = {}

            for i in range(len(values)):
                if solver.best_solution_contains(i):
                    item_name = item_names[i]
                    original_item = next(item for item in items if item["name"] == item_name)

                    if item_name in item_counts:
                        item_counts[item_name] += 1
                    else:
                        item_counts[item_name] = 1

            # Create selected items list
            for item_name, count in item_counts.items():
                original_item = next(item for item in items if item["name"] == item_name)
                selected_items.append(
                    {
                        "name": item_name,
                        "quantity": count,
                        "value": original_item["value"],
                        "weight": original_item["weight"],
                        "volume": original_item.get("volume"),
                        "total_value": original_item["value"] * count,
                        "total_weight": original_item["weight"] * count,
                        "total_volume": original_item.get("volume", 0) * count
                        if original_item.get("volume")
                        else None,
                    }
                )
                total_value += original_item["value"] * count

            result = {
                "status": "optimal",
                "total_value": total_value,
                "selected_items": selected_items,
                "execution_time": execution_time,
                "solver_info": {
                    "solver_name": "OR-Tools KnapsackSolver",
                    "algorithm": "Dynamic Programming"
                    if not volume_capacity
                    else "Branch and Bound",
                    "items_count": len(items),
                    "capacity": capacity,
                    "volume_capacity": volume_capacity,
                },
            }
        else:
            result = {
                "status": "infeasible",
                "total_value": 0.0,
                "selected_items": [],
                "execution_time": execution_time,
                "solver_info": {
                    "solver_name": "OR-Tools KnapsackSolver",
                    "algorithm": "Dynamic Programming"
                    if not volume_capacity
                    else "Branch and Bound",
                    "items_count": len(items),
                    "capacity": capacity,
                    "volume_capacity": volume_capacity,
                },
            }

        logger.info(f"Knapsack problem solved with status: {result['status']}")
        return result

    except Exception as e:
        logger.error(f"Error in solve_knapsack_problem: {e}")
        return {
            "status": "error",
            "total_value": None,
            "selected_items": [],
            "execution_time": 0.0,
            "error_message": f"Failed to solve knapsack problem: {str(e)}",
        }


def register_knapsack_tools(mcp: FastMCP[Any]) -> None:
    """Register knapsack problem tools with the MCP server."""

    @mcp.tool()
    def solve_knapsack_problem_tool(
        items: list[dict[str, Any]],
        capacity: float,
        volume_capacity: float | None = None,
        knapsack_type: str = "0-1",
        max_items_per_type: int | None = None,
    ) -> dict[str, Any]:
        """Solve knapsack optimization problems using OR-Tools.

        This tool solves knapsack problems where items need to be selected
        to maximize value while staying within capacity constraints.

        Use cases:
        - Cargo loading: Optimize loading of trucks, ships, or planes by weight and volume
        - Portfolio selection: Choose optimal set of investments within budget constraints
        - Resource allocation: Select projects or activities with limited budget or resources
        - Advertising planning: Choose optimal mix of advertising channels within budget
        - Menu planning: Select dishes for a restaurant menu considering costs and popularity
        - Inventory optimization: Decide which products to stock in limited warehouse space

        Args:
            items: List of items, each with 'name', 'value', 'weight', and optionally 'volume', 'quantity'
            capacity: Weight capacity constraint
            volume_capacity: Volume capacity constraint (optional)
            knapsack_type: Type of knapsack problem ('0-1', 'bounded', 'unbounded')
            max_items_per_type: Maximum items per type for bounded knapsack

        Returns:
            Knapsack result with total value and selected items

        Example:
            # Select items to maximize value within weight limit
            solve_knapsack_problem(
                items=[
                    {"name": "Item1", "value": 10, "weight": 5, "volume": 2},
                    {"name": "Item2", "value": 15, "weight": 8, "volume": 3},
                    {"name": "Item3", "value": 8, "weight": 3, "volume": 1}
                ],
                capacity=10,
                volume_capacity=5
            )
        """
        return solve_knapsack_problem(
            items, capacity, volume_capacity, knapsack_type, max_items_per_type
        )

    logger.info("Registered knapsack tools")
