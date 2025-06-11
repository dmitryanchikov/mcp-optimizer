"""Tests for scheduling optimization tools."""

from unittest.mock import Mock

import pytest

from mcp_optimizer.schemas.base import OptimizationStatus
from mcp_optimizer.tools.scheduling import (
    EmployeeConstraints,
    Job,
    JobSchedulingInput,
    Shift,
    ShiftSchedulingInput,
    Task,
    register_scheduling_tools,
    solve_job_scheduling,
    solve_shift_scheduling,
)


class TestTask:
    """Test Task model."""

    def test_valid_task(self):
        """Test creating a valid task."""
        task = Task(machine=0, duration=5, setup_time=2)
        assert task.machine == 0
        assert task.duration == 5
        assert task.setup_time == 2

    def test_task_defaults(self):
        """Test task with default values."""
        task = Task(machine=1, duration=3)
        assert task.setup_time == 0

    def test_negative_values(self):
        """Test task with negative values."""
        with pytest.raises(ValueError):
            Task(machine=-1, duration=5)

        with pytest.raises(ValueError):
            Task(machine=0, duration=-1)

        with pytest.raises(ValueError):
            Task(machine=0, duration=5, setup_time=-1)


class TestJob:
    """Test Job model."""

    def test_valid_job(self):
        """Test creating a valid job."""
        tasks = [
            Task(machine=0, duration=5),
            Task(machine=1, duration=3),
        ]
        job = Job(
            id="job1",
            tasks=tasks,
            priority=2,
            deadline=20,
            release_time=5,
        )
        assert job.id == "job1"
        assert len(job.tasks) == 2
        assert job.priority == 2
        assert job.deadline == 20
        assert job.release_time == 5

    def test_job_defaults(self):
        """Test job with default values."""
        tasks = [Task(machine=0, duration=5)]
        job = Job(id="job1", tasks=tasks)
        assert job.priority == 1
        assert job.deadline is None
        assert job.release_time == 0

    def test_empty_tasks(self):
        """Test job with empty tasks."""
        with pytest.raises(ValueError, match="Job must have at least one task"):
            Job(id="job1", tasks=[])

    def test_negative_values(self):
        """Test job with negative values."""
        tasks = [Task(machine=0, duration=5)]

        with pytest.raises(ValueError):
            Job(id="job1", tasks=tasks, priority=0)

        with pytest.raises(ValueError):
            Job(id="job1", tasks=tasks, deadline=-1)

        with pytest.raises(ValueError):
            Job(id="job1", tasks=tasks, release_time=-1)


class TestJobSchedulingInput:
    """Test JobSchedulingInput model."""

    def test_valid_job_scheduling_input(self):
        """Test creating valid job scheduling input."""
        jobs = [
            Job(id="job1", tasks=[Task(machine=0, duration=5)]),
            Job(id="job2", tasks=[Task(machine=1, duration=3)]),
        ]
        machines = ["machine1", "machine2"]

        input_data = JobSchedulingInput(
            jobs=jobs,
            machines=machines,
            horizon=100,
            objective="makespan",
            time_limit_seconds=60.0,
        )

        assert len(input_data.jobs) == 2
        assert len(input_data.machines) == 2
        assert input_data.horizon == 100
        assert input_data.objective == "makespan"
        assert input_data.time_limit_seconds == 60.0

    def test_job_scheduling_input_defaults(self):
        """Test job scheduling input with default values."""
        jobs = [Job(id="job1", tasks=[Task(machine=0, duration=5)])]
        machines = ["machine1"]

        input_data = JobSchedulingInput(jobs=jobs, machines=machines, horizon=50)
        assert input_data.objective == "makespan"
        assert input_data.time_limit_seconds == 30.0

    def test_empty_jobs(self):
        """Test job scheduling input with empty jobs."""
        with pytest.raises(ValueError, match="Must have at least one job"):
            JobSchedulingInput(jobs=[], machines=["machine1"], horizon=50)

    def test_empty_machines(self):
        """Test job scheduling input with empty machines."""
        jobs = [Job(id="job1", tasks=[Task(machine=0, duration=5)])]
        with pytest.raises(ValueError, match="Must have at least one machine"):
            JobSchedulingInput(jobs=jobs, machines=[], horizon=50)

    def test_invalid_objective(self):
        """Test job scheduling input with invalid objective."""
        jobs = [Job(id="job1", tasks=[Task(machine=0, duration=5)])]
        machines = ["machine1"]

        with pytest.raises(ValueError):
            JobSchedulingInput(
                jobs=jobs, machines=machines, horizon=50, objective="invalid_objective"
            )

    def test_negative_horizon(self):
        """Test job scheduling input with negative horizon."""
        jobs = [Job(id="job1", tasks=[Task(machine=0, duration=5)])]
        machines = ["machine1"]

        with pytest.raises(ValueError):
            JobSchedulingInput(jobs=jobs, machines=machines, horizon=0)


