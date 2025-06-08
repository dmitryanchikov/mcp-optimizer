"""Tests for integer programming optimization tools."""

from unittest.mock import Mock

import pytest

from mcp_optimizer.schemas.base import OptimizationStatus
from mcp_optimizer.tools.integer_programming import (
    IntegerConstraint,
    IntegerObjective,
    IntegerProgramInput,
    IntegerVariable,
    register_integer_programming_tools,
    solve_binary_program,
    solve_integer_program,
    solve_mixed_integer_program,
)


class TestIntegerVariable:
    """Test IntegerVariable model."""

    def test_valid_integer_variable(self):
        """Test creating a valid integer variable."""
        var = IntegerVariable(
            name="x1",
            type="integer",
            lower=0.0,
            upper=10.0,
        )
        assert var.name == "x1"
        assert var.type == "integer"
        assert var.lower == 0.0
        assert var.upper == 10.0

    def test_binary_variable(self):
        """Test creating a binary variable."""
        var = IntegerVariable(name="b1", type="binary")
        assert var.name == "b1"
        assert var.type == "binary"
        assert var.lower is None
        assert var.upper is None

    def test_continuous_variable(self):
        """Test creating a continuous variable."""
        var = IntegerVariable(name="y1", type="continuous", lower=-5.0, upper=15.0)
        assert var.name == "y1"
        assert var.type == "continuous"
        assert var.lower == -5.0
        assert var.upper == 15.0

    def test_invalid_variable_type(self):
        """Test creating variable with invalid type."""
        with pytest.raises(ValueError):
            IntegerVariable(name="x1", type="invalid_type")

    def test_invalid_bounds(self):
        """Test creating variable with invalid bounds."""
        with pytest.raises(ValueError, match="upper bound must be >= lower bound"):
            IntegerVariable(name="x1", type="integer", lower=10.0, upper=5.0)


class TestIntegerConstraint:
    """Test IntegerConstraint model."""

    def test_valid_constraint(self):
        """Test creating a valid constraint."""
        constraint = IntegerConstraint(
            name="constraint1",
            expression={"x1": 2.0, "x2": 1.5},
            operator="<=",
            rhs=10.0,
        )
        assert constraint.name == "constraint1"
        assert constraint.expression == {"x1": 2.0, "x2": 1.5}
        assert constraint.operator == "<="
        assert constraint.rhs == 10.0

    def test_constraint_without_name(self):
        """Test creating constraint without name."""
        constraint = IntegerConstraint(
            expression={"x1": 1.0},
            operator=">=",
            rhs=5.0,
        )
        assert constraint.name is None

    def test_equality_constraint(self):
        """Test creating equality constraint."""
        constraint = IntegerConstraint(
            expression={"x1": 1.0, "x2": -1.0},
            operator="==",
            rhs=0.0,
        )
        assert constraint.operator == "=="

    def test_invalid_operator(self):
        """Test creating constraint with invalid operator."""
        with pytest.raises(ValueError):
            IntegerConstraint(
                expression={"x1": 1.0},
                operator="<",  # Invalid operator
                rhs=5.0,
            )


class TestIntegerObjective:
    """Test IntegerObjective model."""

    def test_minimize_objective(self):
        """Test creating minimize objective."""
        objective = IntegerObjective(
            sense="minimize",
            coefficients={"x1": 3.0, "x2": 2.0},
        )
        assert objective.sense == "minimize"
        assert objective.coefficients == {"x1": 3.0, "x2": 2.0}

    def test_maximize_objective(self):
        """Test creating maximize objective."""
        objective = IntegerObjective(
            sense="maximize",
            coefficients={"x1": 5.0, "x2": 4.0},
        )
        assert objective.sense == "maximize"

    def test_empty_coefficients(self):
        """Test creating objective with empty coefficients."""
        with pytest.raises(ValueError, match="Objective must have at least one coefficient"):
            IntegerObjective(sense="minimize", coefficients={})

    def test_invalid_sense(self):
        """Test creating objective with invalid sense."""
        with pytest.raises(ValueError):
            IntegerObjective(sense="invalid", coefficients={"x1": 1.0})


