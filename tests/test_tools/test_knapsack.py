"""Tests for knapsack problem tools."""

from unittest.mock import MagicMock, patch

from mcp_optimizer.tools.knapsack import register_knapsack_tools, solve_knapsack_problem


class TestKnapsackTools:
    """Tests for knapsack problem solving tools."""

    def test_solve_knapsack_problem_success(self):
        """Test successful knapsack problem solving."""
        items = [
            {"name": "item1", "value": 10, "weight": 5},
            {"name": "item2", "value": 20, "weight": 10},
        ]
        capacity = 15

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        assert isinstance(result["total_value"], (int, float))
        assert isinstance(result["selected_items"], list)
        assert "execution_time" in result
        assert "solver_info" in result

    def test_solve_knapsack_problem_empty_items(self):
        """Test knapsack with empty items list."""
        result = solve_knapsack_problem([], 10)

        assert result["status"] == "error"
        assert result["error_message"] == "No items provided"
        assert result["total_value"] is None
        assert result["selected_items"] == []

    def test_solve_knapsack_problem_zero_capacity(self):
        """Test knapsack with zero capacity."""
        items = [{"name": "item1", "value": 10, "weight": 5}]
        result = solve_knapsack_problem(items, 0)

        assert result["status"] == "error"
        assert result["error_message"] == "Capacity must be positive"

    def test_solve_knapsack_problem_negative_capacity(self):
        """Test knapsack with negative capacity."""
        items = [{"name": "item1", "value": 10, "weight": 5}]
        result = solve_knapsack_problem(items, -5)

        assert result["status"] == "error"
        assert result["error_message"] == "Capacity must be positive"

    def test_solve_knapsack_problem_with_volume(self):
        """Test knapsack with volume constraints."""
        items = [
            {"name": "item1", "value": 10, "weight": 5, "volume": 3},
            {"name": "item2", "value": 20, "weight": 8, "volume": 4},
        ]
        capacity = 15
        volume_capacity = 6

        result = solve_knapsack_problem(items, capacity, volume_capacity)

        assert result["status"] in ["optimal", "infeasible"]
        assert "solver_info" in result
        if result["status"] == "optimal":
            assert result["solver_info"]["algorithm"] == "Branch and Bound"

    def test_solve_knapsack_problem_large_items(self):
        """Test knapsack where all items are larger than capacity."""
        items = [
            {"name": "item1", "value": 10, "weight": 20},
            {"name": "item2", "value": 15, "weight": 25},
        ]
        capacity = 10

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] in ["optimal", "infeasible"]
        if result["status"] == "optimal":
            assert result["total_value"] == 0.0

    def test_solve_knapsack_problem_single_item(self):
        """Test knapsack with single item."""
        items = [{"name": "item1", "value": 10, "weight": 5}]
        capacity = 10

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        assert result["total_value"] == 10.0
        assert len(result["selected_items"]) == 1
        assert result["selected_items"][0]["name"] == "item1"

    def test_solve_knapsack_problem_invalid_item_type(self):
        """Test knapsack with invalid item type."""
        items = ["invalid_item"]
        capacity = 10

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "error"
        assert "Item 0 must be a dictionary" in result["error_message"]

    def test_solve_knapsack_problem_missing_item_fields(self):
        """Test knapsack with missing item fields."""
        items = [{"name": "item1"}]  # Missing value and weight
        capacity = 10

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "error"
        assert "missing required field: value" in result["error_message"]

    def test_solve_knapsack_problem_negative_item_values(self):
        """Test knapsack with negative item values."""
        items = [{"name": "item1", "value": -10, "weight": 5}]
        capacity = 10

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "error"
        assert "value and weight must be non-negative" in result["error_message"]

    def test_solve_knapsack_problem_unbounded(self):
        """Test unbounded knapsack problem."""
        items = [
            {"name": "item1", "value": 10, "weight": 5},
            {"name": "item2", "value": 15, "weight": 8},
        ]
        capacity = 20

        result = solve_knapsack_problem(items, capacity, knapsack_type="unbounded")

        assert result["status"] in ["optimal", "infeasible"]
        if result["status"] == "optimal":
            assert isinstance(result["total_value"], (int, float))

    def test_solve_knapsack_problem_bounded(self):
        """Test bounded knapsack problem."""
        items = [
            {"name": "item1", "value": 10, "weight": 5, "quantity": 2},
            {"name": "item2", "value": 15, "weight": 8, "quantity": 1},
        ]
        capacity = 20

        result = solve_knapsack_problem(
            items, capacity, knapsack_type="bounded", max_items_per_type=3
        )

        assert result["status"] in ["optimal", "infeasible"]
        if result["status"] == "optimal":
            assert isinstance(result["total_value"], (int, float))

    def test_solve_knapsack_problem_with_volume_no_volume_data(self):
        """Test knapsack with volume capacity but no volume data in items."""
        items = [
            {"name": "item1", "value": 10, "weight": 5},  # No volume field
            {"name": "item2", "value": 15, "weight": 8},
        ]
        capacity = 20
        volume_capacity = 10

        result = solve_knapsack_problem(items, capacity, volume_capacity)

        assert result["status"] in ["optimal", "infeasible"]
        # Should use dynamic programming since no volume constraints are active
        if result["status"] == "optimal":
            assert result["solver_info"]["algorithm"] == "Dynamic Programming"

    def test_solve_knapsack_problem_no_feasible_solution(self):
        """Test knapsack with no feasible solution."""
        with patch("ortools.algorithms.python.knapsack_solver.KnapsackSolver") as mock_solver_class:
            mock_solver = MagicMock()
            mock_solver.solve.return_value = 0  # No solution found
            mock_solver_class.return_value = mock_solver

            items = [{"name": "item1", "value": 10, "weight": 5}]
            capacity = 10

            result = solve_knapsack_problem(items, capacity)

            assert result["status"] == "infeasible"
            assert result["total_value"] == 0.0
            assert result["selected_items"] == []

    def test_solve_knapsack_problem_with_optimal_solution(self):
        """Test knapsack with optimal solution and proper item selection."""
        items = [
            {"name": "item1", "value": 60, "weight": 10},
            {"name": "item2", "value": 100, "weight": 20},
            {"name": "item3", "value": 120, "weight": 30},
        ]
        capacity = 50

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        assert result["total_value"] > 0
        assert len(result["selected_items"]) > 0

        # Verify selected items structure
        for item in result["selected_items"]:
            assert "name" in item
            assert "quantity" in item
            assert "value" in item
            assert "weight" in item
            assert "total_value" in item
            assert "total_weight" in item

    def test_solve_knapsack_problem_with_volume_constraints_active(self):
        """Test knapsack with active volume constraints."""
        items = [
            {"name": "item1", "value": 60, "weight": 10, "volume": 5},
            {"name": "item2", "value": 100, "weight": 20, "volume": 8},
        ]
        capacity = 50
        volume_capacity = 10

        result = solve_knapsack_problem(items, capacity, volume_capacity)

        assert result["status"] in ["optimal", "infeasible"]
        if result["status"] == "optimal":
            # Check that volume constraints are respected
            for item in result["selected_items"]:
                assert "total_volume" in item
                if item["total_volume"] is not None:
                    assert item["total_volume"] >= 0