class TestShift:
    """Test Shift model."""

    def test_valid_shift(self):
        """Test creating a valid shift."""
        shift = Shift(
            name="morning",
            start=8,
            end=16,
            required_staff=3,
            skills_required=["customer_service", "cash_handling"],
        )
        assert shift.name == "morning"
        assert shift.start == 8
        assert shift.end == 16
        assert shift.required_staff == 3
        assert shift.skills_required == ["customer_service", "cash_handling"]

    def test_shift_defaults(self):
        """Test shift with default values."""
        shift = Shift(name="evening", start=16, end=24, required_staff=2)
        assert shift.skills_required == []

    def test_invalid_end_time(self):
        """Test shift with invalid end time."""
        with pytest.raises(ValueError, match="End time must be after start time"):
            Shift(name="invalid", start=16, end=8, required_staff=2)

        with pytest.raises(ValueError, match="End time must be after start time"):
            Shift(name="invalid", start=16, end=16, required_staff=2)

    def test_negative_values(self):
        """Test shift with negative values."""
        with pytest.raises(ValueError):
            Shift(name="test", start=-1, end=8, required_staff=2)

        with pytest.raises(ValueError):
            Shift(name="test", start=8, end=-1, required_staff=2)

        with pytest.raises(ValueError):
            Shift(name="test", start=8, end=16, required_staff=0)


class TestEmployeeConstraints:
    """Test EmployeeConstraints model."""

    def test_valid_employee_constraints(self):
        """Test creating valid employee constraints."""
        constraints = EmployeeConstraints(
            max_shifts_per_week=5,
            min_shifts_per_week=2,
            unavailable_shifts=["night"],
            preferred_shifts=["morning", "afternoon"],
            skills=["customer_service"],
            max_consecutive_shifts=3,
        )
        assert constraints.max_shifts_per_week == 5
        assert constraints.min_shifts_per_week == 2
        assert constraints.unavailable_shifts == ["night"]
        assert constraints.preferred_shifts == ["morning", "afternoon"]
        assert constraints.skills == ["customer_service"]
        assert constraints.max_consecutive_shifts == 3

    def test_employee_constraints_defaults(self):
        """Test employee constraints with default values."""
        constraints = EmployeeConstraints()
        assert constraints.max_shifts_per_week is None
        assert constraints.min_shifts_per_week is None
        assert constraints.unavailable_shifts == []
        assert constraints.preferred_shifts == []
        assert constraints.skills == []
        assert constraints.max_consecutive_shifts is None

    def test_negative_values(self):
        """Test employee constraints with negative values."""
        with pytest.raises(ValueError):
            EmployeeConstraints(max_shifts_per_week=-1)

        with pytest.raises(ValueError):
            EmployeeConstraints(min_shifts_per_week=-1)

        with pytest.raises(ValueError):
            EmployeeConstraints(max_consecutive_shifts=0)