class TestIntegerProgramInput:
    """Test IntegerProgramInput model."""

    def test_valid_integer_program_input(self):
        """Test creating valid integer program input."""
        objective = IntegerObjective(sense="maximize", coefficients={"x1": 3.0, "x2": 2.0})
        variables = {
            "x1": IntegerVariable(name="x1", type="integer", lower=0.0, upper=10.0),
            "x2": IntegerVariable(name="x2", type="binary"),
        }
        constraints = [
            IntegerConstraint(expression={"x1": 2.0, "x2": 1.0}, operator="<=", rhs=20.0),
        ]

        input_data = IntegerProgramInput(
            objective=objective,
            variables=variables,
            constraints=constraints,
            solver="SCIP",
            time_limit_seconds=60.0,
            gap_tolerance=0.01,
        )

        assert input_data.objective == objective
        assert len(input_data.variables) == 2
        assert len(input_data.constraints) == 1
        assert input_data.solver == "SCIP"
        assert input_data.time_limit_seconds == 60.0
        assert input_data.gap_tolerance == 0.01

    def test_input_defaults(self):
        """Test integer program input with default values."""
        objective = IntegerObjective(sense="minimize", coefficients={"x1": 1.0})
        variables = {"x1": IntegerVariable(name="x1", type="integer")}
        constraints = [IntegerConstraint(expression={"x1": 1.0}, operator=">=", rhs=0.0)]

        input_data = IntegerProgramInput(
            objective=objective,
            variables=variables,
            constraints=constraints,
        )

        assert input_data.solver == "SCIP"
        assert input_data.time_limit_seconds is None
        assert input_data.gap_tolerance is None

    def test_empty_variables(self):
        """Test integer program input with empty variables."""
        objective = IntegerObjective(sense="minimize", coefficients={"x1": 1.0})
        constraints = [IntegerConstraint(expression={"x1": 1.0}, operator=">=", rhs=0.0)]

        with pytest.raises(ValueError, match="Must have at least one variable"):
            IntegerProgramInput(
                objective=objective,
                variables={},
                constraints=constraints,
            )

    def test_empty_constraints(self):
        """Test integer program input with empty constraints."""
        objective = IntegerObjective(sense="minimize", coefficients={"x1": 1.0})
        variables = {"x1": IntegerVariable(name="x1", type="integer")}

        with pytest.raises(ValueError, match="Must have at least one constraint"):
            IntegerProgramInput(
                objective=objective,
                variables=variables,
                constraints=[],
            )

    def test_invalid_solver(self):
        """Test integer program input with invalid solver."""
        objective = IntegerObjective(sense="minimize", coefficients={"x1": 1.0})
        variables = {"x1": IntegerVariable(name="x1", type="integer")}
        constraints = [IntegerConstraint(expression={"x1": 1.0}, operator=">=", rhs=0.0)]

        with pytest.raises(ValueError):
            IntegerProgramInput(
                objective=objective,
                variables=variables,
                constraints=constraints,
                solver="INVALID_SOLVER",
            )

    def test_negative_time_limit(self):
        """Test integer program input with negative time limit."""
        objective = IntegerObjective(sense="minimize", coefficients={"x1": 1.0})
        variables = {"x1": IntegerVariable(name="x1", type="integer")}
        constraints = [IntegerConstraint(expression={"x1": 1.0}, operator=">=", rhs=0.0)]

        with pytest.raises(ValueError):
            IntegerProgramInput(
                objective=objective,
                variables=variables,
                constraints=constraints,
                time_limit_seconds=-1.0,
            )

    def test_invalid_gap_tolerance(self):
        """Test integer program input with invalid gap tolerance."""
        objective = IntegerObjective(sense="minimize", coefficients={"x1": 1.0})
        variables = {"x1": IntegerVariable(name="x1", type="integer")}
        constraints = [IntegerConstraint(expression={"x1": 1.0}, operator=">=", rhs=0.0)]

        with pytest.raises(ValueError):
            IntegerProgramInput(
                objective=objective,
                variables=variables,
                constraints=constraints,
                gap_tolerance=1.5,  # > 1.0
            )


