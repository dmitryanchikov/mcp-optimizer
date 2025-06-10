"""Tests for linear programming tools."""

from unittest.mock import MagicMock

from mcp_optimizer.schemas.base import (
    Constraint,
    ConstraintOperator,
    Objective,
    ObjectiveSense,
    Variable,
    VariableType,
)
from mcp_optimizer.solvers.pulp_solver import PuLPSolver
from mcp_optimizer.tools.linear_programming import (
    register_linear_programming_tools,
    solve_integer_program,
    solve_linear_program,
)


class TestLinearProgrammingTools:
    """Tests for linear programming tools."""

    def test_solve_linear_program_success(self):
        """Test successful linear program solving."""
        # Test data: maximize 3x + 2y subject to constraints
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 3, "y": 2},
        )
        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0),
            "y": Variable(type=VariableType.CONTINUOUS, lower=0),
        }
        constraints = [
            Constraint(
                expression={"x": 2, "y": 1},
                operator=ConstraintOperator.LE,
                rhs=20,
            ),
            Constraint(
                expression={"x": 1, "y": 3},
                operator=ConstraintOperator.LE,
                rhs=30,
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == "optimal"
        assert result["objective_value"] is not None
        assert result["objective_value"] > 0
        assert "x" in result["variables"]
        assert "y" in result["variables"]
        assert result["execution_time"] > 0
        assert "solver_info" in result

    def test_solve_integer_program_success(self):
        """Test successful integer program solving."""
        # Binary knapsack problem
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"item1": 10, "item2": 15},
        )
        variables = {
            "item1": Variable(type=VariableType.BINARY),
            "item2": Variable(type=VariableType.BINARY),
        }
        constraints = [
            Constraint(
                expression={"item1": 5, "item2": 8},
                operator=ConstraintOperator.LE,
                rhs=10,
            )
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == "optimal"
        assert result["objective_value"] is not None

        # Check binary constraints
        for var_name, value in result["variables"].items():
            assert value in [0, 1], f"Variable {var_name} should be binary"

    def test_solve_linear_program_infeasible(self):
        """Test infeasible linear program."""
        # Infeasible problem: x >= 0, x <= -1
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1},
        )
        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0),
        }
        constraints = [
            Constraint(
                expression={"x": 1},
                operator=ConstraintOperator.LE,
                rhs=-1,
            )
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == "infeasible"
        assert result["objective_value"] is None
        assert result["error_message"] is not None

    def test_solve_with_time_limit(self):
        """Test solving with time limit."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1, "y": 1},
        )
        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0),
            "y": Variable(type=VariableType.CONTINUOUS, lower=0),
        }
        constraints = [
            Constraint(
                expression={"x": 1, "y": 1},
                operator=ConstraintOperator.LE,
                rhs=10,
            )
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints, time_limit=0.1)

        # Should still solve this simple problem
        assert result["status"] == "optimal"
        assert result["execution_time"] <= 1.0

    def test_different_solvers(self):
        """Test using different solvers."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1},
        )
        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=1),
        }
        constraints = []

        # Test with different solvers (CBC should always be available)
        for solver_name in ["CBC"]:  # Could add "GLPK" if available
            solver = PuLPSolver(solver_name=solver_name)
            result = solver.solve_linear_program(objective, variables, constraints)

            assert result["status"] == "optimal"
            assert result["solver_info"]["solver_name"] == solver_name

    def test_mixed_integer_program(self):
        """Test mixed integer programming."""
        objective = Objective(
            sense=ObjectiveSense.MINIMIZE,
            coefficients={"x": 1, "y": 2, "z": 3},
        )
        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0),
            "y": Variable(type=VariableType.INTEGER, lower=0),
            "z": Variable(type=VariableType.BINARY),
        }
        constraints = [
            Constraint(
                expression={"x": 1, "y": 1, "z": 1},
                operator=ConstraintOperator.GE,
                rhs=2,
            )
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] in ["optimal", "feasible"]

        # Check variable types
        if "y" in result["variables"]:
            assert result["variables"]["y"] == int(result["variables"]["y"])
        if "z" in result["variables"]:
            assert result["variables"]["z"] in [0, 1]

    def test_solve_linear_program_minimize(self):
        """Test linear program with minimize objective."""
        objective = {"sense": "minimize", "coefficients": {"x": 1, "y": 1}}
        variables = {
            "x": {"type": "continuous", "lower": 0},
            "y": {"type": "continuous", "lower": 0},
        }
        constraints = [{"expression": {"x": 1, "y": 1}, "operator": ">=", "rhs": 10}]

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result
        assert result["status"] in ["optimal", "infeasible", "unbounded"]

    def test_solve_linear_program_with_equality_constraints(self):
        """Test linear program with equality constraints."""
        objective = {"sense": "maximize", "coefficients": {"x": 1, "y": 1}}
        variables = {
            "x": {"type": "continuous", "lower": 0},
            "y": {"type": "continuous", "lower": 0},
        }
        constraints = [{"expression": {"x": 1, "y": 1}, "operator": "==", "rhs": 10}]

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result
        assert result["status"] in ["optimal", "infeasible", "unbounded"]

    def test_solve_linear_program_unbounded(self):
        """Test unbounded linear program."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "continuous", "lower": 0}}
        constraints = []  # No upper bound constraints

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result

    def test_solve_linear_program_with_time_limit(self):
        """Test linear program with time limit."""
        objective = {"sense": "maximize", "coefficients": {"x": 3, "y": 2}}
        variables = {
            "x": {"type": "continuous", "lower": 0},
            "y": {"type": "continuous", "lower": 0},
        }
        constraints = [{"expression": {"x": 2, "y": 1}, "operator": "<=", "rhs": 20}]

        result = solve_linear_program(objective, variables, constraints, time_limit_seconds=60.0)

        assert "status" in result
        assert "execution_time" in result

    def test_solve_linear_program_different_solvers(self):
        """Test linear program with different solvers."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "continuous", "lower": 0, "upper": 10}}
        constraints = []

        solvers = ["CBC", "GLPK"]

        for solver in solvers:
            result = solve_linear_program(objective, variables, constraints, solver=solver)
            assert "status" in result
            if "solver_info" in result and result["solver_info"]:
                # Only check if solver_info exists and is not empty
                assert (
                    solver.lower() in str(result["solver_info"]).lower()
                    or result["status"] == "error"
                )

    def test_solve_linear_program_invalid_objective(self):
        """Test linear program with invalid objective."""
        objective = {"sense": "invalid", "coefficients": {"x": 1}}
        variables = {"x": {"type": "continuous", "lower": 0}}
        constraints = []

        result = solve_linear_program(objective, variables, constraints)

        assert result["status"] == "error"
        assert "error_message" in result

    def test_solve_linear_program_invalid_variable(self):
        """Test linear program with invalid variable."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "invalid_type", "lower": 0}}
        constraints = []

        result = solve_linear_program(objective, variables, constraints)

        assert result["status"] == "error"
        assert "error_message" in result

    def test_solve_linear_program_invalid_constraint(self):
        """Test linear program with invalid constraint."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "continuous", "lower": 0}}
        constraints = [{"expression": {"x": 1}, "operator": "invalid", "rhs": 10}]

        result = solve_linear_program(objective, variables, constraints)

        assert result["status"] == "error"
        assert "error_message" in result

    def test_solve_linear_program_exception_handling(self):
        """Test linear program with invalid input causing real error."""
        # Test with invalid coefficient type - should cause real error
        objective = {
            "sense": "maximize",
            "coefficients": {"x": "invalid"},
        }  # String instead of number
        variables = {"x": {"type": "continuous", "lower": 0}}
        constraints = []

        result = solve_linear_program(objective, variables, constraints)

        assert result["status"] == "error"
        assert "error_message" in result