class TestShiftSchedulingInput:
    """Test ShiftSchedulingInput model."""

    def test_valid_shift_scheduling_input(self):
        """Test creating valid shift scheduling input."""
        employees = ["Alice", "Bob", "Charlie"]
        shifts = [
            Shift(name="morning", start=8, end=16, required_staff=2),
            Shift(name="evening", start=16, end=24, required_staff=1),
        ]
        employee_constraints = {
            "Alice": EmployeeConstraints(max_shifts_per_week=4),
            "Bob": EmployeeConstraints(unavailable_shifts=["night"]),
        }

        input_data = ShiftSchedulingInput(
            employees=employees,
            shifts=shifts,
            days=7,
            employee_constraints=employee_constraints,
            time_limit_seconds=60.0,
        )

        assert len(input_data.employees) == 3
        assert len(input_data.shifts) == 2
        assert input_data.days == 7
        assert len(input_data.employee_constraints) == 2
        assert input_data.time_limit_seconds == 60.0

    def test_shift_scheduling_input_defaults(self):
        """Test shift scheduling input with default values."""
        employees = ["Alice"]
        shifts = [Shift(name="morning", start=8, end=16, required_staff=1)]

        input_data = ShiftSchedulingInput(employees=employees, shifts=shifts, days=5)
        assert input_data.employee_constraints == {}
        assert input_data.time_limit_seconds == 30.0

    def test_empty_employees(self):
        """Test shift scheduling input with empty employees."""
        shifts = [Shift(name="morning", start=8, end=16, required_staff=1)]
        with pytest.raises(ValueError, match="Must have at least one employee"):
            ShiftSchedulingInput(employees=[], shifts=shifts, days=7)

    def test_empty_shifts(self):
        """Test shift scheduling input with empty shifts."""
        employees = ["Alice"]
        with pytest.raises(ValueError, match="Must have at least one shift"):
            ShiftSchedulingInput(employees=employees, shifts=[], days=7)

    def test_negative_days(self):
        """Test shift scheduling input with negative days."""
        employees = ["Alice"]
        shifts = [Shift(name="morning", start=8, end=16, required_staff=1)]

        with pytest.raises(ValueError):
            ShiftSchedulingInput(employees=employees, shifts=shifts, days=0)