class TestIntegerProgramming:
    """Test Integer Programming functions."""

    def test_simple_integer_program(self):
        """Test simple integer programming problem."""
        input_data = {
            "objective": {
                "sense": "maximize",
                "coefficients": {"x1": 3.0, "x2": 2.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0, "upper": 10.0},
                "x2": {"name": "x2", "type": "integer", "lower": 0.0, "upper": 10.0},
            },
            "constraints": [
                {"expression": {"x1": 2.0, "x2": 1.0}, "operator": "<=", "rhs": 20.0},
                {"expression": {"x1": 1.0, "x2": 3.0}, "operator": "<=", "rhs": 30.0},
            ],
            "solver": "SCIP",
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert result.variables is not None
        assert result.objective_value is not None

    def test_binary_program(self):
        """Test binary programming problem."""
        input_data = {
            "objective": {
                "sense": "maximize",
                "coefficients": {"x1": 5.0, "x2": 3.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "binary"},
                "x2": {"name": "x2", "type": "binary"},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "x2": 1.0}, "operator": "<=", "rhs": 1.0},
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_mixed_integer_program(self):
        """Test mixed integer programming problem."""
        input_data = {
            "objective": {
                "sense": "minimize",
                "coefficients": {"x1": 2.0, "x2": 3.0, "y1": 1.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0},
                "x2": {"name": "x2", "type": "binary"},
                "y1": {"name": "y1", "type": "continuous", "lower": 0.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "y1": 2.0}, "operator": ">=", "rhs": 5.0},
                {"expression": {"x2": 1.0, "y1": 1.0}, "operator": "<=", "rhs": 3.0},
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_equality_constraints(self):
        """Test integer program with equality constraints."""
        input_data = {
            "objective": {
                "sense": "minimize",
                "coefficients": {"x1": 1.0, "x2": 1.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0},
                "x2": {"name": "x2", "type": "integer", "lower": 0.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "x2": 1.0}, "operator": "==", "rhs": 5.0},
                {"expression": {"x1": 2.0, "x2": -1.0}, "operator": ">=", "rhs": 1.0},
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_time_limit(self):
        """Test integer program with time limit."""
        input_data = {
            "objective": {
                "sense": "maximize",
                "coefficients": {"x1": 1.0, "x2": 1.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0, "upper": 100.0},
                "x2": {"name": "x2", "type": "integer", "lower": 0.0, "upper": 100.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "x2": 1.0}, "operator": "<=", "rhs": 150.0},
            ],
            "time_limit_seconds": 1.0,
        }

        result = solve_integer_program(input_data)
        assert result.status in [OptimizationStatus.OPTIMAL, OptimizationStatus.TIME_LIMIT]

    def test_infeasible_program(self):
        """Test infeasible integer programming problem."""
        input_data = {
            "objective": {
                "sense": "maximize",
                "coefficients": {"x1": 1.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0, "upper": 10.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0}, "operator": ">=", "rhs": 15.0},  # Impossible
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.INFEASIBLE

    def test_unbounded_program(self):
        """Test unbounded integer programming problem."""
        input_data = {
            "objective": {
                "sense": "maximize",
                "coefficients": {"x1": 1.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0},  # No upper bound
            },
            "constraints": [
                {"expression": {"x1": -1.0}, "operator": "<=", "rhs": -1.0},  # x1 >= 1
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status in [OptimizationStatus.UNBOUNDED, OptimizationStatus.OPTIMAL]

    def test_unknown_variable_in_constraint(self):
        """Test integer program with unknown variable in constraint."""
        input_data = {
            "objective": {
                "sense": "maximize",
                "coefficients": {"x1": 1.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "unknown_var": 1.0}, "operator": "<=", "rhs": 10.0},
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.ERROR
        assert "Unknown variable" in result.error_message

    def test_unknown_variable_in_objective(self):
        """Test integer program with unknown variable in objective."""
        input_data = {
            "objective": {
                "sense": "maximize",
                "coefficients": {"x1": 1.0, "unknown_var": 2.0},
            },
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0}, "operator": "<=", "rhs": 10.0},
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.ERROR
        assert "Unknown variable" in result.error_message

    def test_invalid_input_data(self):
        """Test integer program with invalid input data."""
        result = solve_integer_program(
            {
                "objective": {"sense": "maximize", "coefficients": {}},  # Empty coefficients
                "variables": {"x1": {"name": "x1", "type": "integer"}},
                "constraints": [{"expression": {"x1": 1.0}, "operator": "<=", "rhs": 10.0}],
            }
        )
        assert result.status == OptimizationStatus.ERROR
        assert "at least one coefficient" in result.error_message


class TestBinaryProgram:
    """Test solve_binary_program wrapper function."""

    def test_binary_program_wrapper(self):
        """Test binary program wrapper function."""
        input_data = {
            "objective": {"sense": "maximize", "coefficients": {"x1": 5.0, "x2": 3.0}},
            "variables": {
                "x1": {"name": "x1", "type": "binary"},
                "x2": {"name": "x2", "type": "binary"},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "x2": 1.0}, "operator": "<=", "rhs": 1.0},
            ],
        }

        result = solve_binary_program(input_data)
        assert result["status"] == "optimal"
        assert "variables" in result


class TestMixedIntegerProgram:
    """Test solve_mixed_integer_program wrapper function."""

    def test_mixed_integer_program_wrapper(self):
        """Test mixed integer program wrapper function."""
        input_data = {
            "objective": {"sense": "minimize", "coefficients": {"x1": 2.0, "y1": 1.0}},
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0},
                "y1": {"name": "y1", "type": "continuous", "lower": 0.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "y1": 2.0}, "operator": ">=", "rhs": 3.0},
            ],
        }

        result = solve_mixed_integer_program(input_data)
        assert result["status"] == "optimal"


