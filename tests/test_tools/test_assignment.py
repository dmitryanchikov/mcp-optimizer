"""Tests for assignment tools."""

import pytest

from mcp_optimizer.solvers.ortools_solver import ORToolsSolver
from mcp_optimizer.tools.assignment import register_assignment_tools
from fastmcp import FastMCP


class TestAssignmentTools:
    """Tests for assignment tools."""

    def test_solve_assignment_problem_success(self):
        """Test successful assignment problem solving."""
        workers = ["Alice", "Bob", "Charlie"]
        tasks = ["Task1", "Task2", "Task3"]
        costs = [
            [9, 2, 7],  # Alice's costs
            [6, 4, 3],  # Bob's costs
            [5, 8, 1],  # Charlie's costs
        ]

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs)

        assert result["status"] == "optimal"
        assert result["total_cost"] is not None
        assert result["total_cost"] > 0
        assert len(result["assignments"]) == 3
        assert result["execution_time"] > 0

        # Verify assignments structure
        for assignment in result["assignments"]:
            assert "worker" in assignment
            assert "task" in assignment
            assert "cost" in assignment
            assert assignment["worker"] in workers
            assert assignment["task"] in tasks

    def test_solve_assignment_problem_maximize(self):
        """Test assignment problem with maximization."""
        workers = ["Worker1", "Worker2"]
        tasks = ["Task1", "Task2"]
        costs = [
            [10, 5],  # Worker1's values
            [8, 12],  # Worker2's values
        ]

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs, maximize=True)

        assert result["status"] == "optimal"
        assert result["total_cost"] == 22  # 10 + 12

    def test_solve_assignment_problem_with_constraints(self):
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

        assert result["status"] == "optimal"
        assert len(result["assignments"]) <= 4  # Max 2 tasks per worker

    def test_solve_assignment_problem_empty_workers(self):
        """Test assignment problem with empty workers list."""
        workers = []
        tasks = ["Task1"]
        costs = []

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs)

        # Empty workers should result in optimal solution with no assignments
        assert result["status"] == "optimal"
        assert result["total_cost"] == 0
        assert len(result["assignments"]) == 0

    def test_solve_assignment_problem_empty_tasks(self):
        """Test assignment problem with empty tasks list."""
        workers = ["Worker1"]
        tasks = []
        costs = [[]]

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs)

        # Empty tasks should result in optimal solution with no assignments
        assert result["status"] == "optimal"
        assert result["total_cost"] == 0
        assert len(result["assignments"]) == 0

    def test_solve_assignment_problem_invalid_cost_matrix(self):
        """Test assignment problem with invalid cost matrix."""
        workers = ["Worker1", "Worker2"]
        tasks = ["Task1", "Task2"]
        costs = [[1, 2, 3]]  # Wrong dimensions

        solver = ORToolsSolver()
        result = solver.solve_assignment_problem(workers, tasks, costs)

        assert result["status"] == "error"
        assert "cost matrix" in result["error_message"].lower()

    def test_solve_transportation_problem_success(self):
        """Test successful transportation problem solving."""
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

        assert result["status"] == "optimal"
        assert result["total_cost"] is not None
        assert result["total_cost"] > 0
        assert len(result["flows"]) > 0
        assert result["execution_time"] > 0

        # Verify flows structure
        for flow in result["flows"]:
            assert "supplier" in flow
            assert "consumer" in flow
            assert "amount" in flow
            assert "cost" in flow
            assert flow["amount"] > 0

    def test_solve_transportation_problem_unbalanced(self):
        """Test transportation problem with unbalanced supply/demand."""
        suppliers = [{"name": "Supplier", "supply": 100}]
        consumers = [{"name": "Consumer", "demand": 150}]
        costs = [[5]]

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        # Unbalanced problem should be infeasible
        assert result["status"] == "infeasible"
        assert result["error_message"] is not None

    def test_solve_transportation_problem_empty_suppliers(self):
        """Test transportation problem with empty suppliers."""
        suppliers = []
        consumers = [{"name": "Consumer", "demand": 100}]
        costs = []

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        # Empty suppliers with demand should be infeasible
        assert result["status"] == "infeasible"
        assert result["error_message"] is not None

    def test_solve_transportation_problem_invalid_supplier_format(self):
        """Test transportation problem with invalid supplier format."""
        suppliers = [{"name": "Supplier"}]  # Missing supply
        consumers = [{"name": "Consumer", "demand": 100}]
        costs = [[5]]

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "supply" in result["error_message"].lower()

    def test_solve_transportation_problem_invalid_consumer_format(self):
        """Test transportation problem with invalid consumer format."""
        suppliers = [{"name": "Supplier", "supply": 100}]
        consumers = [{"name": "Consumer"}]  # Missing demand
        costs = [[5]]

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "demand" in result["error_message"].lower()

    def test_solve_transportation_problem_invalid_cost_matrix(self):
        """Test transportation problem with invalid cost matrix."""
        suppliers = [{"name": "Supplier", "supply": 100}]
        consumers = [{"name": "Consumer", "demand": 100}]
        costs = [[1, 2]]  # Wrong dimensions

        solver = ORToolsSolver()
        result = solver.solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "cost matrix" in result["error_message"].lower()


class TestAssignmentToolsValidation:
    """Tests for assignment tools input validation."""

    @pytest.fixture
    def mcp_server(self):
        """Create MCP server with assignment tools."""
        mcp = FastMCP("test-server")
        register_assignment_tools(mcp)
        return mcp

    async def test_assignment_tool_empty_workers_validation(self, mcp_server):
        """Test assignment tool validation with empty workers."""
        result = await mcp_server.call_tool("solve_assignment_problem", {
            "workers": [],
            "tasks": ["Task1"],
            "costs": []
        })

        assert result["status"] == "error"
        assert "workers" in result["error_message"].lower()

    async def test_assignment_tool_empty_tasks_validation(self, mcp_server):
        """Test assignment tool validation with empty tasks."""
        result = await mcp_server.call_tool("solve_assignment_problem", {
            "workers": ["Worker1"],
            "tasks": [],
            "costs": [[]]
        })

        assert result["status"] == "error"
        assert "tasks" in result["error_message"].lower()

    async def test_transportation_tool_empty_suppliers_validation(self, mcp_server):
        """Test transportation tool validation with empty suppliers."""
        result = await mcp_server.call_tool("solve_transportation_problem", {
            "suppliers": [],
            "consumers": [{"name": "Consumer", "demand": 100}],
            "costs": []
        })

        assert result["status"] == "error"
        assert "suppliers" in result["error_message"].lower()

    async def test_transportation_tool_unbalanced_validation(self, mcp_server):
        """Test transportation tool validation with unbalanced supply/demand."""
        result = await mcp_server.call_tool("solve_transportation_problem", {
            "suppliers": [{"name": "Supplier", "supply": 100}],
            "consumers": [{"name": "Consumer", "demand": 150}],
            "costs": [[5]]
        })

        assert result["status"] == "error"
        assert "supply" in result["error_message"].lower()
        assert "demand" in result["error_message"].lower() 