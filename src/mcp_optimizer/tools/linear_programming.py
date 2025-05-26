"""Linear programming tools for MCP server."""

import logging
from typing import Any

from fastmcp import FastMCP

from mcp_optimizer.schemas.base import Constraint, Objective, Variable
from mcp_optimizer.solvers.pulp_solver import PuLPSolver

logger = logging.getLogger(__name__)

# Define functions that can be imported directly
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
        vars_dict = {
            name: Variable(**var_data) for name, var_data in variables.items()
        }
        constraints_list = [Constraint(**constraint) for constraint in constraints]

        # Create solver
        pulp_solver = PuLPSolver(solver_name=solver)

        # Solve problem
        result = pulp_solver.solve_linear_program(
            objective=obj,
            variables=vars_dict,
            constraints=constraints_list,
            time_limit=time_limit_seconds,
        )

        logger.info(f"Linear program solved with status: {result.get('status') if isinstance(result, dict) else result}")
        return result if isinstance(result, dict) else {"error": "Invalid result type"}

    except Exception as e:
        logger.error(f"Error in solve_linear_program: {e}")
        return {
            "status": "error",
            "objective_value": None,
            "execution_time": 0.0,
            "error_message": f"Failed to solve linear program: {str(e)}",
            "variables": {},
            "solver_info": {"solver_name": solver},
        }


def solve_integer_program(
    objective: dict[str, Any],
    variables: dict[str, dict[str, Any]],
    constraints: list[dict[str, Any]],
    solver: str = "CBC",
    time_limit_seconds: float | None = None,
) -> dict[str, Any]:
    """Solve an integer or mixed-integer programming problem using PuLP."""
    try:
        # Parse and validate input
        obj = Objective(**objective)
        vars_dict = {
            name: Variable(**var_data) for name, var_data in variables.items()
        }
        constraints_list = [Constraint(**constraint) for constraint in constraints]

        # Create solver
        pulp_solver = PuLPSolver(solver_name=solver)

        # Solve problem (same method handles integer/binary variables)
        result = pulp_solver.solve_linear_program(
            objective=obj,
            variables=vars_dict,
            constraints=constraints_list,
            time_limit=time_limit_seconds,
        )

        logger.info(f"Integer program solved with status: {result.get('status') if isinstance(result, dict) else result}")
        return result if isinstance(result, dict) else {"error": "Invalid result type"}

    except Exception as e:
        logger.error(f"Error in solve_integer_program: {e}")
        return {
            "status": "error",
            "objective_value": None,
            "execution_time": 0.0,
            "error_message": f"Failed to solve integer program: {str(e)}",
            "variables": {},
            "solver_info": {"solver_name": solver},
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
        return solve_linear_program(objective, variables, constraints, solver, time_limit_seconds)

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
        return solve_integer_program(objective, variables, constraints, solver, time_limit_seconds)

    logger.info("Registered linear programming tools")
