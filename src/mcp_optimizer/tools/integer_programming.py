"""Integer programming optimization tools for MCP server.

This module provides tools for solving integer and mixed-integer programming problems.
"""

import logging
import time
from typing import Any

from fastmcp import FastMCP
from ortools.linear_solver import pywraplp
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from mcp_optimizer.utils.resource_monitor import with_resource_limits

from ..schemas.base import OptimizationResult, OptimizationStatus

logger = logging.getLogger(__name__)


class IntegerVariable(BaseModel):
    """Integer variable definition."""

    name: str
    type: str = Field(pattern="^(integer|binary|continuous)$")
    lower: float | None = None
    upper: float | None = None

    @field_validator("upper")
    @classmethod
    def validate_upper(cls, v: float | None, info: ValidationInfo) -> float | None:
        if v is not None and info.data and "lower" in info.data and v < info.data["lower"]:
            raise ValueError("upper bound must be >= lower bound")
        return v


class IntegerConstraint(BaseModel):
    """Integer programming constraint."""

    name: str | None = None
    expression: dict[str, float]  # variable_name -> coefficient
    operator: str = Field(pattern="^(<=|>=|==)$")
    rhs: float


class IntegerObjective(BaseModel):
    """Integer programming objective."""

    sense: str = Field(pattern="^(minimize|maximize)$")
    coefficients: dict[str, float]  # variable_name -> coefficient

    @field_validator("coefficients")
    @classmethod
    def validate_coefficients(cls, v: dict[str, float]) -> dict[str, float]:
        if not v:
            raise ValueError("Objective must have at least one coefficient")
        return v


class IntegerProgramInput(BaseModel):
    """Input schema for Integer Programming."""

    objective: IntegerObjective
    variables: dict[str, IntegerVariable]
    constraints: list[IntegerConstraint]
    solver: str = Field(default="SCIP", pattern="^(SCIP|CBC|GUROBI|CPLEX)$")
    time_limit_seconds: float | None = Field(default=None, ge=0)
    gap_tolerance: float | None = Field(default=None, ge=0, le=1)

    @field_validator("variables")
    @classmethod
    def validate_variables(cls, v: dict[str, IntegerVariable]) -> dict[str, IntegerVariable]:
        if not v:
            raise ValueError("Must have at least one variable")
        return v

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[IntegerConstraint]) -> list[IntegerConstraint]:
        if not v:
            raise ValueError("Must have at least one constraint")
        return v