class TestJobScheduling:
    """Test Job Scheduling functions."""

    def test_simple_job_scheduling(self):
        """Test simple job scheduling problem."""
        input_data = {
            "jobs": [
                {
                    "id": "job1",
                    "tasks": [
                        {"machine": 0, "duration": 3},
                        {"machine": 1, "duration": 2},
                    ],
                },
                {
                    "id": "job2",
                    "tasks": [
                        {"machine": 1, "duration": 2},
                        {"machine": 0, "duration": 4},
                    ],
                },
            ],
            "machines": ["machine1", "machine2"],
            "horizon": 20,
            "objective": "makespan",
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert "schedule" in result.variables
        assert result.objective_value is not None

    def test_job_scheduling_with_setup_time(self):
        """Test job scheduling with setup times."""
        input_data = {
            "jobs": [
                {
                    "id": "job1",
                    "tasks": [
                        {"machine": 0, "duration": 3, "setup_time": 1},
                        {"machine": 1, "duration": 2, "setup_time": 1},
                    ],
                },
            ],
            "machines": ["machine1", "machine2"],
            "horizon": 20,
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_job_scheduling_with_release_time(self):
        """Test job scheduling with release times."""
        input_data = {
            "jobs": [
                {
                    "id": "job1",
                    "tasks": [{"machine": 0, "duration": 3}],
                    "release_time": 5,
                },
            ],
            "machines": ["machine1"],
            "horizon": 20,
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_job_scheduling_with_deadline(self):
        """Test job scheduling with deadlines."""
        input_data = {
            "jobs": [
                {
                    "id": "job1",
                    "tasks": [{"machine": 0, "duration": 3}],
                    "deadline": 10,
                },
            ],
            "machines": ["machine1"],
            "horizon": 20,
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_job_scheduling_total_completion_time(self):
        """Test job scheduling with total completion time objective."""
        input_data = {
            "jobs": [
                {
                    "id": "job1",
                    "tasks": [{"machine": 0, "duration": 3}],
                },
                {
                    "id": "job2",
                    "tasks": [{"machine": 0, "duration": 2}],
                },
            ],
            "machines": ["machine1"],
            "horizon": 20,
            "objective": "total_completion_time",
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_job_scheduling_infeasible(self):
        """Test infeasible job scheduling problem."""
        input_data = {
            "jobs": [
                {
                    "id": "job1",
                    "tasks": [{"machine": 0, "duration": 15}],
                    "deadline": 5,  # Impossible deadline
                },
            ],
            "machines": ["machine1"],
            "horizon": 10,
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.INFEASIBLE

    def test_job_scheduling_invalid_input(self):
        """Test job scheduling with invalid input."""
        result = solve_job_scheduling(
            {
                "jobs": [],
                "machines": ["machine1"],
                "horizon": 20,
            }
        )
        assert result.status == OptimizationStatus.ERROR
        assert "at least one job" in result.error_message


class TestShiftScheduling:
    """Test Shift Scheduling functions."""

    def test_simple_shift_scheduling(self):
        """Test simple shift scheduling problem."""
        input_data = {
            "employees": ["Alice", "Bob", "Charlie"],
            "shifts": [
                {"name": "morning", "start": 8, "end": 16, "required_staff": 2},
                {"name": "evening", "start": 16, "end": 24, "required_staff": 1},
            ],
            "days": 3,
        }

        result = solve_shift_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert "schedule" in result.variables

    def test_shift_scheduling_with_constraints(self):
        """Test shift scheduling with employee constraints."""
        input_data = {
            "employees": ["Alice", "Bob"],
            "shifts": [
                {"name": "morning", "start": 8, "end": 16, "required_staff": 1},
                {"name": "evening", "start": 16, "end": 24, "required_staff": 1},
            ],
            "days": 5,
            "employee_constraints": {
                "Alice": {
                    "max_shifts_per_week": 3,
                    "unavailable_shifts": ["evening"],
                },
                "Bob": {
                    "min_shifts_per_week": 2,
                    "preferred_shifts": ["evening"],
                },
            },
        }

        result = solve_shift_scheduling(input_data)
        assert result.status in [OptimizationStatus.OPTIMAL, OptimizationStatus.INFEASIBLE]

    def test_shift_scheduling_with_skills(self):
        """Test shift scheduling with skill requirements."""
        input_data = {
            "employees": ["Alice", "Bob"],
            "shifts": [
                {
                    "name": "management",
                    "start": 8,
                    "end": 16,
                    "required_staff": 1,
                    "skills_required": ["management"],
                },
            ],
            "days": 3,
            "employee_constraints": {
                "Alice": {"skills": ["management"]},
                "Bob": {"skills": ["customer_service"]},
            },
        }

        result = solve_shift_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_shift_scheduling_consecutive_shifts(self):
        """Test shift scheduling with consecutive shift limits."""
        input_data = {
            "employees": ["Alice"],
            "shifts": [
                {"name": "shift1", "start": 8, "end": 16, "required_staff": 1},
            ],
            "days": 5,
            "employee_constraints": {
                "Alice": {"max_consecutive_shifts": 2},
            },
        }

        result = solve_shift_scheduling(input_data)
        assert result.status in [OptimizationStatus.OPTIMAL, OptimizationStatus.INFEASIBLE]

    def test_shift_scheduling_infeasible(self):
        """Test infeasible shift scheduling problem."""
        input_data = {
            "employees": ["Alice"],
            "shifts": [
                {"name": "morning", "start": 8, "end": 16, "required_staff": 2},  # Need 2 staff
            ],
            "days": 1,
        }

        result = solve_shift_scheduling(input_data)
        assert result.status == OptimizationStatus.INFEASIBLE

    def test_shift_scheduling_invalid_input(self):
        """Test shift scheduling with invalid input."""
        result = solve_shift_scheduling(
            {
                "employees": [],
                "shifts": [{"name": "morning", "start": 8, "end": 16, "required_staff": 1}],
                "days": 7,
            }
        )
        assert result.status == OptimizationStatus.ERROR
        assert "at least one employee" in result.error_message


class TestRegisterSchedulingTools:
    """Test MCP tool registration."""

    def test_register_scheduling_tools(self):
        """Test registering scheduling tools with MCP."""
        mcp_mock = Mock()
        mcp_mock.tool.return_value = lambda func: func  # Mock decorator

        register_scheduling_tools(mcp_mock)

        # Verify that mcp.tool() was called
        mcp_mock.tool.assert_called()

    def test_job_shop_scheduling_tool(self):
        """Test the job shop scheduling MCP tool wrapper with real solving."""
        mcp_mock = Mock()
        tool_functions = []

        def mock_tool_decorator():
            def decorator(func):
                tool_functions.append(func)
                return func

            return decorator

        mcp_mock.tool = mock_tool_decorator

        register_scheduling_tools(mcp_mock)

        # Get the first registered tool function (job scheduling)
        assert len(tool_functions) >= 1
        tool_func = tool_functions[0]

        # Test the tool function with real problem
        jobs = [{"id": "job1", "tasks": [{"machine": 0, "duration": 5}]}]
        machines = ["machine1"]

        result = tool_func(jobs=jobs, machines=machines, horizon=20)

        # Verify real solving occurred
        assert result["status"] == "optimal"
        assert "variables" in result
        assert "execution_time" in result

    def test_shift_scheduling_tool(self):
        """Test the shift scheduling MCP tool wrapper with real solving."""
        mcp_mock = Mock()
        tool_functions = []

        def mock_tool_decorator():
            def decorator(func):
                tool_functions.append(func)
                return func

            return decorator

        mcp_mock.tool = mock_tool_decorator

        register_scheduling_tools(mcp_mock)

        # Get the second registered tool function (shift scheduling)
        assert len(tool_functions) >= 2
        tool_func = tool_functions[1]

        # Test the tool function with real problem
        employees = ["Alice", "Bob"]
        shifts = [{"name": "morning", "start": 8, "end": 16, "required_staff": 1}]

        result = tool_func(employees=employees, shifts=shifts, days=5)

        # Verify real solving occurred
        assert result["status"] == "optimal"
        assert "variables" in result
        assert "execution_time" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_single_job_single_machine(self):
        """Test scheduling with single job and machine."""
        input_data = {
            "jobs": [
                {"id": "job1", "tasks": [{"machine": 0, "duration": 5}]},
            ],
            "machines": ["machine1"],
            "horizon": 20,
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_single_employee_single_shift(self):
        """Test shift scheduling with single employee and shift."""
        input_data = {
            "employees": ["Alice"],
            "shifts": [{"name": "morning", "start": 8, "end": 16, "required_staff": 1}],
            "days": 1,
        }

        result = solve_shift_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_zero_duration_task(self):
        """Test job scheduling with zero duration task."""
        input_data = {
            "jobs": [
                {"id": "job1", "tasks": [{"machine": 0, "duration": 0}]},
            ],
            "machines": ["machine1"],
            "horizon": 20,
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_high_priority_job(self):
        """Test job scheduling with high priority job."""
        input_data = {
            "jobs": [
                {
                    "id": "job1",
                    "tasks": [{"machine": 0, "duration": 5}],
                    "priority": 10,
                },
                {
                    "id": "job2",
                    "tasks": [{"machine": 0, "duration": 3}],
                    "priority": 1,
                },
            ],
            "machines": ["machine1"],
            "horizon": 20,
        }

        result = solve_job_scheduling(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
