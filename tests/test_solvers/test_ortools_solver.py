"""Tests for OR-Tools solver."""

import pytest

from mcp_optimizer.schemas.base import OptimizationStatus
from mcp_optimizer.solvers.ortools_solver import AdvancedConstraints, ORToolsSolver


class TestORToolsSolver:
    """Tests for OR-Tools solver."""

    def test_simple_assignment_problem(self):
        """Test solving a simple assignment problem."""
        # 3x3 assignment problem
        workers = ["Alice", "Bob", "Charlie"]
        tasks = ["Task1", "Task2", "Task3"]
        costs = [
            [9, 2, 7],  # Alice's costs
            [6, 4, 3],  # Bob's costs
            [5, 8, 1],  # Charlie's costs
        ]

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["total_cost"] is not None
        assert result["total_cost"] > 0
        assert len(result["assignments"]) == 3
        assert result["execution_time"] > 0

        # Check that each worker is assigned exactly one task
        assigned_workers = {assignment["worker"] for assignment in result["assignments"]}
        assert assigned_workers == set(workers)

        # Check that each task is assigned to exactly one worker
        assigned_tasks = {assignment["task"] for assignment in result["assignments"]}
        assert assigned_tasks == set(tasks)

    def test_assignment_problem_maximize(self):
        """Test assignment problem with maximization."""
        workers = ["Worker1", "Worker2"]
        tasks = ["Task1", "Task2"]
        costs = [
            [10, 5],  # Worker1's values
            [8, 12],  # Worker2's values
        ]

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs, maximize=True)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["total_cost"] is not None
        assert len(result["assignments"]) == 2

        # For maximization, we expect Worker1->Task1 (10) and Worker2->Task2 (12)
        # Total value should be 22
        assert result["total_cost"] == 22

    def test_assignment_problem_with_constraints(self):
        """Test assignment problem with worker constraints."""
        workers = ["Worker1", "Worker2"]
        tasks = ["Task1", "Task2", "Task3"]
        costs = [
            [1, 2, 3],  # Worker1's costs
            [4, 5, 6],  # Worker2's costs
        ]

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs, max_tasks_per_worker=2)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["total_cost"] is not None
        assert len(result["assignments"]) <= 4  # Max 2 tasks per worker

    def test_assignment_problem_infeasible(self):
        """Test infeasible assignment problem."""
        workers = ["Worker1"]
        tasks = ["Task1", "Task2"]
        costs = [[1, 2]]

        solver = ORToolsSolver()

        # This should raise ValueError due to validation
        with pytest.raises(ValueError, match="Minimum assignments exceed available tasks"):
            solver.solve_assignment_problem(
                workers,
                tasks,
                costs,
                min_tasks_per_worker=3,  # Impossible constraint
            )

    def test_transportation_problem(self):
        """Test solving a transportation problem."""
        suppliers = [
            {"name": "Warehouse A", "supply": 100},
            {"name": "Warehouse B", "supply": 150},
        ]
        consumers = [
            {"name": "Store 1", "demand": 80},
            {"name": "Store 2", "demand": 70},
            {"name": "Store 3", "demand": 100},
        ]
        costs = [
            [4, 6, 8],  # Costs from Warehouse A
            [5, 3, 7],  # Costs from Warehouse B
        ]

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["total_cost"] is not None
        assert result["total_cost"] > 0
        assert len(result["flows"]) > 0
        assert result["execution_time"] > 0

        # Check that supply and demand are satisfied
        total_shipped = sum(flow["amount"] for flow in result["flows"])
        total_demand = sum(consumer["demand"] for consumer in consumers)
        assert abs(total_shipped - total_demand) < 1e-6

    def test_transportation_problem_unbalanced(self):
        """Test transportation problem with unbalanced supply/demand."""
        suppliers = [{"name": "Supplier", "supply": 100}]
        consumers = [{"name": "Consumer", "demand": 150}]  # More demand than supply
        costs = [[5]]

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == OptimizationStatus.INFEASIBLE.value
        assert result["error_message"] is not None

    def test_assignment_problem_invalid_dimensions(self):
        """Test assignment problem with invalid cost matrix dimensions."""
        workers = ["Worker1", "Worker2"]
        tasks = ["Task1", "Task2"]
        costs = [[1, 2, 3]]  # Wrong: 1 row for 2 workers, and 3 columns for 2 tasks

        solver = ORToolsSolver()

        # This should raise ValueError due to validation (wrong number of rows)
        with pytest.raises(ValueError, match="Cost matrix rows .* must match workers count"):
            solver.solve_assignment_problem(workers, tasks, costs)

    def test_transportation_problem_invalid_dimensions(self):
        """Test transportation problem with invalid cost matrix dimensions."""
        suppliers = [{"name": "Supplier", "supply": 100}]
        consumers = [{"name": "Consumer", "demand": 100}]
        costs = [[1, 2]]  # Wrong number of columns

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == OptimizationStatus.ERROR.value
        assert result["error_message"] is not None


