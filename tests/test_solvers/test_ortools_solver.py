"""Tests for OR-Tools solver."""

import pytest

from mcp_optimizer.schemas.base import OptimizationStatus
from mcp_optimizer.solvers.ortools_solver import ORToolsSolver


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
        result = solver.solve_assignment_problem(
            workers, tasks, costs, maximize=True
        )

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
        result = solver.solve_assignment_problem(
            workers, tasks, costs, max_tasks_per_worker=2
        )

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["total_cost"] is not None
        assert len(result["assignments"]) <= 4  # Max 2 tasks per worker

    def test_assignment_problem_infeasible(self):
        """Test infeasible assignment problem."""
        workers = ["Worker1"]
        tasks = ["Task1", "Task2"]
        costs = [[1, 2]]

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(
            workers, tasks, costs, min_tasks_per_worker=3  # Impossible constraint
        )

        assert result["status"] == OptimizationStatus.INFEASIBLE.value
        assert result["total_cost"] is None
        assert result["error_message"] is not None

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
        costs = [[1, 2, 3]]  # Wrong number of columns

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs)

        assert result["status"] == OptimizationStatus.ERROR.value
        assert result["error_message"] is not None

    def test_transportation_problem_invalid_dimensions(self):
        """Test transportation problem with invalid cost matrix dimensions."""
        suppliers = [{"name": "Supplier", "supply": 100}]
        consumers = [{"name": "Consumer", "demand": 100}]
        costs = [[1, 2]]  # Wrong number of columns

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == OptimizationStatus.ERROR.value
        assert result["error_message"] is not None 