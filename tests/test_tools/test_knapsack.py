"""Tests for knapsack tools."""

from ortools.algorithms.python import knapsack_solver  # type: ignore


class TestKnapsackTools:
    """Tests for knapsack tools."""

    def test_solve_knapsack_problem_success(self):
        """Test successful knapsack problem solving."""
        items = [
            {"name": "Item1", "value": 10, "weight": 5},
            {"name": "Item2", "value": 15, "weight": 8},
            {"name": "Item3", "value": 8, "weight": 3},
            {"name": "Item4", "value": 12, "weight": 6},
        ]
        capacity = 10

        # Create knapsack solver directly
        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "KnapsackSolver"
        )

        # Prepare data
        values = [int(item["value"] * 1000) for item in items]
        weights = [int(item["weight"] * 1000) for item in items]
        capacities = [int(capacity * 1000)]

        solver.init(values, [weights], capacities)
        computed_value = solver.solve()

        assert computed_value > 0

        # Extract solution
        selected_items = []
        total_value = 0.0

        for i in range(len(items)):
            if solver.best_solution_contains(i):
                selected_items.append(items[i])
                total_value += items[i]["value"]

        assert len(selected_items) > 0
        assert total_value > 0

    def test_solve_knapsack_problem_empty_items(self):
        """Test knapsack problem with empty items list."""
        # This should return an error
        # We'll test this through the tool interface when we add tool tests
        pass

    def test_solve_knapsack_problem_zero_capacity(self):
        """Test knapsack problem with zero capacity."""
        # This should return an error
        # We'll test this through the tool interface when we add tool tests
        pass

    def test_solve_knapsack_problem_with_volume(self):
        """Test knapsack problem with volume constraints."""
        items = [
            {"name": "Item1", "value": 10, "weight": 5, "volume": 2},
            {"name": "Item2", "value": 15, "weight": 8, "volume": 3},
            {"name": "Item3", "value": 8, "weight": 3, "volume": 1},
        ]
        capacity = 10
        volume_capacity = 4

        # Create knapsack solver for multidimensional problem
        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER,
            "KnapsackSolver",
        )

        # Prepare data with volume constraints
        values = [int(item["value"] * 1000) for item in items]
        weights = [int(item["weight"] * 1000) for item in items]
        volumes = [int(item["volume"] * 1000) for item in items]
        capacities = [int(capacity * 1000), int(volume_capacity * 1000)]

        solver.init(values, [weights, volumes], capacities)
        computed_value = solver.solve()

        assert computed_value >= 0  # May be 0 if no feasible solution

    def test_solve_knapsack_problem_large_items(self):
        """Test knapsack problem where all items are too heavy."""
        items = [
            {"name": "Item1", "value": 10, "weight": 15},
            {"name": "Item2", "value": 15, "weight": 20},
        ]
        capacity = 10

        # Create knapsack solver
        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "KnapsackSolver"
        )

        # Prepare data
        values = [int(item["value"] * 1000) for item in items]
        weights = [int(item["weight"] * 1000) for item in items]
        capacities = [int(capacity * 1000)]

        solver.init(values, [weights], capacities)
        computed_value = solver.solve()

        # Should be 0 since no items fit
        assert computed_value == 0

    def test_solve_knapsack_problem_single_item(self):
        """Test knapsack problem with single item that fits."""
        items = [{"name": "Item1", "value": 10, "weight": 5}]
        capacity = 10

        # Create knapsack solver
        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "KnapsackSolver"
        )

        # Prepare data
        values = [int(item["value"] * 1000) for item in items]
        weights = [int(item["weight"] * 1000) for item in items]
        capacities = [int(capacity * 1000)]

        solver.init(values, [weights], capacities)
        computed_value = solver.solve()

        assert computed_value > 0

        # Should select the single item
        assert solver.best_solution_contains(0)


