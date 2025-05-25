"""Tests for linear programming tools."""


from mcp_optimizer.schemas.base import (
    Constraint,
    ConstraintOperator,
    Objective,
    ObjectiveSense,
    Variable,
    VariableType,
)
from mcp_optimizer.solvers.pulp_solver import PuLPSolver


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
        result = solver.solve_linear_program(
            objective, variables, constraints, time_limit=0.1
        )

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
