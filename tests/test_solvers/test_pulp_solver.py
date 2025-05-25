"""Tests for PuLP solver."""


from mcp_optimizer.schemas.base import (
    Constraint,
    ConstraintOperator,
    Objective,
    ObjectiveSense,
    OptimizationStatus,
    Variable,
    VariableType,
)
from mcp_optimizer.solvers.pulp_solver import PuLPSolver


class TestPuLPSolver:
    """Tests for PuLP solver."""

    def test_simple_linear_program(self):
        """Test solving a simple linear program."""
        # Maximize 3x + 2y subject to 2x + y <= 20, x + 3y <= 30, x,y >= 0
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

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["objective_value"] is not None
        assert result["objective_value"] > 0
        assert "x" in result["variables"]
        assert "y" in result["variables"]
        assert result["execution_time"] > 0

    def test_infeasible_problem(self):
        """Test solving an infeasible problem."""
        # Maximize x subject to x <= -1, x >= 0 (infeasible)
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
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.INFEASIBLE.value
        assert result["objective_value"] is None
        assert result["error_message"] is not None

    def test_binary_variables(self):
        """Test solving with binary variables."""
        # Binary knapsack: maximize 10*item1 + 15*item2 subject to 5*item1 + 8*item2 <= 10
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
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["objective_value"] is not None

        # Check that variables are binary (0 or 1)
        for var_name, value in result["variables"].items():
            assert value in [0, 1], (
                f"Variable {var_name} should be binary but got {value}"
            )

    def test_integer_variables(self):
        """Test solving with integer variables."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1, "y": 1},
        )

        variables = {
            "x": Variable(type=VariableType.INTEGER, lower=0, upper=5),
            "y": Variable(type=VariableType.INTEGER, lower=0, upper=3),
        }

        constraints = [
            Constraint(
                expression={"x": 1, "y": 2},
                operator=ConstraintOperator.LE,
                rhs=7,
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.OPTIMAL.value

        # Check that variables are integers
        for var_name, value in result["variables"].items():
            assert value == int(value), (
                f"Variable {var_name} should be integer but got {value}"
            )

    def test_mixed_variable_types(self):
        """Test solving with mixed variable types."""
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
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] in [
            OptimizationStatus.OPTIMAL.value,
            OptimizationStatus.FEASIBLE.value,
        ]

        # Check variable types
        if "y" in result["variables"]:
            assert result["variables"]["y"] == int(result["variables"]["y"])
        if "z" in result["variables"]:
            assert result["variables"]["z"] in [0, 1]

    def test_time_limit(self):
        """Test solver with time limit."""
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
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(
            objective, variables, constraints, time_limit=0.1
        )

        # Should still solve this simple problem quickly
        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["execution_time"] <= 1.0  # Should be much faster than 1 second

    def test_solver_info(self):
        """Test that solver info is included in results."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=1),
        }

        constraints = []

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert "solver_info" in result
        assert result["solver_info"]["solver_name"] is not None
        assert isinstance(result["solver_info"], dict)