class TestORToolsConstraintValidation:
    """Test constraint validation in OR-Tools solver."""

    def test_max_tasks_zero_with_tasks(self):
        """Test validation when max_tasks_per_worker=0 but tasks exist."""
        solver = ORToolsSolver()
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]
        costs = [[1, 2], [3, 4]]

        with pytest.raises(
            ValueError, match="All workers have max_tasks_per_worker=0 but tasks exist"
        ):
            solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs, max_tasks_per_worker=0
            )

    def test_max_tasks_negative(self):
        """Test validation when max_tasks_per_worker is negative."""
        solver = ORToolsSolver()
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]
        costs = [[1, 2], [3, 4]]

        with pytest.raises(ValueError, match="max_tasks_per_worker cannot be negative"):
            solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs, max_tasks_per_worker=-1
            )

    def test_min_tasks_negative(self):
        """Test validation when min_tasks_per_worker is negative."""
        solver = ORToolsSolver()
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]
        costs = [[1, 2], [3, 4]]

        with pytest.raises(ValueError, match="min_tasks_per_worker cannot be negative"):
            solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs, min_tasks_per_worker=-1
            )

    def test_advanced_constraints_skill_validation(self):
        """Test skill requirements validation with invalid skills."""
        solver = ORToolsSolver()
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]
        costs = [[1, 2], [3, 4]]

        # Worker has no required skills for task - should raise validation error
        worker_skills = {"w1": ["skill_a"], "w2": []}
        task_requirements = {"t1": ["skill_b"], "t2": ["skill_c"]}

        # This should raise a validation error because no worker can do the tasks
        with pytest.raises(ValueError, match="No worker has all required skills"):
            solver.solve_assignment_problem(
                workers=workers,
                tasks=tasks,
                costs=costs,
                worker_skills=worker_skills,
                task_requirements=task_requirements,
            )

    def test_advanced_constraints_complex_scenario(self):
        """Test complex advanced constraints scenario."""
        solver = ORToolsSolver()
        workers = ["w1", "w2", "w3"]
        tasks = ["t1", "t2", "t3"]
        costs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        # Create advanced constraints
        advanced_constraints = AdvancedConstraints()
        advanced_constraints.add_precedence_constraint("t1", "t2")
        advanced_constraints.add_skill_requirement("t1", ["skill_a"])
        advanced_constraints.add_resource_limit("resource_1", 2)
        advanced_constraints.add_exclusion_constraint(["t1", "t2"])
        advanced_constraints.add_grouping_constraint(["t2", "t3"], same_worker=True)

        worker_skills = {"w1": ["skill_a", "skill_b"], "w2": ["skill_b"], "w3": ["skill_a"]}
        task_requirements = {"t1": ["skill_a"], "t2": ["skill_b"], "t3": []}

        result = solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            worker_skills=worker_skills,
            task_requirements=task_requirements,
            advanced_constraints=advanced_constraints,
        )

        assert "status" in result


class TestORToolsTransportationEdgeCases:
    """Test edge cases for transportation problems."""

    def test_transportation_problem_infeasible_supply_demand(self):
        """Test transportation problem with infeasible supply/demand."""
        solver = ORToolsSolver()

        # Supply much less than demand
        suppliers = [{"name": "S1", "supply": 10}, {"name": "S2", "supply": 5}]
        consumers = [{"name": "C1", "demand": 100}, {"name": "C2", "demand": 200}]
        costs = [[1, 2], [3, 4]]

        result = solver.solve_transportation_problem(
            suppliers=suppliers, consumers=consumers, costs=costs
        )

        # Should handle infeasible case gracefully
        assert "status" in result

    def test_transportation_problem_zero_supply(self):
        """Test transportation problem with zero supply."""
        solver = ORToolsSolver()

        suppliers = [{"name": "S1", "supply": 0}, {"name": "S2", "supply": 0}]
        consumers = [{"name": "C1", "demand": 10}, {"name": "C2", "demand": 20}]
        costs = [[1, 2], [3, 4]]

        result = solver.solve_transportation_problem(
            suppliers=suppliers, consumers=consumers, costs=costs
        )

        assert "status" in result

    def test_transportation_problem_large_values(self):
        """Test transportation problem with large cost values."""
        solver = ORToolsSolver()

        suppliers = [{"name": "S1", "supply": 100}, {"name": "S2", "supply": 200}]
        consumers = [{"name": "C1", "demand": 150}, {"name": "C2", "demand": 150}]
        # Very large costs
        costs = [[1e6, 2e6], [3e6, 4e6]]

        result = solver.solve_transportation_problem(
            suppliers=suppliers, consumers=consumers, costs=costs
        )

        assert "status" in result


