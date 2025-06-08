"""Tests for assignment tools."""

from unittest.mock import MagicMock

from mcp_optimizer.tools.assignment import (
    register_assignment_tools,
    solve_assignment_problem,
    solve_transportation_problem,
)


class TestAssignmentTools:
    """Tests for assignment problem solving tools."""

    def test_solve_assignment_problem_success(self):
        """Test successful assignment problem solving."""
        workers = ["Alice", "Bob", "Charlie"]
        tasks = ["Task1", "Task2", "Task3"]
        costs = [[4, 6, 3], [2, 5, 1], [3, 4, 2]]

        result = solve_assignment_problem(workers, tasks, costs)

        assert "status" in result
        assert "total_cost" in result
        assert "assignments" in result
        assert "execution_time" in result

    def test_solve_assignment_problem_maximize(self):
        """Test assignment problem with maximize objective."""
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2"]
        costs = [[10, 5], [8, 12]]

        result = solve_assignment_problem(workers, tasks, costs, objective="maximize")

        assert "status" in result
        assert result["objective"] == "maximize"

    def test_solve_assignment_problem_with_constraints(self):
        """Test assignment problem with additional constraints."""
        workers = ["Alice", "Bob", "Charlie"]
        tasks = ["Task1", "Task2", "Task3"]
        costs = [[4, 6, 3], [2, 5, 1], [3, 4, 2]]
        constraints = {"worker_limits": {"Alice": 1, "Bob": 2}, "task_requirements": {"Task1": 1}}

        result = solve_assignment_problem(workers, tasks, costs, constraints=constraints)

        assert "status" in result

    def test_solve_assignment_problem_empty_workers(self):
        """Test assignment problem with empty workers list."""
        result = solve_assignment_problem([], ["Task1"], [[]])

        assert result["status"] == "error"
        assert "No workers provided" in result["error_message"]

    def test_solve_assignment_problem_empty_tasks(self):
        """Test assignment problem with empty tasks list."""
        result = solve_assignment_problem(["Alice"], [], [[]])

        assert result["status"] == "error"
        assert "No tasks provided" in result["error_message"]

    def test_solve_assignment_problem_invalid_cost_matrix(self):
        """Test assignment problem with invalid cost matrix dimensions."""
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2"]
        costs = [[4, 6]]  # Missing row for Bob

        result = solve_assignment_problem(workers, tasks, costs)

        assert result["status"] == "error"
        assert "Cost matrix dimensions" in result["error_message"]

    def test_solve_assignment_problem_unbalanced(self):
        """Test assignment problem with unbalanced workers and tasks."""
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2", "Task3"]
        costs = [[4, 6, 3], [2, 5, 1]]

        result = solve_assignment_problem(workers, tasks, costs)

        assert "status" in result
        # Should handle unbalanced assignment

    def test_solve_assignment_problem_infeasible_constraints(self):
        """Test assignment problem with worker limits constraint."""
        workers = ["Alice"]
        tasks = ["Task1", "Task2"]
        costs = [[4, 6]]
        constraints = {
            "worker_limits": {"Alice": 0}  # Alice can't be assigned to any task
        }

        result = solve_assignment_problem(workers, tasks, costs, constraints=constraints)

        # With max_tasks_per_worker=0, the problem should be infeasible
        assert result["status"] == "infeasible"

    def test_solve_assignment_problem_exception_handling(self):
        """Test assignment problem with invalid input causing real error."""
        # Test with invalid cost matrix - non-numeric values should cause error
        workers = ["Alice"]
        tasks = ["Task1"]
        costs = [["invalid"]]  # String instead of number

        result = solve_assignment_problem(workers, tasks, costs)

        assert result["status"] == "error"
        assert "error_message" in result

    def test_solve_transportation_problem_success(self):
        """Test successful transportation problem solving."""
        suppliers = [{"name": "S1", "supply": 100}, {"name": "S2", "supply": 150}]
        consumers = [{"name": "C1", "demand": 80}, {"name": "C2", "demand": 170}]
        costs = [[5, 10], [8, 6]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert "status" in result
        assert "total_cost" in result
        assert "shipments" in result
        assert "execution_time" in result

    def test_solve_transportation_problem_unbalanced(self):
        """Test transportation problem with unbalanced supply and demand."""
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1", "demand": 80}, {"name": "C2", "demand": 50}]
        costs = [[5, 10]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert "status" in result
        # Should handle unbalanced transportation

    def test_solve_transportation_problem_empty_suppliers(self):
        """Test transportation problem with empty suppliers."""
        result = solve_transportation_problem([], [{"name": "C1", "demand": 80}], [[]])

        assert result["status"] == "error"
        assert "No suppliers provided" in result["error_message"]

    def test_solve_transportation_problem_empty_consumers(self):
        """Test transportation problem with empty consumers."""
        result = solve_transportation_problem([{"name": "S1", "supply": 100}], [], [[]])

        assert result["status"] == "error"
        assert "No consumers provided" in result["error_message"]

    def test_solve_transportation_problem_invalid_supplier_format(self):
        """Test transportation problem with invalid supplier format."""
        suppliers = ["invalid_supplier"]
        consumers = [{"name": "C1", "demand": 80}]
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert (
            "Supplier" in result["error_message"]
            and "must be a dictionary" in result["error_message"]
        )

    def test_solve_transportation_problem_invalid_consumer_format(self):
        """Test transportation problem with invalid consumer format."""
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = ["invalid_consumer"]
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert (
            "Consumer" in result["error_message"]
            and "must be a dictionary" in result["error_message"]
        )

    def test_solve_transportation_problem_invalid_cost_matrix(self):
        """Test transportation problem with invalid cost matrix."""
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1", "demand": 80}]
        costs = []  # Empty cost matrix

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "Cost matrix dimensions" in result["error_message"]

    def test_solve_transportation_problem_missing_supplier_fields(self):
        """Test transportation problem with missing supplier fields."""
        suppliers = [{"name": "S1"}]  # Missing supply
        consumers = [{"name": "C1", "demand": 80}]
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "supply" in result["error_message"]

    def test_solve_transportation_problem_missing_consumer_fields(self):
        """Test transportation problem with missing consumer fields."""
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1"}]  # Missing demand
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "demand" in result["error_message"]

    def test_solve_transportation_problem_negative_supply(self):
        """Test transportation problem with negative supply."""
        suppliers = [{"name": "S1", "supply": -100}]
        consumers = [{"name": "C1", "demand": 80}]
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "Supply must be non-negative" in result["error_message"]

    def test_solve_transportation_problem_negative_demand(self):
        """Test transportation problem with negative demand."""
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1", "demand": -80}]
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "Demand must be non-negative" in result["error_message"]

    def test_solve_transportation_problem_exception_handling(self):
        """Test transportation problem with invalid input causing real error."""
        # Test with invalid cost matrix - non-numeric values should cause error
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1", "demand": 100}]
        costs = [["invalid"]]  # String instead of number

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert result["status"] == "error"
        assert "error_message" in result


class TestAssignmentToolsValidation:
    """Tests for assignment tools validation."""

    def test_assignment_tool_empty_workers_validation(self):
        """Test assignment tool validation with empty workers."""
        result = solve_assignment_problem([], ["Task1"], [[]])
        assert result["status"] == "error"

    def test_assignment_tool_empty_tasks_validation(self):
        """Test assignment tool validation with empty tasks."""
        result = solve_assignment_problem(["Alice"], [], [[]])
        assert result["status"] == "error"

    def test_transportation_tool_empty_suppliers_validation(self):
        """Test transportation tool validation with empty suppliers."""
        result = solve_transportation_problem([], [{"name": "C1", "demand": 80}], [[]])
        assert result["status"] == "error"

    def test_transportation_tool_empty_consumers_validation(self):
        """Test transportation tool validation with empty consumers."""
        result = solve_transportation_problem([{"name": "S1", "supply": 100}], [], [[]])
        assert result["status"] == "error"

    def test_transportation_tool_unbalanced_validation(self):
        """Test transportation tool with unbalanced supply/demand."""
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1", "demand": 200}]  # More demand than supply
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert "status" in result
        # Should handle or warn about unbalanced problem


class TestRegisterAssignmentTools:
    """Tests for assignment tools registration."""

    def test_register_assignment_tools(self):
        """Test registration of assignment tools with MCP server."""
        # Mock FastMCP instance
        mock_mcp = MagicMock()
        mock_tool_decorator = MagicMock()
        mock_mcp.tool.return_value = mock_tool_decorator

        # Register tools
        register_assignment_tools(mock_mcp)

        # Verify tool decorator was called (should be called twice: for assignment and transportation)
        assert mock_mcp.tool.call_count == 2

    def test_assignment_tool_wrapper(self):
        """Test the wrapped assignment tool function with real solving."""
        # Mock FastMCP instance and tool registration
        mock_mcp = MagicMock()
        tool_functions = []

        def capture_tool_function():
            def decorator(func):
                tool_functions.append(func)
                return func

            return decorator

        mock_mcp.tool.side_effect = capture_tool_function

        # Register tools
        register_assignment_tools(mock_mcp)

        # Get the assignment tool function
        assert len(tool_functions) == 2
        assignment_tool = tool_functions[0]  # First registered tool should be assignment

        # Test the wrapped function with real data
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2"]
        costs = [[4, 6], [2, 5]]

        result = assignment_tool(workers, tasks, costs)

        # Verify real solving occurred
        assert result["status"] == "optimal"
        assert "total_cost" in result
        assert "assignments" in result
        assert "execution_time" in result
        assert len(result["assignments"]) == 2

    def test_transportation_tool_wrapper(self):
        """Test the wrapped transportation tool function with real solving."""
        # Mock FastMCP instance and tool registration
        mock_mcp = MagicMock()
        tool_functions = []

        def capture_tool_function():
            def decorator(func):
                tool_functions.append(func)
                return func

            return decorator

        mock_mcp.tool.side_effect = capture_tool_function

        # Register tools
        register_assignment_tools(mock_mcp)

        # Get the transportation tool function
        assert len(tool_functions) == 2
        transportation_tool = tool_functions[1]  # Second registered tool should be transportation

        # Test the wrapped function with balanced supply/demand
        suppliers = [{"name": "S1", "supply": 100}]
        consumers = [{"name": "C1", "demand": 100}]  # Balanced supply/demand
        costs = [[5]]

        result = transportation_tool(suppliers, consumers, costs)

        # Verify real solving occurred
        assert result["status"] == "optimal"
        assert "total_cost" in result
        assert "flows" in result or "shipments" in result
        assert "execution_time" in result


class TestAssignmentEdgeCases:
    """Tests for assignment edge cases and error conditions."""

    def test_large_assignment_problem(self):
        """Test assignment problem with many workers and tasks."""
        num_workers = 20
        num_tasks = 20
        workers = [f"Worker{i}" for i in range(num_workers)]
        tasks = [f"Task{i}" for i in range(num_tasks)]
        costs = [[i + j for j in range(num_tasks)] for i in range(num_workers)]

        result = solve_assignment_problem(workers, tasks, costs)

        assert "status" in result

    def test_single_worker_single_task(self):
        """Test assignment problem with single worker and task."""
        workers = ["Alice"]
        tasks = ["Task1"]
        costs = [[5]]

        result = solve_assignment_problem(workers, tasks, costs)

        assert "status" in result
        if result["status"] == "optimal":
            assert result["total_cost"] == 5
            assert len(result["assignments"]) == 1

    def test_zero_cost_assignment(self):
        """Test assignment problem with zero costs."""
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2"]
        costs = [[0, 5], [3, 0]]

        result = solve_assignment_problem(workers, tasks, costs)

        assert "status" in result
        if result["status"] == "optimal":
            assert result["total_cost"] >= 0

    def test_high_cost_assignment(self):
        """Test assignment problem with very high costs."""
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2"]
        costs = [[1000000, 2000000], [1500000, 1800000]]

        result = solve_assignment_problem(workers, tasks, costs)

        assert "status" in result

    def test_fractional_costs(self):
        """Test assignment problem with fractional costs."""
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2"]
        costs = [[4.5, 6.2], [2.1, 5.8]]

        result = solve_assignment_problem(workers, tasks, costs)

        assert "status" in result

    def test_transportation_large_supply_demand(self):
        """Test transportation problem with large supply and demand values."""
        suppliers = [{"name": "S1", "supply": 1000000}]
        consumers = [{"name": "C1", "demand": 1000000}]
        costs = [[1.5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert "status" in result

    def test_transportation_zero_supply_demand(self):
        """Test transportation problem with zero supply and demand."""
        suppliers = [{"name": "S1", "supply": 0}]
        consumers = [{"name": "C1", "demand": 0}]
        costs = [[5]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert "status" in result
        if result["status"] == "optimal":
            assert result["total_cost"] == 0

    def test_transportation_fractional_supply_demand(self):
        """Test transportation problem with fractional supply and demand."""
        suppliers = [{"name": "S1", "supply": 100.5}]
        consumers = [{"name": "C1", "demand": 100.5}]
        costs = [[2.3]]

        result = solve_transportation_problem(suppliers, consumers, costs)

        assert "status" in result

    def test_assignment_with_complex_constraints(self):
        """Test assignment problem with complex constraint structure."""
        workers = ["Alice", "Bob", "Charlie"]
        tasks = ["Task1", "Task2", "Task3"]
        costs = [[4, 6, 3], [2, 5, 1], [3, 4, 2]]

        # Test forbidden assignments constraint - should return error
        constraints = {"forbidden_assignments": [("Alice", "Task2"), ("Bob", "Task3")]}
        result = solve_assignment_problem(workers, tasks, costs, constraints=constraints)
        assert result["status"] == "error"
        assert (
            "Forbidden assignments constraints are not currently supported"
            in result["error_message"]
        )

        # Test task requirements constraint - should return error
        constraints = {"task_requirements": {"Task1": 1, "Task2": 1, "Task3": 1}}
        result = solve_assignment_problem(workers, tasks, costs, constraints=constraints)
        assert result["status"] == "error"
        assert (
            "Task requirements constraints are not currently supported" in result["error_message"]
        )

        # Test different worker limits - should return error
        constraints = {"worker_limits": {"Alice": 1, "Bob": 2, "Charlie": 1}}
        result = solve_assignment_problem(workers, tasks, costs, constraints=constraints)
        assert result["status"] == "error"
        assert (
            "Individual worker limits with different values are not currently supported"
            in result["error_message"]
        )

    def test_assignment_maximize_large_values(self):
        """Test assignment problem maximizing with large values."""
        workers = ["Alice", "Bob"]
        tasks = ["Task1", "Task2"]
        costs = [[100000, 150000], [120000, 180000]]

        result = solve_assignment_problem(workers, tasks, costs, objective="maximize")

        assert "status" in result
        if result["status"] == "optimal":
            assert result["total_cost"] > 0
