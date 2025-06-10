"""OR-Tools solver implementation for various optimization problems."""

import logging
import time
from typing import Any

try:
    from ortools.graph.python import linear_sum_assignment
    from ortools.linear_solver import pywraplp

    ORTOOLS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"OR-Tools not available: {e}")
    linear_sum_assignment = None
    pywraplp = None
    ORTOOLS_AVAILABLE = False

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


class AdvancedConstraints:
    """Advanced constraint types for optimization problems."""

    def __init__(self) -> None:
        self.precedence_constraints: list[tuple[str, str]] = []
        self.skill_requirements: dict[str, list[str]] = {}
        self.resource_limits: dict[str, int] = {}
        self.exclusion_constraints: list[list[str]] = []
        self.grouping_constraints: list[tuple[list[str], bool]] = []

    def add_precedence_constraint(self, task_before: str, task_after: str) -> None:
        """Add precedence constraint: task_before must be completed before task_after."""
        self.precedence_constraints.append((task_before, task_after))

    def add_skill_requirement(self, task: str, required_skills: list[str]) -> None:
        """Add skill requirement for a task."""
        self.skill_requirements[task] = required_skills

    def add_resource_limit(self, resource: str, limit: int) -> None:
        """Add resource limit constraint."""
        self.resource_limits[resource] = limit

    def add_exclusion_constraint(self, tasks: list[str]) -> None:
        """Add exclusion constraint: these tasks cannot be assigned to the same worker."""
        self.exclusion_constraints.append(tasks)

    def add_grouping_constraint(self, tasks: list[str], same_worker: bool = True) -> None:
        """Add grouping constraint: these tasks must/must not be assigned to the same worker."""
        self.grouping_constraints.append((tasks, same_worker))


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
        worker_skills: dict[str, list[str]] | None = None,
        task_requirements: dict[str, list[str]] | None = None,
        advanced_constraints: AdvancedConstraints | None = None,
    ) -> dict[str, Any]:
        """Solve assignment problem using OR-Tools with advanced constraints support.

        Args:
            workers: List of worker names
            tasks: List of task names
            costs: Cost matrix (workers x tasks)
            maximize: Whether to maximize instead of minimize
            max_tasks_per_worker: Maximum tasks per worker
            min_tasks_per_worker: Minimum tasks per worker
            worker_skills: Dictionary mapping workers to their skills
            task_requirements: Dictionary mapping tasks to required skills
            advanced_constraints: Advanced constraint object

        Returns:
            Assignment optimization result
        """
        if not ORTOOLS_AVAILABLE:
            return {
                "status": "error",
                "error_message": "OR-Tools is not available. Please install it with 'pip install ortools'",
                "total_cost": None,
                "assignments": [],
                "execution_time": 0.0,
            }

        # Validate input dimensions first (outside try-catch)
        if len(costs) != len(workers):
            raise ValueError(
                f"Cost matrix rows ({len(costs)}) must match workers count ({len(workers)})"
            )

        for i, row in enumerate(costs):
            if len(row) != len(tasks):
                raise ValueError(
                    f"Cost matrix row {i} length ({len(row)}) must match tasks count ({len(tasks)})"
                )

        # Validate constraints feasibility (outside try-catch)
        self._validate_assignment_constraints(
            workers,
            tasks,
            max_tasks_per_worker,
            min_tasks_per_worker,
            worker_skills,
            task_requirements,
            advanced_constraints,
        )

        start_time = time.time()

        try:
            # For maximize problems, negate costs
            if maximize:
                costs = [[-cost for cost in row] for row in costs]

            # Use LinearSumAssignment for simple 1:1 assignment without advanced constraints
            if (
                max_tasks_per_worker is None
                and min_tasks_per_worker is None
                and worker_skills is None
                and task_requirements is None
                and advanced_constraints is None
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

                    logger.info(f"Assignment problem solved optimally in {execution_time:.3f}s")
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
                return self._solve_assignment_with_advanced_constraints(
                    workers,
                    tasks,
                    costs,
                    maximize,
                    max_tasks_per_worker,
                    min_tasks_per_worker,
                    worker_skills,
                    task_requirements,
                    advanced_constraints,
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

    def _validate_assignment_constraints(
        self,
        workers: list[str],
        tasks: list[str],
        max_tasks_per_worker: int | None,
        min_tasks_per_worker: int | None,
        worker_skills: dict[str, list[str]] | None,
        task_requirements: dict[str, list[str]] | None,
        advanced_constraints: AdvancedConstraints | None,
    ) -> None:
        """Validate assignment constraints for feasibility."""
        # Check basic capacity constraints
        if max_tasks_per_worker is not None and max_tasks_per_worker <= 0:
            if max_tasks_per_worker == 0 and len(tasks) > 0:
                raise ValueError("All workers have max_tasks_per_worker=0 but tasks exist")
            if max_tasks_per_worker < 0:
                raise ValueError("max_tasks_per_worker cannot be negative")

        if min_tasks_per_worker is not None and min_tasks_per_worker < 0:
            raise ValueError("min_tasks_per_worker cannot be negative")

        if (
            max_tasks_per_worker is not None
            and min_tasks_per_worker is not None
            and min_tasks_per_worker > max_tasks_per_worker
        ):
            raise ValueError("min_tasks_per_worker cannot exceed max_tasks_per_worker")

        # Check if enough capacity exists
        if max_tasks_per_worker is not None:
            total_capacity = len(workers) * max_tasks_per_worker
            if total_capacity < len(tasks):
                raise ValueError(
                    f"Insufficient total capacity: {total_capacity} < {len(tasks)} tasks"
                )

        # Check minimum capacity requirements
        if min_tasks_per_worker is not None:
            min_total_assignments = len(workers) * min_tasks_per_worker
            if min_total_assignments > len(tasks):
                raise ValueError(
                    f"Minimum assignments exceed available tasks: {min_total_assignments} > {len(tasks)}"
                )

        # Validate skill constraints
        if worker_skills and task_requirements:
            for task, required_skills in task_requirements.items():
                if task not in tasks:
                    raise ValueError(f"Task '{task}' in requirements not found in task list")

                # Check if at least one worker has all required skills
                capable_workers = []
                for worker in workers:
                    worker_skill_set = set(worker_skills.get(worker, []))
                    required_skill_set = set(required_skills)
                    if required_skill_set.issubset(worker_skill_set):
                        capable_workers.append(worker)

                if not capable_workers:
                    raise ValueError(
                        f"No worker has all required skills for task '{task}': {required_skills}"
                    )

        # Validate advanced constraints
        if advanced_constraints:
            # Check precedence constraints
            task_set = set(tasks)
            for task_before, task_after in advanced_constraints.precedence_constraints:
                if task_before not in task_set:
                    raise ValueError(
                        f"Precedence constraint references unknown task: {task_before}"
                    )
                if task_after not in task_set:
                    raise ValueError(f"Precedence constraint references unknown task: {task_after}")

            # Check exclusion constraints
            for excluded_tasks in advanced_constraints.exclusion_constraints:
                for task in excluded_tasks:
                    if task not in task_set:
                        raise ValueError(f"Exclusion constraint references unknown task: {task}")

    def _solve_assignment_with_advanced_constraints(
        self,
        workers: list[str],
        tasks: list[str],
        costs: list[list[float]],
        maximize: bool,
        max_tasks_per_worker: int | None,
        min_tasks_per_worker: int | None,
        worker_skills: dict[str, list[str]] | None,
        task_requirements: dict[str, list[str]] | None,
        advanced_constraints: AdvancedConstraints | None,
        start_time: float,
    ) -> dict[str, Any]:
        """Solve assignment problem with advanced constraints using linear programming."""
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

            # Constraints: each task assigned to exactly one worker
            for j in range(len(tasks)):
                constraint = solver.Constraint(1, 1)  # Changed from (0,1) to (1,1)
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

            # Skill-based constraints
            if worker_skills and task_requirements:
                for j, task in enumerate(tasks):
                    if task in task_requirements:
                        required_skills = set(task_requirements[task])
                        # Only allow assignment to workers with required skills
                        for i, worker in enumerate(workers):
                            worker_skill_set = set(worker_skills.get(worker, []))
                            if not required_skills.issubset(worker_skill_set):
                                # Force this assignment to be 0
                                constraint = solver.Constraint(0, 0)
                                constraint.SetCoefficient(x[i, j], 1)

            # Advanced constraints
            if advanced_constraints:
                # Precedence constraints (simplified: tasks must be assigned to different workers)
                for task_before, task_after in advanced_constraints.precedence_constraints:
                    try:
                        j_before = tasks.index(task_before)
                        j_after = tasks.index(task_after)

                        # If both tasks are assigned to the same worker, ensure precedence
                        for i in range(len(workers)):
                            # This is a simplification - in reality, precedence needs scheduling
                            # For now, we prevent same worker assignment
                            constraint = solver.Constraint(0, 1)
                            constraint.SetCoefficient(x[i, j_before], 1)
                            constraint.SetCoefficient(x[i, j_after], 1)
                    except ValueError:
                        continue  # Task not found, skip this constraint

                # Exclusion constraints
                for excluded_tasks in advanced_constraints.exclusion_constraints:
                    task_indices = []
                    for task in excluded_tasks:
                        try:
                            task_indices.append(tasks.index(task))
                        except ValueError:
                            continue

                    # These tasks cannot be assigned to the same worker
                    for i in range(len(workers)):
                        constraint = solver.Constraint(0, 1)
                        for j in task_indices:
                            constraint.SetCoefficient(x[i, j], 1)

                # Grouping constraints
                for grouped_tasks, same_worker in advanced_constraints.grouping_constraints:
                    task_indices = []
                    for task in grouped_tasks:
                        try:
                            task_indices.append(tasks.index(task))
                        except ValueError:
                            continue

                    if len(task_indices) < 2:
                        continue

                    if same_worker:
                        # All tasks must be assigned to the same worker
                        # Create auxiliary variable for worker selection
                        worker_vars = []
                        for i in range(len(workers)):
                            worker_var = solver.BoolVar(f"group_worker_{i}")
                            worker_vars.append(worker_var)

                            # If this worker is selected, all tasks go to this worker
                            for j in task_indices:
                                constraint = solver.Constraint(-solver.infinity(), 0)
                                constraint.SetCoefficient(x[i, j], 1)
                                constraint.SetCoefficient(worker_var, -1)

                        # Exactly one worker must be selected
                        constraint = solver.Constraint(1, 1)
                        for worker_var in worker_vars:
                            constraint.SetCoefficient(worker_var, 1)

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
                        solver_name="OR-Tools SCIP with Advanced Constraints",
                        iterations=solver.iterations(),
                        gap=None,
                    ),
                )

                logger.info(
                    f"Assignment problem with advanced constraints solved in {execution_time:.3f}s"
                )
                return result.model_dump()

            elif status == pywraplp.Solver.INFEASIBLE:
                return AssignmentResult(
                    status=OptimizationStatus.INFEASIBLE,
                    total_cost=None,
                    assignments=[],
                    execution_time=execution_time,
                    error_message="Assignment problem with constraints is infeasible",
                ).model_dump()

            elif status == pywraplp.Solver.TIME_LIMIT:
                # Extract best solution found so far
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

                return AssignmentResult(
                    status=OptimizationStatus.FEASIBLE,
                    total_cost=total_cost,
                    assignments=assignments,
                    execution_time=execution_time,
                    error_message="Time limit reached, returning best solution found",
                    solver_info=SolverInfo(
                        solver_name="OR-Tools SCIP with Advanced Constraints",
                        iterations=solver.iterations(),
                        gap=None,
                    ),
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
            logger.error(f"Error in advanced constrained assignment solver: {e}")

            return AssignmentResult(
                status=OptimizationStatus.ERROR,
                total_cost=None,
                assignments=[],
                execution_time=execution_time,
                error_message=f"Solver error: {str(e)}",
            ).model_dump()

    # Legacy method for backward compatibility
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
        """Legacy method for backward compatibility."""
        return self._solve_assignment_with_advanced_constraints(
            workers,
            tasks,
            costs,
            maximize,
            max_tasks_per_worker,
            min_tasks_per_worker,
            None,  # worker_skills
            None,  # task_requirements
            None,  # advanced_constraints
            start_time,
        )

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
        if not ORTOOLS_AVAILABLE:
            return {
                "status": "error",
                "error_message": "OR-Tools is not available. Please install it with 'pip install ortools'",
                "total_cost": None,
                "flows": [],
                "execution_time": 0.0,
            }

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

                logger.info(f"Transportation problem solved optimally in {execution_time:.3f}s")
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