class TestORToolsAdvancedConstraints:
    """Test AdvancedConstraints class methods."""

    def test_advanced_constraints_init(self):
        """Test AdvancedConstraints initialization."""
        constraints = AdvancedConstraints()

        assert constraints.precedence_constraints == []
        assert constraints.skill_requirements == {}
        assert constraints.resource_limits == {}
        assert constraints.exclusion_constraints == []
        assert constraints.grouping_constraints == []

    def test_add_precedence_constraint(self):
        """Test adding precedence constraints."""
        constraints = AdvancedConstraints()
        constraints.add_precedence_constraint("task1", "task2")
        constraints.add_precedence_constraint("task2", "task3")

        assert len(constraints.precedence_constraints) == 2
        assert ("task1", "task2") in constraints.precedence_constraints
        assert ("task2", "task3") in constraints.precedence_constraints

    def test_add_skill_requirement(self):
        """Test adding skill requirements."""
        constraints = AdvancedConstraints()
        constraints.add_skill_requirement("task1", ["skill_a", "skill_b"])
        constraints.add_skill_requirement("task2", ["skill_c"])

        assert constraints.skill_requirements["task1"] == ["skill_a", "skill_b"]
        assert constraints.skill_requirements["task2"] == ["skill_c"]

    def test_add_resource_limit(self):
        """Test adding resource limits."""
        constraints = AdvancedConstraints()
        constraints.add_resource_limit("cpu", 4)
        constraints.add_resource_limit("memory", 8)

        assert constraints.resource_limits["cpu"] == 4
        assert constraints.resource_limits["memory"] == 8

    def test_add_exclusion_constraint(self):
        """Test adding exclusion constraints."""
        constraints = AdvancedConstraints()
        constraints.add_exclusion_constraint(["task1", "task2"])
        constraints.add_exclusion_constraint(["task3", "task4", "task5"])

        assert len(constraints.exclusion_constraints) == 2
        assert ["task1", "task2"] in constraints.exclusion_constraints
        assert ["task3", "task4", "task5"] in constraints.exclusion_constraints

    def test_add_grouping_constraint(self):
        """Test adding grouping constraints."""
        constraints = AdvancedConstraints()
        constraints.add_grouping_constraint(["task1", "task2"], same_worker=True)
        constraints.add_grouping_constraint(["task3", "task4"], same_worker=False)

        assert len(constraints.grouping_constraints) == 2
        assert (["task1", "task2"], True) in constraints.grouping_constraints
        assert (["task3", "task4"], False) in constraints.grouping_constraints

    def test_add_grouping_constraint_default(self):
        """Test adding grouping constraints with default same_worker=True."""
        constraints = AdvancedConstraints()
        constraints.add_grouping_constraint(["task1", "task2"])  # default same_worker=True

        assert len(constraints.grouping_constraints) == 1
        assert (["task1", "task2"], True) in constraints.grouping_constraints


class TestORToolsErrorHandling:
    """Test error handling in OR-Tools solver."""

    def test_assignment_problem_solver_error(self):
        """Test assignment problem when solver encounters an error."""
        solver = ORToolsSolver()
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]

        # Invalid costs that might cause solver error
        costs = [[float("inf"), float("nan")], [float("-inf"), 1e20]]

        result = solver.solve_assignment_problem(workers=workers, tasks=tasks, costs=costs)

        # Should handle error gracefully
        assert "status" in result
        if result["status"] == "error":
            assert "error_message" in result

    def test_transportation_problem_invalid_costs(self):
        """Test transportation problem with invalid cost values."""
        solver = ORToolsSolver()

        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1", "demand": 100}]

        # Invalid costs
        costs = [[float("nan")]]

        result = solver.solve_transportation_problem(
            suppliers=suppliers, consumers=consumers, costs=costs
        )

        assert "status" in result