@with_resource_limits(timeout_seconds=90.0, estimated_memory_mb=150.0)
def solve_integer_program(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Integer Programming Problem using OR-Tools.

    Args:
        input_data: Integer programming problem specification

    Returns:
        OptimizationResult with optimal solution
    """
    start_time = time.time()

    try:
        # Parse and validate input
        ip_input = IntegerProgramInput(**input_data)

        # Create solver
        solver_name = ip_input.solver
        if solver_name == "SCIP":
            solver = pywraplp.Solver.CreateSolver("SCIP")
        elif solver_name == "CBC":
            solver = pywraplp.Solver.CreateSolver("CBC")
        elif solver_name == "GUROBI":
            solver = pywraplp.Solver.CreateSolver("GUROBI_MIXED_INTEGER_PROGRAMMING")
        elif solver_name == "CPLEX":
            solver = pywraplp.Solver.CreateSolver("CPLEX_MIXED_INTEGER_PROGRAMMING")
        else:
            return OptimizationResult(
                status=OptimizationStatus.ERROR,
                error_message=f"Unsupported solver: {solver_name}",
                execution_time=time.time() - start_time,
            )

        if not solver:
            return OptimizationResult(
                status=OptimizationStatus.ERROR,
                error_message=f"Could not create {solver_name} solver",
                execution_time=time.time() - start_time,
            )

        # Set time limit
        if ip_input.time_limit_seconds:
            solver.SetTimeLimit(int(ip_input.time_limit_seconds * 1000))  # milliseconds

        # Create variables
        variables = {}
        for var_name, var_def in ip_input.variables.items():
            lower = var_def.lower if var_def.lower is not None else -solver.infinity()
            upper = var_def.upper if var_def.upper is not None else solver.infinity()

            if var_def.type == "continuous":
                var = solver.NumVar(lower, upper, var_name)
            elif var_def.type == "integer":
                var = solver.IntVar(
                    int(lower) if lower != -solver.infinity() else -2147483648,
                    int(upper) if upper != solver.infinity() else 2147483647,
                    var_name,
                )
            elif var_def.type == "binary":
                var = solver.BoolVar(var_name)
            else:
                return OptimizationResult(
                    status=OptimizationStatus.ERROR,
                    error_message=f"Unknown variable type: {var_def.type}",
                    execution_time=time.time() - start_time,
                )

            variables[var_name] = var

        # Add constraints
        constraints = []
        for i, constraint_def in enumerate(ip_input.constraints):
            constraint_name = constraint_def.name or f"constraint_{i}"

            # Build constraint expression
            constraint = solver.Constraint(-solver.infinity(), solver.infinity(), constraint_name)

            for var_name, coeff in constraint_def.expression.items():
                if var_name in variables:
                    constraint.SetCoefficient(variables[var_name], coeff)
                else:
                    return OptimizationResult(
                        status=OptimizationStatus.ERROR,
                        error_message=f"Unknown variable '{var_name}' in constraint '{constraint_name}'",
                        execution_time=time.time() - start_time,
                    )

            # Set constraint bounds based on operator
            if constraint_def.operator == "<=":
                constraint.SetUB(constraint_def.rhs)
            elif constraint_def.operator == ">=":
                constraint.SetLB(constraint_def.rhs)
            elif constraint_def.operator == "==":
                constraint.SetLB(constraint_def.rhs)
                constraint.SetUB(constraint_def.rhs)

            constraints.append(constraint)

        # Set objective
        objective = solver.Objective()
        for var_name, coeff in ip_input.objective.coefficients.items():
            if var_name in variables:
                objective.SetCoefficient(variables[var_name], coeff)
            else:
                return OptimizationResult(
                    status=OptimizationStatus.ERROR,
                    error_message=f"Unknown variable '{var_name}' in objective",
                    execution_time=time.time() - start_time,
                )

        if ip_input.objective.sense == "maximize":
            objective.SetMaximization()
        else:
            objective.SetMinimization()

        # Set gap tolerance if specified
        if ip_input.gap_tolerance is not None:
            solver.SetSolverSpecificParametersAsString(f"limits/gap={ip_input.gap_tolerance}")

        # Solve
        status = solver.Solve()

        # Process results
        if status == pywraplp.Solver.OPTIMAL:
            solution_status = OptimizationStatus.OPTIMAL
        elif status == pywraplp.Solver.FEASIBLE:
            solution_status = OptimizationStatus.FEASIBLE
        elif status == pywraplp.Solver.INFEASIBLE:
            solution_status = OptimizationStatus.INFEASIBLE
        elif status == pywraplp.Solver.UNBOUNDED:
            solution_status = OptimizationStatus.UNBOUNDED
        else:
            solution_status = OptimizationStatus.ERROR

        execution_time = time.time() - start_time

        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            # Extract solution
            solution_variables = {}
            for var_name, var in variables.items():
                solution_variables[var_name] = var.solution_value()

            # Calculate constraint violations (for debugging)
            constraint_info = []
            for i, (_constraint, constraint_def) in enumerate(
                zip(constraints, ip_input.constraints, strict=False)
            ):
                lhs_value = sum(
                    coeff * variables[var_name].solution_value()
                    for var_name, coeff in constraint_def.expression.items()
                )

                constraint_info.append(
                    {
                        "name": constraint_def.name or f"constraint_{i}",
                        "lhs_value": lhs_value,
                        "operator": constraint_def.operator,
                        "rhs_value": constraint_def.rhs,
                        "slack": constraint_def.rhs - lhs_value
                        if constraint_def.operator == "<="
                        else lhs_value - constraint_def.rhs,
                    }
                )

            return OptimizationResult(
                status=solution_status,
                objective_value=solver.Objective().Value(),
                variables=solution_variables,
                execution_time=execution_time,
                solver_info={
                    "solver_name": solver_name,
                    "iterations": solver.iterations() if hasattr(solver, "iterations") else None,
                    "nodes": solver.nodes() if hasattr(solver, "nodes") else None,
                    "gap": (solver.Objective().BestBound() - solver.Objective().Value())
                    / abs(solver.Objective().Value())
                    if solver.Objective().Value() != 0 and hasattr(solver.Objective(), "BestBound")
                    else 0,
                    "constraint_info": constraint_info,
                },
            )
        else:
            error_messages = {
                pywraplp.Solver.INFEASIBLE: "Problem is infeasible",
                pywraplp.Solver.UNBOUNDED: "Problem is unbounded",
                pywraplp.Solver.ABNORMAL: "Solver encountered an error",
                pywraplp.Solver.NOT_SOLVED: "Problem not solved",
            }

            return OptimizationResult(
                status=solution_status,
                error_message=error_messages.get(status, f"Unknown solver status: {status}"),
                execution_time=execution_time,
                solver_info={"solver_name": solver_name},
            )

    except Exception as e:
        return OptimizationResult(
            status=OptimizationStatus.ERROR,
            error_message=f"Integer programming error: {str(e)}",
            execution_time=time.time() - start_time,
        )


def solve_binary_program(input_data: dict[str, Any]) -> dict[str, Any]:
    """Solve Binary Programming Problem (convenience function).

    Args:
        input_data: Binary programming problem specification

    Returns:
        Dictionary with optimization result
    """
    # Convert all variables to binary type
    if "variables" in input_data:
        for _var_name, var_def in input_data["variables"].items():
            if isinstance(var_def, dict):
                var_def["type"] = "binary"
                var_def["lower"] = 0
                var_def["upper"] = 1

    result = solve_integer_program(input_data)
    result_dict: dict[str, Any] = result.model_dump()
    return result_dict


def solve_mixed_integer_program(input_data: dict[str, Any]) -> dict[str, Any]:
    """Solve Mixed-Integer Programming Problem (alias for solve_integer_program).

    Args:
        input_data: Mixed-integer programming problem specification

    Returns:
        Dictionary with optimization result
    """
    result = solve_integer_program(input_data)
    result_dict: dict[str, Any] = result.model_dump()
    return result_dict


def register_integer_programming_tools(mcp: FastMCP[Any]) -> None:
    """Register integer programming optimization tools with MCP server."""

    @mcp.tool()
    def solve_mixed_integer_program(
        variables: list[dict[str, Any]],
        constraints: list[dict[str, Any]],
        objective: dict[str, Any],
        solver_name: str = "SCIP",
        time_limit_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Solve Mixed-Integer Programming (MIP) problems with integer, binary, and continuous variables.

        Args:
            variables: List of variable definitions with bounds and types
            constraints: List of constraint definitions with coefficients and bounds
            objective: Objective function definition with coefficients and direction
            solver_name: Solver to use ("SCIP", "CBC", "GUROBI", "CPLEX")
            time_limit_seconds: Maximum solving time in seconds (default: 30.0)

        Returns:
            Optimization result with optimal variable values and objective
        """
        input_data = {
            "variables": variables,
            "constraints": constraints,
            "objective": objective,
            "solver_name": solver_name,
            "time_limit_seconds": time_limit_seconds,
        }

        result = solve_integer_program(input_data)
        result_dict: dict[str, Any] = result.model_dump()
        return result_dict
