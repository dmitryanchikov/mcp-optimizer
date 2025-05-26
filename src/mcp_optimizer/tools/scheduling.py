"""Scheduling optimization tools for MCP server.

This module provides tools for solving scheduling problems including:
- Job Shop Scheduling
- Shift Scheduling
"""

import time
from typing import Any

from fastmcp import FastMCP
from ortools.sat.python import cp_model
from pydantic import BaseModel, Field, validator

from ..schemas.base import OptimizationResult, OptimizationStatus


class Task(BaseModel):
    """Task in a job with machine and duration requirements."""

    machine: int = Field(ge=0)
    duration: int = Field(ge=0)
    setup_time: int = Field(default=0, ge=0)


class Job(BaseModel):
    """Job with sequence of tasks."""

    id: str
    tasks: list[Task]
    priority: int = Field(default=1, ge=1)
    deadline: int | None = Field(default=None, ge=0)
    release_time: int = Field(default=0, ge=0)

    @validator("tasks")
    def validate_tasks(cls, v: list[Task]) -> list[Task]:
        if not v:
            raise ValueError("Job must have at least one task")
        return v


class JobSchedulingInput(BaseModel):
    """Input schema for Job Shop Scheduling."""

    jobs: list[Job]
    machines: list[str]
    horizon: int = Field(ge=1)
    objective: str = Field(
        default="makespan", pattern="^(makespan|total_completion_time)$"
    )
    time_limit_seconds: float = Field(default=30.0, ge=0)

    @validator("jobs")
    def validate_jobs(cls, v: list[Job]) -> list[Job]:
        if not v:
            raise ValueError("At least one job required")
        return v

    @validator("machines")
    def validate_machines(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one machine required")
        return v


class Shift(BaseModel):
    """Shift definition with time and requirements."""

    name: str
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    required_staff: int = Field(ge=1)
    skills_required: list[str] = Field(default_factory=list)

    @validator("end")
    def validate_end_time(cls, v: int, values: dict[str, Any]) -> int:
        if "start" in values and v <= values["start"]:
            raise ValueError("Shift end time must be after start time")
        return v


class EmployeeConstraints(BaseModel):
    """Employee constraints and preferences."""

    max_shifts_per_week: int | None = Field(default=None, ge=0)
    min_shifts_per_week: int | None = Field(default=None, ge=0)
    unavailable_shifts: list[str] = Field(default_factory=list)
    preferred_shifts: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    max_consecutive_shifts: int | None = Field(default=None, ge=1)


class ShiftSchedulingInput(BaseModel):
    """Input schema for Shift Scheduling."""

    employees: list[str]
    shifts: list[Shift]
    days: int = Field(ge=1)
    employee_constraints: dict[str, EmployeeConstraints] = Field(default_factory=dict)
    time_limit_seconds: float = Field(default=30.0, ge=0)

    @validator("employees")
    def validate_employees(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one employee required")
        return v

    @validator("shifts")
    def validate_shifts(cls, v: list[Shift]) -> list[Shift]:
        if not v:
            raise ValueError("At least one shift required")
        return v


def solve_job_scheduling(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Job Shop Scheduling Problem using OR-Tools CP-SAT.

    Args:
        input_data: Job scheduling problem specification

    Returns:
        OptimizationResult with schedule and makespan
    """
    start_time = time.time()

    try:
        # Parse and validate input
        scheduling_input = JobSchedulingInput(**input_data)
        jobs = scheduling_input.jobs
        machines = scheduling_input.machines
        horizon = scheduling_input.horizon

        # Create CP-SAT model
        model = cp_model.CpModel()

        # Variables
        task_vars = {}  # (job_id, task_idx) -> (start_var, end_var, interval_var)
        machine_intervals: dict[int, list[Any]] = {
            machine_idx: [] for machine_idx in range(len(machines))
        }

        # Create variables for each task
        for job in jobs:
            for task_idx, task in enumerate(job.tasks):
                start_var = model.NewIntVar(
                    job.release_time, horizon, f"start_{job.id}_{task_idx}"
                )
                duration = task.duration + task.setup_time
                end_var = model.NewIntVar(
                    job.release_time, horizon, f"end_{job.id}_{task_idx}"
                )
                interval_var = model.NewIntervalVar(
                    start_var, duration, end_var, f"interval_{job.id}_{task_idx}"
                )

                task_vars[(job.id, task_idx)] = (start_var, end_var, interval_var)
                machine_intervals[task.machine].append(interval_var)

        # Precedence constraints within jobs
        for job in jobs:
            for task_idx in range(len(job.tasks) - 1):
                current_end = task_vars[(job.id, task_idx)][1]
                next_start = task_vars[(job.id, task_idx + 1)][0]
                model.Add(current_end <= next_start)

        # Machine capacity constraints (no overlap)
        for _machine_idx, intervals in machine_intervals.items():
            if intervals:
                model.AddNoOverlap(intervals)

        # Deadline constraints
        for job in jobs:
            if job.deadline is not None:
                last_task_idx = len(job.tasks) - 1
                last_task_end = task_vars[(job.id, last_task_idx)][1]
                model.Add(last_task_end <= job.deadline)

        # Objective
        if scheduling_input.objective == "makespan":
            # Minimize makespan (maximum completion time)
            makespan = model.NewIntVar(0, horizon, "makespan")
            for job in jobs:
                last_task_idx = len(job.tasks) - 1
                last_task_end = task_vars[(job.id, last_task_idx)][1]
                model.AddMaxEquality(makespan, [last_task_end])
            model.Minimize(makespan)
        else:  # total_completion_time
            # Minimize total completion time
            completion_times = []
            for job in jobs:
                last_task_idx = len(job.tasks) - 1
                last_task_end = task_vars[(job.id, last_task_idx)][1]
                completion_times.append(last_task_end * job.priority)
            model.Minimize(sum(completion_times))

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = scheduling_input.time_limit_seconds
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            schedule = []
            job_completion_times = {}

            for job in jobs:
                job_schedule = []
                for task_idx, task in enumerate(job.tasks):
                    start_var, end_var, _ = task_vars[(job.id, task_idx)]
                    start_time_val = solver.Value(start_var)
                    end_time_val = solver.Value(end_var)

                    job_schedule.append(
                        {
                            "task_index": task_idx,
                            "machine": machines[task.machine],
                            "machine_index": task.machine,
                            "start_time": start_time_val,
                            "end_time": end_time_val,
                            "duration": task.duration,
                            "setup_time": task.setup_time,
                        }
                    )

                completion_time = max(task["end_time"] for task in job_schedule)  # type: ignore
                job_completion_times[job.id] = completion_time

                schedule.append(
                    {
                        "job_id": job.id,
                        "tasks": job_schedule,
                        "completion_time": completion_time,
                        "priority": job.priority,
                    }
                )

            makespan = max(job_completion_times.values()) if job_completion_times else 0  # type: ignore
            total_completion_time = sum(job_completion_times.values())  # type: ignore

            execution_time = time.time() - start_time

            return OptimizationResult(
                status=OptimizationStatus.OPTIMAL
                if status == cp_model.OPTIMAL
                else OptimizationStatus.FEASIBLE,
                objective_value=float(
                    makespan  # type: ignore
                    if scheduling_input.objective == "makespan"
                    else total_completion_time
                ),
                variables={
                    "schedule": schedule,
                    "makespan": makespan,
                    "total_completion_time": total_completion_time,
                    "job_completion_times": job_completion_times,
                    "num_jobs": len(jobs),
                    "num_machines": len(machines),
                },
                execution_time=execution_time,
                solver_info={
                    "solver_name": "OR-Tools CP-SAT",
                    "status": solver.StatusName(status),
                    "objective": scheduling_input.objective,
                },
            )
        else:
            status_name = solver.StatusName(status)
            return OptimizationResult(
                status=OptimizationStatus.INFEASIBLE
                if status == cp_model.INFEASIBLE
                else OptimizationStatus.ERROR,
                error_message=f"No solution found: {status_name}",
                execution_time=time.time() - start_time,
            )

    except Exception as e:
        return OptimizationResult(
            status=OptimizationStatus.ERROR,
            error_message=f"Job scheduling error: {str(e)}",
            execution_time=time.time() - start_time,
        )


def solve_shift_scheduling(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Shift Scheduling Problem using OR-Tools CP-SAT.

    Args:
        input_data: Shift scheduling problem specification

    Returns:
        OptimizationResult with employee shift assignments
    """
    start_time = time.time()

    try:
        # Parse and validate input
        scheduling_input = ShiftSchedulingInput(**input_data)
        employees = scheduling_input.employees
        shifts = scheduling_input.shifts
        days = scheduling_input.days
        employee_constraints = scheduling_input.employee_constraints

        # Create CP-SAT model
        model = cp_model.CpModel()

        # Variables: assignment[employee][shift][day] = 1 if employee works shift on day
        assignments: dict[int, dict[int, dict[int, Any]]] = {}
        for emp_idx, employee in enumerate(employees):
            assignments[emp_idx] = {}
            for shift_idx, shift in enumerate(shifts):
                assignments[emp_idx][shift_idx] = {}
                for day in range(days):
                    var_name = f"assign_{employee}_{shift.name}_{day}"
                    assignments[emp_idx][shift_idx][day] = model.NewBoolVar(var_name)

        # Constraint: Each shift must have required staff each day
        for shift_idx, shift in enumerate(shifts):
            for day in range(days):
                model.Add(
                    sum(
                        assignments[emp_idx][shift_idx][day]
                        for emp_idx in range(len(employees))
                    )
                    >= shift.required_staff
                )

        # Employee constraints
        for emp_idx, employee in enumerate(employees):
            emp_constraints = employee_constraints.get(employee, EmployeeConstraints())

            # Max/min shifts per week
            if emp_constraints.max_shifts_per_week is not None:
                total_shifts = sum(
                    assignments[emp_idx][shift_idx][day]
                    for shift_idx in range(len(shifts))
                    for day in range(days)
                )
                model.Add(total_shifts <= emp_constraints.max_shifts_per_week)

            if emp_constraints.min_shifts_per_week is not None:
                total_shifts = sum(
                    assignments[emp_idx][shift_idx][day]
                    for shift_idx in range(len(shifts))
                    for day in range(days)
                )
                model.Add(total_shifts >= emp_constraints.min_shifts_per_week)

            # Unavailable shifts
            for shift_name in emp_constraints.unavailable_shifts:
                for shift_idx, shift in enumerate(shifts):
                    if shift.name == shift_name:
                        for day in range(days):
                            model.Add(assignments[emp_idx][shift_idx][day] == 0)

            # Skills requirements
            for shift_idx, shift in enumerate(shifts):
                if shift.skills_required:
                    has_required_skills = all(
                        skill in emp_constraints.skills
                        for skill in shift.skills_required
                    )
                    if not has_required_skills:
                        for day in range(days):
                            model.Add(assignments[emp_idx][shift_idx][day] == 0)

            # No overlapping shifts on same day
            for day in range(days):
                overlapping_shifts = []
                for shift_idx, _shift in enumerate(shifts):
                    overlapping_shifts.append(assignments[emp_idx][shift_idx][day])
                model.Add(sum(overlapping_shifts) <= 1)

            # Max consecutive shifts
            if emp_constraints.max_consecutive_shifts is not None:
                for start_day in range(days - emp_constraints.max_consecutive_shifts):
                    consecutive_vars = []
                    for day in range(
                        start_day,
                        start_day + emp_constraints.max_consecutive_shifts + 1,
                    ):
                        day_working = model.NewBoolVar(f"working_{employee}_{day}")
                        model.Add(
                            day_working
                            == sum(
                                assignments[emp_idx][shift_idx][day]
                                for shift_idx in range(len(shifts))
                            )
                        )
                        consecutive_vars.append(day_working)
                    model.Add(
                        sum(consecutive_vars) <= emp_constraints.max_consecutive_shifts
                    )

        # Objective: Minimize total assignments (prefer fewer shifts) and maximize preferences
        total_assignments = sum(
            assignments[emp_idx][shift_idx][day]
            for emp_idx in range(len(employees))
            for shift_idx in range(len(shifts))
            for day in range(days)
        )

        preference_score = 0
        for emp_idx, employee in enumerate(employees):
            emp_constraints = employee_constraints.get(employee, EmployeeConstraints())
            for shift_name in emp_constraints.preferred_shifts:
                for shift_idx, shift in enumerate(shifts):
                    if shift.name == shift_name:
                        preference_score += sum(
                            assignments[emp_idx][shift_idx][day] for day in range(days)
                        )

        # Minimize total assignments while maximizing preferences
        model.Minimize(total_assignments - preference_score)

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = scheduling_input.time_limit_seconds
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            schedule = []
            employee_stats = {}

            for emp_idx, employee in enumerate(employees):
                employee_schedule = []
                total_shifts = 0

                for day in range(days):
                    day_assignments = []
                    for shift_idx, shift in enumerate(shifts):
                        if solver.Value(assignments[emp_idx][shift_idx][day]):
                            day_assignments.append(
                                {
                                    "shift_name": shift.name,
                                    "start_time": shift.start,
                                    "end_time": shift.end,
                                    "skills_required": shift.skills_required,
                                }
                            )
                            total_shifts += 1

                    employee_schedule.append({"day": day, "shifts": day_assignments})

                employee_stats[employee] = {
                    "total_shifts": total_shifts,
                    "schedule": employee_schedule,
                }

                schedule.append(
                    {
                        "employee": employee,
                        "total_shifts": total_shifts,
                        "daily_schedule": employee_schedule,
                    }
                )

            # Calculate coverage statistics
            coverage_stats = []
            for day in range(days):
                day_coverage = []
                for shift_idx, shift in enumerate(shifts):
                    assigned_count = sum(
                        int(solver.Value(assignments[emp_idx][shift_idx][day]))
                        for emp_idx in range(len(employees))
                    )
                    day_coverage.append(
                        {
                            "shift_name": shift.name,
                            "required_staff": shift.required_staff,
                            "assigned_staff": assigned_count,
                            "coverage_ratio": assigned_count / shift.required_staff
                            if shift.required_staff > 0
                            else 1.0,
                        }
                    )
                coverage_stats.append({"day": day, "shifts": day_coverage})

            execution_time = time.time() - start_time

            return OptimizationResult(
                status=OptimizationStatus.OPTIMAL
                if status == cp_model.OPTIMAL
                else OptimizationStatus.FEASIBLE,
                objective_value=float(solver.ObjectiveValue()),
                variables={
                    "schedule": schedule,
                    "employee_stats": employee_stats,
                    "coverage_stats": coverage_stats,
                    "total_assignments": sum(
                        emp["total_shifts"] for emp in employee_stats.values()
                    ),
                    "num_employees": len(employees),
                    "num_shifts": len(shifts),
                    "num_days": days,
                },
                execution_time=execution_time,
                solver_info={
                    "solver_name": "OR-Tools CP-SAT",
                    "status": solver.StatusName(status),
                },
            )
        else:
            status_name = solver.StatusName(status)
            return OptimizationResult(
                status=OptimizationStatus.INFEASIBLE
                if status == cp_model.INFEASIBLE
                else OptimizationStatus.ERROR,
                error_message=f"No solution found: {status_name}",
                execution_time=time.time() - start_time,
            )

    except Exception as e:
        return OptimizationResult(
            status=OptimizationStatus.ERROR,
            error_message=f"Shift scheduling error: {str(e)}",
            execution_time=time.time() - start_time,
        )


def register_scheduling_tools(mcp: FastMCP[Any]) -> None:
    """Register scheduling optimization tools with MCP server."""

    @mcp.tool()
    def solve_job_shop_scheduling(
        jobs: list[dict[str, Any]],
        machines: list[str],
        horizon: int,
        objective: str = "makespan",
        time_limit_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Solve Job Shop Scheduling Problem to optimize machine utilization and completion times.

        Args:
            jobs: List of job dictionaries with tasks and constraints
            machines: List of available machine names
            horizon: Maximum time horizon for scheduling
            objective: Optimization objective ("makespan" or "total_completion_time")
            time_limit_seconds: Maximum solving time in seconds (default: 30.0)

        Returns:
            Optimization result with job schedule and machine assignments
        """
        input_data = {
            "jobs": jobs,
            "machines": machines,
            "horizon": horizon,
            "objective": objective,
            "time_limit_seconds": time_limit_seconds,
        }

        result = solve_job_scheduling(input_data)
        return result.model_dump()

    @mcp.tool()
    def solve_employee_shift_scheduling(
        employees: list[str],
        shifts: list[dict[str, Any]],
        days: int,
        employee_constraints: dict[str, dict[str, Any]] | None = None,
        time_limit_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Solve Employee Shift Scheduling to assign employees to shifts optimally.

        Args:
            employees: List of employee names
            shifts: List of shift dictionaries with time and requirements
            days: Number of days to schedule
            employee_constraints: Optional constraints and preferences per employee
            time_limit_seconds: Maximum solving time in seconds (default: 30.0)

        Returns:
            Optimization result with employee schedules and coverage statistics
        """
        input_data = {
            "employees": employees,
            "shifts": shifts,
            "days": days,
            "employee_constraints": employee_constraints or {},
            "time_limit_seconds": time_limit_seconds,
        }

        result = solve_shift_scheduling(input_data)
        return result.model_dump()