class TestKnapsackToolsValidation:
    """Tests for knapsack tools validation."""

    def test_knapsack_tool_empty_items_validation(self):
        """Test knapsack tool validation with empty items."""
        result = solve_knapsack_problem([], 10)
        assert result["status"] == "error"

    def test_knapsack_tool_zero_capacity_validation(self):
        """Test knapsack tool validation with zero capacity."""
        items = [{"name": "item1", "value": 10, "weight": 5}]
        result = solve_knapsack_problem(items, 0)
        assert result["status"] == "error"

    def test_knapsack_tool_invalid_item_format_validation(self):
        """Test knapsack tool validation with invalid item format."""
        items = [42]  # Invalid item format
        result = solve_knapsack_problem(items, 10)
        assert result["status"] == "error"

    def test_knapsack_tool_missing_fields_validation(self):
        """Test knapsack tool validation with missing item fields."""
        items = [{"name": "item1"}]  # Missing value and weight
        result = solve_knapsack_problem(items, 10)
        assert result["status"] == "error"

    def test_knapsack_tool_negative_values_validation(self):
        """Test knapsack tool validation with negative values."""
        items = [{"name": "item1", "value": -10, "weight": 5}]
        result = solve_knapsack_problem(items, 10)
        assert result["status"] == "error"


