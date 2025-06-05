"""Linear programming tools for MCP server."""

import logging
from typing import Any

from fastmcp import FastMCP

from mcp_optimizer.schemas.base import Constraint, Objective, Variable
from mcp_optimizer.solvers.pulp_solver import PuLPSolver
from mcp_optimizer.utils.resource_monitor import with_resource_limits

logger = logging.getLogger(__name__)


# Define functions that can be imported directly
@with_resource_limits(timeout_seconds=60.0, estimated_memory_mb=100.0)
def solve_linear_program(
    objective: dict[str, Any],
    variables: dict[str, dict[str, Any]],
    constraints: list[dict[str, Any]],
    solver: str = "CBC",
    time_limit_seconds: float | None = None,
) -> dict[str, Any]:
    """Solve a linear programming problem using PuLP."""
    try:
        # Parse and validate input
        obj = Objective(**objective)
        vars_dict = {name: Variable(**var_def) for name, var_def in variables.items()}
        constraints_list = [Constraint(**constraint) for constraint in constraints]

        # Create and solve problem
        pulp_solver = PuLPSolver(solver)
        result = pulp_solver.solve_linear_program(
            objective=obj,
            variables=vars_dict,
            constraints=constraints_list,
            time_limit=time_limit_seconds,
        )

        return result

    except Exception as e:
        logger.error(f"Linear programming error: {e}")
        return {
            "status": "error",
            "error_message": f"Failed to solve linear program: {str(e)}",
            "objective_value": None,
            "variables": {},
            "execution_time": 0.0,
            "solver_info": {},
        }


@with_resource_limits(timeout_seconds=60.0, estimated_memory_mb=100.0)
def solve_integer_program(
    objective: dict[str, Any],
    variables: dict[str, dict[str, Any]],
    constraints: list[dict[str, Any]],
    solver: str = "CBC",
    time_limit_seconds: float | None = None,
) -> dict[str, Any]:
    """Solve an integer programming problem using PuLP."""
    try:
        # Parse and validate input
        obj = Objective(**objective)
        vars_dict = {name: Variable(**var_def) for name, var_def in variables.items()}
        constraints_list = [Constraint(**constraint) for constraint in constraints]

        # Create and solve problem with integer variables
        pulp_solver = PuLPSolver(solver)
        result = pulp_solver.solve_linear_program(
            objective=obj,
            variables=vars_dict,
            constraints=constraints_list,
            time_limit=time_limit_seconds,
        )

        return result

    except Exception as e:
        logger.error(f"Integer programming error: {e}")
        return {
            "status": "error",
            "error_message": f"Failed to solve integer program: {str(e)}",
            "objective_value": None,
            "variables": {},
            "execution_time": 0.0,
            "solver_info": {},
        }


def register_linear_programming_tools(mcp: FastMCP[Any]) -> None:
    """Register linear programming tools with the MCP server."""

    @mcp.tool()
    def solve_linear_program_tool(
        objective: dict[str, Any],
        variables: dict[str, dict[str, Any]],
        constraints: list[dict[str, Any]],
        solver: str = "CBC",
        time_limit_seconds: float | None = None,
    ) -> dict[str, Any]:
        """Solve a linear programming problem using PuLP.

        This tool solves general linear programming problems where you want to
        optimize a linear objective function subject to linear constraints.

        Use cases:
        - Resource allocation: Distribute limited resources optimally
        - Diet planning: Create nutritionally balanced meal plans within budget
        - Manufacturing mix: Determine optimal product mix to maximize profit
        - Investment planning: Allocate capital across different investment options
        - Supply chain optimization: Minimize transportation and storage costs
        - Energy optimization: Optimize power generation and distribution

        Args:
            objective: Objective function with 'sense' ("minimize" or "maximize")
                      and 'coefficients' (dict mapping variable names to coefficients)
            variables: Variable definitions mapping variable names to their properties
                      (type: "continuous"/"integer"/"binary", lower: bound, upper: bound)
            constraints: List of constraints, each with 'expression' (coefficients),
                        'operator' ("<=", ">=", "=="), and 'rhs' (right-hand side value)
            solver: Solver to use ("CBC", "GLPK", "GUROBI", "CPLEX")
            time_limit_seconds: Maximum time to spend solving (optional)

        Returns:
            Optimization result with status, objective value, variable values, and solver info

        Example:
            # Maximize 3x + 2y subject to 2x + y <= 20, x + 3y <= 30, x,y >= 0
            solve_linear_program(
                objective={"sense": "maximize", "coefficients": {"x": 3, "y": 2}},
                variables={
                    "x": {"type": "continuous", "lower": 0},
                    "y": {"type": "continuous", "lower": 0}
                },
                constraints=[
                    {"expression": {"x": 2, "y": 1}, "operator": "<=", "rhs": 20},
                    {"expression": {"x": 1, "y": 3}, "operator": "<=", "rhs": 30}
                ]
            )
        """
        result = solve_linear_program(objective, variables, constraints, solver, time_limit_seconds)
        result_dict: dict[str, Any] = result
        return result_dict

    @mcp.tool()
    def solve_integer_program_tool(
        objective: dict[str, Any],
        variables: dict[str, dict[str, Any]],
        constraints: list[dict[str, Any]],
        solver: str = "CBC",
        time_limit_seconds: float | None = None,
    ) -> dict[str, Any]:
        """Solve an integer or mixed-integer programming problem using PuLP.

        This tool solves optimization problems where some or all variables must
        take integer values, which is useful for discrete decision problems.

        Use cases:
        - Facility location: Decide where to build warehouses or service centers
        - Project selection: Choose which projects to fund (binary decisions)
        - Crew scheduling: Assign integer numbers of staff to shifts
        - Network design: Design networks with discrete components
        - Cutting stock: Minimize waste when cutting materials
        - Capital budgeting: Select investments when partial investments aren't allowed

        Args:
            objective: Objective function with 'sense' and 'coefficients'
            variables: Variable definitions with types "continuous", "integer", or "binary"
            constraints: List of linear constraints
            solver: Solver to use ("CBC", "GLPK", "GUROBI", "CPLEX")
            time_limit_seconds: Maximum time to spend solving (optional)

        Returns:
            Optimization result with integer/binary variable values

        Example:
            # Binary knapsack: select items to maximize value within weight limit
            solve_integer_program(
                objective={"sense": "maximize", "coefficients": {"item1": 10, "item2": 15}},
                variables={
                    "item1": {"type": "binary"},
                    "item2": {"type": "binary"}
                },
                constraints=[
                    {"expression": {"item1": 5, "item2": 8}, "operator": "<=", "rhs": 10}
                ]
            )
        """
        result = solve_integer_program(
            objective, variables, constraints, solver, time_limit_seconds
        )
        result_dict: dict[str, Any] = result
        return result_dict

    logger.info("Registered linear programming tools")