class TestRegisterIntegerProgrammingTools:
    """Test MCP tool registration."""

    def test_register_integer_programming_tools(self):
        """Test registering integer programming tools with MCP."""
        mcp_mock = Mock()
        mcp_mock.tool.return_value = lambda func: func  # Mock decorator

        register_integer_programming_tools(mcp_mock)

        # Verify that mcp.tool() was called
        mcp_mock.tool.assert_called()

    def test_mixed_integer_program_tool(self):
        """Test the MCP tool wrapper with real solving."""
        mcp_mock = Mock()
        tool_functions = []

        def mock_tool_decorator():
            def decorator(func):
                tool_functions.append(func)
                return func

            return decorator

        mcp_mock.tool = mock_tool_decorator

        register_integer_programming_tools(mcp_mock)

        # Get the registered tool function
        assert len(tool_functions) == 1
        tool_func = tool_functions[0]

        # Test the tool function with real problem
        variables = {"x1": {"name": "x1", "type": "integer", "lower": 0.0}}
        constraints = [{"expression": {"x1": 1.0}, "operator": "<=", "rhs": 10.0}]
        objective = {"sense": "maximize", "coefficients": {"x1": 1.0}}

        result = tool_func(
            variables=variables,
            constraints=constraints,
            objective=objective,
        )

        # Verify real solving occurred
        assert result["status"] in ["optimal", "feasible"]
        assert "variables" in result
        assert "objective_value" in result
        assert "execution_time" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_single_variable_single_constraint(self):
        """Test integer program with single variable and constraint."""
        input_data = {
            "objective": {"sense": "maximize", "coefficients": {"x1": 1.0}},
            "variables": {"x1": {"name": "x1", "type": "integer", "lower": 0.0, "upper": 10.0}},
            "constraints": [{"expression": {"x1": 1.0}, "operator": "<=", "rhs": 5.0}],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert result.variables["x1"] == 5.0

    def test_zero_coefficient_in_objective(self):
        """Test integer program with zero coefficient in objective."""
        input_data = {
            "objective": {"sense": "maximize", "coefficients": {"x1": 0.0, "x2": 1.0}},
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0, "upper": 10.0},
                "x2": {"name": "x2", "type": "integer", "lower": 0.0, "upper": 10.0},
            },
            "constraints": [
                {"expression": {"x1": 1.0, "x2": 1.0}, "operator": "<=", "rhs": 5.0},
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_zero_coefficient_in_constraint(self):
        """Test integer program with zero coefficient in constraint."""
        input_data = {
            "objective": {"sense": "maximize", "coefficients": {"x1": 1.0, "x2": 1.0}},
            "variables": {
                "x1": {"name": "x1", "type": "integer", "lower": 0.0, "upper": 10.0},
                "x2": {"name": "x2", "type": "integer", "lower": 0.0, "upper": 10.0},
            },
            "constraints": [
                {"expression": {"x1": 0.0, "x2": 1.0}, "operator": "<=", "rhs": 5.0},
            ],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_negative_bounds(self):
        """Test integer program with negative bounds."""
        input_data = {
            "objective": {"sense": "minimize", "coefficients": {"x1": 1.0}},
            "variables": {"x1": {"name": "x1", "type": "integer", "lower": -5.0, "upper": 5.0}},
            "constraints": [{"expression": {"x1": 1.0}, "operator": ">=", "rhs": -3.0}],
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_large_problem(self):
        """Test integer program with many variables and constraints."""
        variables = {}
        objective_coeffs = {}
        constraints = []

        # Create 10 variables
        for i in range(10):
            var_name = f"x{i}"
            variables[var_name] = {"name": var_name, "type": "integer", "lower": 0.0, "upper": 10.0}
            objective_coeffs[var_name] = 1.0

        # Create 5 constraints
        for i in range(5):
            expression = {f"x{j}": 1.0 for j in range(i, i + 3) if j < 10}
            constraints.append(
                {
                    "expression": expression,
                    "operator": "<=",
                    "rhs": 15.0,
                }
            )

        input_data = {
            "objective": {"sense": "maximize", "coefficients": objective_coeffs},
            "variables": variables,
            "constraints": constraints,
        }

        result = solve_integer_program(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