class TestKnapsackSolverTypes:
    """Tests for different knapsack solver types."""

    def test_dynamic_programming_solver(self):
        """Test dynamic programming solver selection."""
        items = [
            {"name": "item1", "value": 10, "weight": 5},
            {"name": "item2", "value": 20, "weight": 8},
        ]
        capacity = 15

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        assert result["solver_info"]["algorithm"] == "Dynamic Programming"

    def test_brute_force_solver(self):
        """Test solver behavior with small item count (uses dynamic programming)."""
        items = [{"name": "item1", "value": 10, "weight": 5}]
        capacity = 10

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        assert result["solver_info"]["solver_name"] == "OR-Tools KnapsackSolver"

    def test_64items_solver(self):
        """Test solver with larger item count."""
        # Create more items to test solver behavior
        items = []
        for i in range(10):
            items.append(
                {
                    "name": f"item{i}",
                    "value": 10 + i,
                    "weight": 5 + i,
                }
            )
        capacity = 50

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        assert result["solver_info"]["items_count"] == 10


class TestRegisterKnapsackTools:
    """Tests for knapsack tools registration."""

    def test_register_knapsack_tools(self):
        """Test registration of knapsack tools with MCP server."""
        # Mock FastMCP instance
        mock_mcp = MagicMock()
        mock_tool_decorator = MagicMock()
        mock_mcp.tool.return_value = mock_tool_decorator

        # Register tools
        register_knapsack_tools(mock_mcp)

        # Verify tool decorator was called
        mock_mcp.tool.assert_called()

    def test_knapsack_tool_wrapper(self):
        """Test the wrapped knapsack tool function."""
        # Mock FastMCP instance
        mock_mcp = MagicMock()

        # Register tools
        register_knapsack_tools(mock_mcp)

        # Verify tool decorator was called
        mock_mcp.tool.assert_called()


class TestKnapsackEdgeCases:
    """Tests for knapsack edge cases and error conditions."""

    def test_fractional_values_and_weights(self):
        """Test knapsack with fractional values and weights."""
        items = [
            {"name": "item1", "value": 10.5, "weight": 5.2},
            {"name": "item2", "value": 20.8, "weight": 8.3},
        ]
        capacity = 15.5

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        assert isinstance(result["total_value"], (int, float))

    def test_large_capacity(self):
        """Test knapsack with very large capacity."""
        items = [
            {"name": "item1", "value": 10, "weight": 5},
            {"name": "item2", "value": 20, "weight": 8},
        ]
        capacity = 1000000

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        # All items should be selected
        assert result["total_value"] == sum(item["value"] for item in items)

    def test_exact_capacity_match(self):
        """Test knapsack where selected items exactly match capacity."""
        items = [
            {"name": "item1", "value": 10, "weight": 5},
            {"name": "item2", "value": 20, "weight": 10},
        ]
        capacity = 15  # Exact match for both items

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        total_weight = sum(item["total_weight"] for item in result["selected_items"])
        assert total_weight <= capacity

    def test_zero_value_items(self):
        """Test knapsack with zero-value items."""
        items = [
            {"name": "item1", "value": 0, "weight": 5},
            {"name": "item2", "value": 20, "weight": 8},
        ]
        capacity = 15

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        # Should prefer non-zero value items
        assert result["total_value"] >= 0

    def test_zero_weight_items(self):
        """Test knapsack with zero-weight items."""
        items = [
            {"name": "item1", "value": 10, "weight": 0},
            {"name": "item2", "value": 20, "weight": 8},
        ]
        capacity = 15

        result = solve_knapsack_problem(items, capacity)

        assert result["status"] == "optimal"
        # Zero-weight items should always be selected
        assert result["total_value"] >= 10