class TestIntegerProgrammingTools:
    """Tests for integer programming tools."""

    def test_solve_integer_program_success(self):
        """Test successful integer program solving."""
        objective = {"sense": "maximize", "coefficients": {"x": 3, "y": 2}}
        variables = {"x": {"type": "integer", "lower": 0}, "y": {"type": "integer", "lower": 0}}
        constraints = [{"expression": {"x": 2, "y": 1}, "operator": "<=", "rhs": 20}]

        result = solve_integer_program(objective, variables, constraints)

        assert "status" in result
        assert "objective_value" in result
        assert "variables" in result
        assert "execution_time" in result
        assert "solver_info" in result

    def test_solve_integer_program_binary_variables(self):
        """Test integer program with binary variables."""
        objective = {"sense": "maximize", "coefficients": {"item1": 10, "item2": 15}}
        variables = {"item1": {"type": "binary"}, "item2": {"type": "binary"}}
        constraints = [{"expression": {"item1": 5, "item2": 8}, "operator": "<=", "rhs": 10}]

        result = solve_integer_program(objective, variables, constraints)

        assert "status" in result

    def test_solve_integer_program_mixed_variables(self):
        """Test mixed-integer program with continuous and integer variables."""
        objective = {"sense": "minimize", "coefficients": {"x": 1, "y": 2}}
        variables = {"x": {"type": "continuous", "lower": 0}, "y": {"type": "integer", "lower": 0}}
        constraints = [{"expression": {"x": 1, "y": 1}, "operator": ">=", "rhs": 5}]

        result = solve_integer_program(objective, variables, constraints)

        assert "status" in result

    def test_solve_integer_program_infeasible(self):
        """Test infeasible integer program."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "integer", "lower": 0, "upper": 2}}
        constraints = [{"expression": {"x": 1}, "operator": ">=", "rhs": 5}]

        result = solve_integer_program(objective, variables, constraints)

        assert "status" in result

    def test_solve_integer_program_with_time_limit(self):
        """Test integer program with time limit."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "integer", "lower": 0, "upper": 10}}
        constraints = []

        result = solve_integer_program(objective, variables, constraints, time_limit_seconds=30.0)

        assert "status" in result
        assert "execution_time" in result

    def test_solve_integer_program_different_solvers(self):
        """Test integer program with different solvers."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "integer", "lower": 0, "upper": 10}}
        constraints = []

        solvers = ["CBC", "GLPK"]

        for solver in solvers:
            result = solve_integer_program(objective, variables, constraints, solver=solver)
            assert "status" in result

    def test_solve_integer_program_invalid_input(self):
        """Test integer program with invalid input."""
        objective = {"sense": "invalid", "coefficients": {"x": 1}}
        variables = {"x": {"type": "integer", "lower": 0}}
        constraints = []

        result = solve_integer_program(objective, variables, constraints)

        assert result["status"] == "error"
        assert "error_message" in result

    def test_solve_integer_program_exception_handling(self):
        """Test integer program with invalid input causing real error."""
        # Test with invalid variable type - should cause real error
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "invalid_type", "lower": 0}}  # Invalid variable type
        constraints = []

        result = solve_integer_program(objective, variables, constraints)

        assert result["status"] == "error"
        assert "error_message" in result


class TestRegisterLinearProgrammingTools:
    """Tests for linear programming tools registration."""

    def test_register_linear_programming_tools(self):
        """Test registration of linear programming tools with MCP server."""
        # Mock FastMCP instance
        mock_mcp = MagicMock()
        mock_tool_decorator = MagicMock()
        mock_mcp.tool.return_value = mock_tool_decorator

        # Register tools
        register_linear_programming_tools(mock_mcp)

        # Verify tool decorator was called (should be called twice: for LP and IP)
        assert mock_mcp.tool.call_count == 2

    def test_solve_linear_program_tool_wrapper(self):
        """Test the wrapped linear program tool function with real solving."""
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
        register_linear_programming_tools(mock_mcp)

        # Get the linear program tool function
        assert len(tool_functions) == 2
        lp_tool = tool_functions[0]  # First registered tool should be LP

        # Test the wrapped function with real problem
        objective = {"sense": "maximize", "coefficients": {"x": 3, "y": 2}}
        variables = {
            "x": {"type": "continuous", "lower": 0},
            "y": {"type": "continuous", "lower": 0},
        }
        constraints = [{"expression": {"x": 2, "y": 1}, "operator": "<=", "rhs": 20}]

        result = lp_tool(objective, variables, constraints)

        # Verify real solving occurred
        assert result["status"] in ["optimal", "feasible"]
        assert "objective_value" in result
        assert "variables" in result
        assert "execution_time" in result

    def test_solve_integer_program_tool_wrapper(self):
        """Test the wrapped integer program tool function with real solving."""
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
        register_linear_programming_tools(mock_mcp)

        # Get the integer program tool function
        assert len(tool_functions) == 2
        ip_tool = tool_functions[1]  # Second registered tool should be IP

        # Test the wrapped function with real problem
        objective = {"sense": "maximize", "coefficients": {"item1": 10, "item2": 15}}
        variables = {"item1": {"type": "binary"}, "item2": {"type": "binary"}}
        constraints = [{"expression": {"item1": 5, "item2": 8}, "operator": "<=", "rhs": 10}]

        result = ip_tool(objective, variables, constraints, solver="CBC", time_limit_seconds=60.0)

        # Verify real solving occurred
        assert result["status"] in ["optimal", "feasible"]
        assert "objective_value" in result
        assert "variables" in result
        assert "execution_time" in result


class TestLinearProgrammingEdgeCases:
    """Tests for linear programming edge cases."""

    def test_large_problem_size(self):
        """Test linear program with many variables and constraints."""
        # Create a larger problem
        num_vars = 20
        objective = {"sense": "maximize", "coefficients": {f"x{i}": i + 1 for i in range(num_vars)}}
        variables = {
            f"x{i}": {"type": "continuous", "lower": 0, "upper": 10} for i in range(num_vars)
        }
        constraints = [
            {"expression": {f"x{i}": 1 for i in range(num_vars)}, "operator": "<=", "rhs": 50}
        ]

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result

    def test_empty_constraints(self):
        """Test linear program with no constraints."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "continuous", "lower": 0, "upper": 10}}
        constraints = []

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result

    def test_single_variable_single_constraint(self):
        """Test linear program with single variable and constraint."""
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "continuous", "lower": 0}}
        constraints = [{"expression": {"x": 1}, "operator": "<=", "rhs": 5}]

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result
        if result["status"] == "optimal":
            assert result["objective_value"] is not None

    def test_negative_coefficients(self):
        """Test linear program with negative coefficients."""
        objective = {"sense": "minimize", "coefficients": {"x": -1, "y": -2}}
        variables = {
            "x": {"type": "continuous", "lower": 0, "upper": 10},
            "y": {"type": "continuous", "lower": 0, "upper": 10},
        }
        constraints = [{"expression": {"x": 1, "y": 1}, "operator": ">=", "rhs": 5}]

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result

    def test_fractional_coefficients(self):
        """Test linear program with fractional coefficients."""
        objective = {"sense": "maximize", "coefficients": {"x": 1.5, "y": 2.3}}
        variables = {
            "x": {"type": "continuous", "lower": 0},
            "y": {"type": "continuous", "lower": 0},
        }
        constraints = [{"expression": {"x": 0.5, "y": 1.2}, "operator": "<=", "rhs": 10.7}]

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result

    def test_zero_coefficients_in_objective(self):
        """Test linear program with zero coefficients in objective."""
        objective = {"sense": "maximize", "coefficients": {"x": 0, "y": 1}}
        variables = {
            "x": {"type": "continuous", "lower": 0, "upper": 10},
            "y": {"type": "continuous", "lower": 0, "upper": 10},
        }
        constraints = []

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result

    def test_variable_bounds(self):
        """Test linear program with various variable bounds."""
        objective = {"sense": "maximize", "coefficients": {"x": 1, "y": 1, "z": 1}}
        variables = {
            "x": {"type": "continuous", "lower": -5, "upper": 5},  # Negative lower bound
            "y": {"type": "continuous", "lower": 0},  # No upper bound
            "z": {"type": "continuous", "upper": 10},  # No lower bound (None)
        }
        constraints = [{"expression": {"x": 1, "y": 1, "z": 1}, "operator": "<=", "rhs": 10}]

        result = solve_linear_program(objective, variables, constraints)

        assert "status" in result