class TestKnapsackToolsValidation:
    """Tests for knapsack tools input validation."""

    def test_knapsack_tool_empty_items_validation(self):
        """Test knapsack tool validation with empty items."""
        from mcp_optimizer.tools.knapsack import solve_knapsack_problem

        result = solve_knapsack_problem(items=[], capacity=10.0)

        assert result["status"] == "error"
        assert result["error_message"] == "No items provided"
        assert result["total_value"] is None
        assert result["selected_items"] == []

    def test_knapsack_tool_zero_capacity_validation(self):
        """Test knapsack tool validation with zero capacity."""
        from mcp_optimizer.tools.knapsack import solve_knapsack_problem

        items = [{"name": "Item1", "value": 10, "weight": 5}]
        result = solve_knapsack_problem(items=items, capacity=0.0)

        assert result["status"] == "error"
        assert result["error_message"] == "Capacity must be positive"
        assert result["total_value"] is None
        assert result["selected_items"] == []

    def test_knapsack_tool_invalid_item_format_validation(self):
        """Test knapsack tool validation with invalid item format."""
        from mcp_optimizer.tools.knapsack import solve_knapsack_problem

        items = ["not_a_dict", {"name": "Item1", "value": 10, "weight": 5}]
        result = solve_knapsack_problem(items=items, capacity=10.0)

        assert result["status"] == "error"
        assert "Item 0 must be a dictionary" in result["error_message"]
        assert result["total_value"] is None
        assert result["selected_items"] == []

    def test_knapsack_tool_missing_fields_validation(self):
        """Test knapsack tool validation with missing required fields."""
        from mcp_optimizer.tools.knapsack import solve_knapsack_problem

        items = [{"name": "Item1", "value": 10}]  # Missing weight
        result = solve_knapsack_problem(items=items, capacity=10.0)

        assert result["status"] == "error"
        assert "missing required field: weight" in result["error_message"]
        assert result["total_value"] is None
        assert result["selected_items"] == []

    def test_knapsack_tool_negative_values_validation(self):
        """Test knapsack tool validation with negative values."""
        from mcp_optimizer.tools.knapsack import solve_knapsack_problem

        items = [{"name": "Item1", "value": -10, "weight": 5}]
        result = solve_knapsack_problem(items=items, capacity=10.0)

        assert result["status"] == "error"
        assert "value and weight must be non-negative" in result["error_message"]
        assert result["total_value"] is None
        assert result["selected_items"] == []


class TestKnapsackSolverTypes:
    """Tests for different knapsack solver types."""

    def test_dynamic_programming_solver(self):
        """Test dynamic programming solver."""
        items = [
            {"name": "Item1", "value": 10, "weight": 5},
            {"name": "Item2", "value": 15, "weight": 8},
            {"name": "Item3", "value": 8, "weight": 3},
        ]
        capacity = 10

        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "DynamicProgramming"
        )

        values = [int(item["value"] * 1000) for item in items]
        weights = [int(item["weight"] * 1000) for item in items]
        capacities = [int(capacity * 1000)]

        solver.init(values, [weights], capacities)
        result = solver.solve()

        assert result > 0

    def test_brute_force_solver(self):
        """Test brute force solver with small problem."""
        items = [
            {"name": "Item1", "value": 10, "weight": 5},
            {"name": "Item2", "value": 8, "weight": 3},
        ]
        capacity = 10

        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.KNAPSACK_BRUTE_FORCE_SOLVER, "BruteForce"
        )

        values = [int(item["value"] * 1000) for item in items]
        weights = [int(item["weight"] * 1000) for item in items]
        capacities = [int(capacity * 1000)]

        solver.init(values, [weights], capacities)
        result = solver.solve()

        assert result > 0

    def test_64items_solver(self):
        """Test 64 items solver."""
        items = [
            {"name": f"Item{i}", "value": i + 1, "weight": i + 1}
            for i in range(10)  # Small problem for testing
        ]
        capacity = 20

        solver = knapsack_solver.KnapsackSolver(knapsack_solver.KNAPSACK_64ITEMS_SOLVER, "64Items")

        values = [int(item["value"] * 1000) for item in items]
        weights = [int(item["weight"] * 1000) for item in items]
        capacities = [int(capacity * 1000)]

        solver.init(values, [weights], capacities)
        result = solver.solve()

        assert result >= 0  # May be 0 if no solution found
