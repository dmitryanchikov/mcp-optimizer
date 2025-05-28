"""PuLP solver implementation for linear programming problems."""

import logging
import time
from typing import Any

import pulp

from mcp_optimizer.config import SolverType, settings
from mcp_optimizer.schemas.base import (
    BaseOptimizationResult,
    Constraint,
    Objective,
    OptimizationStatus,
    SolverInfo,
    Variable,
)

logger = logging.getLogger(__name__)


class PuLPSolver:
    """Solver for linear programming problems using PuLP."""

    def __init__(self, solver_name: str | None = None):
        """Initialize PuLP solver.

        Args:
            solver_name: Name of the solver to use (CBC, GLPK, GUROBI, CPLEX)
        """
        self.solver_name = solver_name or settings.default_solver.value
        self._solver = self._get_solver()

    def _get_solver(self) -> pulp.LpSolver:
        """Get PuLP solver instance."""
        solver_map = {
            SolverType.CBC.value: pulp.PULP_CBC_CMD,
            SolverType.GLPK.value: pulp.GLPK_CMD,
            SolverType.GUROBI.value: pulp.GUROBI_CMD,
            SolverType.CPLEX.value: pulp.CPLEX_CMD,
        }

        solver_class = solver_map.get(self.solver_name, pulp.PULP_CBC_CMD)

        try:
            return solver_class(
                timeLimit=settings.max_solve_time,
                msg=settings.debug,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize {self.solver_name}: {e}")
            logger.info("Falling back to CBC solver")
            return pulp.PULP_CBC_CMD(
                timeLimit=settings.max_solve_time,
                msg=settings.debug,
            )

    def solve_linear_program(
        self,
        objective: Objective,
        variables: dict[str, Variable],
        constraints: list[Constraint],
        time_limit: float | None = None,
    ) -> dict[str, Any]:
        """Solve linear programming problem.

        Args:
            objective: Objective function
            variables: Variable definitions
            constraints: Problem constraints
            time_limit: Time limit in seconds

        Returns:
            Optimization result
        """
        start_time = time.time()

        try:
            # Create problem
            sense = pulp.LpMaximize if objective.sense.value == "maximize" else pulp.LpMinimize
            problem = pulp.LpProblem("LinearProgram", sense)

            # Create variables
            pulp_vars = {}
            for var_name, var_def in variables.items():
                if var_def.type.value == "binary":
                    pulp_vars[var_name] = pulp.LpVariable(
                        var_name,
                        cat=pulp.LpBinary,
                    )
                elif var_def.type.value == "integer":
                    pulp_vars[var_name] = pulp.LpVariable(
                        var_name,
                        lowBound=var_def.lower,
                        upBound=var_def.upper,
                        cat=pulp.LpInteger,
                    )
                else:  # continuous
                    pulp_vars[var_name] = pulp.LpVariable(
                        var_name,
                        lowBound=var_def.lower,
                        upBound=var_def.upper,
                        cat=pulp.LpContinuous,
                    )

            # Set objective
            obj_expr = pulp.lpSum(
                [
                    coeff * pulp_vars[var_name]
                    for var_name, coeff in objective.coefficients.items()
                    if var_name in pulp_vars
                ]
            )
            problem += obj_expr

            # Add constraints
            for i, constraint in enumerate(constraints):
                constraint_expr = pulp.lpSum(
                    [
                        coeff * pulp_vars[var_name]
                        for var_name, coeff in constraint.expression.items()
                        if var_name in pulp_vars
                    ]
                )

                constraint_name = constraint.name or f"constraint_{i}"

                if constraint.operator.value == "<=":
                    problem += constraint_expr <= constraint.rhs, constraint_name
                elif constraint.operator.value == ">=":
                    problem += constraint_expr >= constraint.rhs, constraint_name
                else:  # ==
                    problem += constraint_expr == constraint.rhs, constraint_name

            # Update solver time limit if provided
            if time_limit:
                self._solver.timeLimit = min(time_limit, settings.max_solve_time)

            # Solve problem
            logger.info(f"Solving linear program with {self.solver_name}")
            status = problem.solve(self._solver)

            execution_time = time.time() - start_time

            # Parse results
            if status == pulp.LpStatusOptimal:
                opt_status = OptimizationStatus.OPTIMAL
                objective_value = pulp.value(problem.objective)
                variable_values = {
                    var_name: var.varValue
                    for var_name, var in pulp_vars.items()
                    if var.varValue is not None
                }
                error_message = None
            elif status == pulp.LpStatusInfeasible:
                opt_status = OptimizationStatus.INFEASIBLE
                objective_value = None
                variable_values = {}
                error_message = "Problem is infeasible"
            elif status == pulp.LpStatusUnbounded:
                opt_status = OptimizationStatus.UNBOUNDED
                objective_value = None
                variable_values = {}
                error_message = "Problem is unbounded"
            elif status == pulp.LpStatusNotSolved:
                opt_status = OptimizationStatus.ERROR
                objective_value = None
                variable_values = {}
                error_message = "Problem was not solved"
            else:
                opt_status = OptimizationStatus.ERROR
                objective_value = None
                variable_values = {}
                error_message = f"Solver returned status: {pulp.LpStatus[status]}"

            # Create solver info
            solver_info = SolverInfo(
                solver_name=self.solver_name,
                iterations=None,  # PuLP doesn't expose iteration count
                gap=None,  # PuLP doesn't expose optimality gap
            )

            result = BaseOptimizationResult(
                status=opt_status,
                objective_value=objective_value,
                execution_time=execution_time,
                error_message=error_message,
            )

            # Add variable values and solver info to result
            result_dict = result.model_dump()
            result_dict["variables"] = variable_values
            result_dict["solver_info"] = solver_info.model_dump()

            logger.info(f"Solved in {execution_time:.3f}s with status: {opt_status.value}")
            return result_dict

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error solving linear program: {e}")

            return BaseOptimizationResult(
                status=OptimizationStatus.ERROR,
                objective_value=None,
                execution_time=execution_time,
                error_message=f"Solver error: {str(e)}",
            ).model_dump()
