"""OR-Tools solver implementation for various optimization problems."""

import logging
import time
from typing import Any

from ortools.graph.python import linear_sum_assignment
from ortools.linear_solver import pywraplp

from mcp_optimizer.config import settings
from mcp_optimizer.schemas.base import (
    OptimizationStatus,
    SolverInfo,
)
from mcp_optimizer.schemas.problem_schemas import (
    Assignment,
    AssignmentResult,
    TransportationFlow,
    TransportationResult,
)

logger = logging.getLogger(__name__)


class ORToolsSolver:
    """Solver for various optimization problems using OR-Tools."""

    def __init__(self) -> None:
        """Initialize OR-Tools solver."""
        self.solver_name = "OR-Tools"

    def solve_assignment_problem(
        self,
        workers: list[str],
        tasks: list[str],
        costs: list[list[float]],
        maximize: bool = False,
        max_tasks_per_worker: int | None = None,
        min_tasks_per_worker: int | None = None,
    ) -> dict[str, Any]:
        """Solve assignment problem using OR-Tools LinearSumAssignment.

        Args:
            workers: List of worker names
            tasks: List of task names
            costs: Cost matrix (workers x tasks)
            maximize: Whether to maximize instead of minimize
            max_tasks_per_worker: Maximum tasks per worker
            min_tasks_per_worker: Minimum tasks per worker

        Returns:
            Assignment optimization result
        """
        start_time = time.time()

        try:
            # Validate input dimensions
            if len(costs) != len(workers):
                raise ValueError(
                    f"Cost matrix rows ({len(costs)}) must match workers count ({len(workers)})"
                )

            for i, row in enumerate(costs):
                if len(row) != len(tasks):
                    raise ValueError(
                        f"Cost matrix row {i} length ({len(row)}) must match tasks count ({len(tasks)})"
                    )

            # For maximize problems, negate costs
            if maximize:
                costs = [[-cost for cost in row] for row in costs]

            # Use LinearSumAssignment for simple 1:1 assignment
            if (
                max_tasks_per_worker is None
                and min_tasks_per_worker is None
                and len(workers) == len(tasks)
            ):
                assignment = linear_sum_assignment.SimpleLinearSumAssignment()

                # Add costs
                for worker_idx in range(len(workers)):
                    for task_idx in range(len(tasks)):
                        assignment.add_arc_with_cost(
                            worker_idx,
                            task_idx,
                            int(costs[worker_idx][task_idx] * 1000),
                        )

                # Solve
                status = assignment.solve()

                execution_time = time.time() - start_time

                if status == assignment.OPTIMAL:
                    # Extract solution
                    assignments = []
                    total_cost = 0.0

                    for worker_idx in range(assignment.num_nodes()):
                        if assignment.right_mate(worker_idx) >= 0:
                            task_idx = assignment.right_mate(worker_idx)
                            original_cost = (
                                -costs[worker_idx][task_idx]
                                if maximize
                                else costs[worker_idx][task_idx]
                            )
                            assignments.append(
                                Assignment(
                                    worker=workers[worker_idx],
                                    task=tasks[task_idx],
                                    cost=original_cost,
                                )
                            )
                            total_cost += original_cost

                    result = AssignmentResult(
                        status=OptimizationStatus.OPTIMAL,
                        total_cost=total_cost,
                        assignments=assignments,
                        execution_time=execution_time,
                        solver_info=SolverInfo(
                            solver_name="OR-Tools LinearSumAssignment",
                            iterations=None,
                            gap=None,
                        ),
                    )

                    logger.info(
                        f"Assignment problem solved optimally in {execution_time:.3f}s"
                    )
                    return result.model_dump()

                else:
                    return AssignmentResult(
                        status=OptimizationStatus.INFEASIBLE,
                        total_cost=None,
                        assignments=[],
                        execution_time=execution_time,
                        error_message="Assignment problem is infeasible",
                    ).model_dump()

            else:
                # Use linear programming for complex constraints
                return self._solve_assignment_with_constraints(
                    workers,
                    tasks,
                    costs,
                    maximize,
                    max_tasks_per_worker,
                    min_tasks_per_worker,
                    start_time,
                )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error solving assignment problem: {e}")

            return AssignmentResult(
                status=OptimizationStatus.ERROR,
                total_cost=None,
                assignments=[],
                execution_time=execution_time,
                error_message=f"Solver error: {str(e)}",
            ).model_dump()

    def _solve_assignment_with_constraints(
        self,
        workers: list[str],
        tasks: list[str],
        costs: list[list[float]],
        maximize: bool,
        max_tasks_per_worker: int | None,
        min_tasks_per_worker: int | None,
        start_time: float,
    ) -> dict[str, Any]:
        """Solve assignment problem with additional constraints using linear programming."""
        try:
            # Create linear programming solver
            solver = pywraplp.Solver.CreateSolver("SCIP")
            if not solver:
                raise RuntimeError("Could not create OR-Tools linear solver")

            # Create binary variables for each worker-task pair
            x = {}
            for i, worker in enumerate(workers):
                for j, task in enumerate(tasks):
                    x[i, j] = solver.BoolVar(f"x_{worker}_{task}")

            # Objective function
            objective = solver.Objective()
            for i in range(len(workers)):
                for j in range(len(tasks)):
                    coeff = -costs[i][j] if maximize else costs[i][j]
                    objective.SetCoefficient(x[i, j], coeff)

            if maximize:
                objective.SetMaximization()
            else:
                objective.SetMinimization()

            # Constraints: each task assigned to at most one worker
            for j in range(len(tasks)):
                constraint = solver.Constraint(0, 1)
                for i in range(len(workers)):
                    constraint.SetCoefficient(x[i, j], 1)

            # Worker capacity constraints
            for i in range(len(workers)):
                if max_tasks_per_worker is not None:
                    constraint = solver.Constraint(0, max_tasks_per_worker)
                    for j in range(len(tasks)):
                        constraint.SetCoefficient(x[i, j], 1)

                if min_tasks_per_worker is not None:
                    constraint = solver.Constraint(min_tasks_per_worker, len(tasks))
                    for j in range(len(tasks)):
                        constraint.SetCoefficient(x[i, j], 1)

            # Set time limit
            solver.SetTimeLimit(int(settings.max_solve_time * 1000))

            # Solve
            status = solver.Solve()

            execution_time = time.time() - start_time

            if status == pywraplp.Solver.OPTIMAL:
                # Extract solution
                assignments = []
                total_cost = 0.0

                for i in range(len(workers)):
                    for j in range(len(tasks)):
                        if x[i, j].solution_value() > 0.5:
                            original_cost = -costs[i][j] if maximize else costs[i][j]
                            assignments.append(
                                Assignment(
                                    worker=workers[i],
                                    task=tasks[j],
                                    cost=original_cost,
                                )
                            )
                            total_cost += original_cost

                result = AssignmentResult(
                    status=OptimizationStatus.OPTIMAL,
                    total_cost=total_cost,
                    assignments=assignments,
                    execution_time=execution_time,
                    solver_info=SolverInfo(
                        solver_name="OR-Tools SCIP",
                        iterations=solver.iterations(),
                        gap=None,
                    ),
                )

                logger.info(
                    f"Assignment problem with constraints solved in {execution_time:.3f}s"
                )
                return result.model_dump()

            elif status == pywraplp.Solver.INFEASIBLE:
                return AssignmentResult(
                    status=OptimizationStatus.INFEASIBLE,
                    total_cost=None,
                    assignments=[],
                    execution_time=execution_time,
                    error_message="Assignment problem is infeasible",
                ).model_dump()

            else:
                return AssignmentResult(
                    status=OptimizationStatus.ERROR,
                    total_cost=None,
                    assignments=[],
                    execution_time=execution_time,
                    error_message=f"Solver returned status: {status}",
                ).model_dump()

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in constrained assignment solver: {e}")

            return AssignmentResult(
                status=OptimizationStatus.ERROR,
                total_cost=None,
                assignments=[],
                execution_time=execution_time,
                error_message=f"Solver error: {str(e)}",
            ).model_dump()

    def solve_transportation_problem(
        self,
        suppliers: list[dict[str, Any]],
        consumers: list[dict[str, Any]],
        costs: list[list[float]],
    ) -> dict[str, Any]:
        """Solve transportation problem using OR-Tools linear programming.

        Args:
            suppliers: List of suppliers with supply amounts
            consumers: List of consumers with demand amounts
            costs: Transportation cost matrix (suppliers x consumers)

        Returns:
            Transportation optimization result
        """
        start_time = time.time()

        try:
            # Validate input
            if len(costs) != len(suppliers):
                raise ValueError(
                    f"Cost matrix rows ({len(costs)}) must match suppliers count ({len(suppliers)})"
                )

            for i, row in enumerate(costs):
                if len(row) != len(consumers):
                    raise ValueError(
                        f"Cost matrix row {i} length ({len(row)}) must match consumers count ({len(consumers)})"
                    )

            # Create linear programming solver
            solver = pywraplp.Solver.CreateSolver("SCIP")
            if not solver:
                raise RuntimeError("Could not create OR-Tools linear solver")

            # Create variables for transportation amounts
            x = {}
            for i in range(len(suppliers)):
                for j in range(len(consumers)):
                    x[i, j] = solver.NumVar(
                        0,
                        solver.infinity(),
                        f"x_{suppliers[i]['name']}_{consumers[j]['name']}",
                    )

            # Objective: minimize total transportation cost
            objective = solver.Objective()
            for i in range(len(suppliers)):
                for j in range(len(consumers)):
                    objective.SetCoefficient(x[i, j], costs[i][j])
            objective.SetMinimization()

            # Supply constraints
            for i, supplier in enumerate(suppliers):
                constraint = solver.Constraint(0, supplier["supply"])
                for j in range(len(consumers)):
                    constraint.SetCoefficient(x[i, j], 1)

            # Demand constraints
            for j, consumer in enumerate(consumers):
                constraint = solver.Constraint(consumer["demand"], consumer["demand"])
                for i in range(len(suppliers)):
                    constraint.SetCoefficient(x[i, j], 1)

            # Set time limit
            solver.SetTimeLimit(int(settings.max_solve_time * 1000))

            # Solve
            status = solver.Solve()

            execution_time = time.time() - start_time

            if status == pywraplp.Solver.OPTIMAL:
                # Extract solution
                flows = []
                total_cost = 0.0

                for i in range(len(suppliers)):
                    for j in range(len(consumers)):
                        amount = x[i, j].solution_value()
                        if amount > 1e-6:  # Only include non-zero flows
                            flow_cost = amount * costs[i][j]
                            flows.append(
                                TransportationFlow(
                                    supplier=suppliers[i]["name"],
                                    consumer=consumers[j]["name"],
                                    amount=amount,
                                    cost=flow_cost,
                                )
                            )
                            total_cost += flow_cost

                result = TransportationResult(
                    status=OptimizationStatus.OPTIMAL,
                    total_cost=total_cost,
                    flows=flows,
                    execution_time=execution_time,
                    solver_info=SolverInfo(
                        solver_name="OR-Tools SCIP",
                        iterations=solver.iterations(),
                        gap=None,
                    ),
                )

                logger.info(
                    f"Transportation problem solved optimally in {execution_time:.3f}s"
                )
                return result.model_dump()

            elif status == pywraplp.Solver.INFEASIBLE:
                return TransportationResult(
                    status=OptimizationStatus.INFEASIBLE,
                    total_cost=None,
                    flows=[],
                    execution_time=execution_time,
                    error_message="Transportation problem is infeasible",
                ).model_dump()

            else:
                return TransportationResult(
                    status=OptimizationStatus.ERROR,
                    total_cost=None,
                    flows=[],
                    execution_time=execution_time,
                    error_message=f"Solver returned status: {status}",
                ).model_dump()

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error solving transportation problem: {e}")

            return TransportationResult(
                status=OptimizationStatus.ERROR,
                total_cost=None,
                flows=[],
                execution_time=execution_time,
                error_message=f"Solver error: {str(e)}",
            ).model_dump()
