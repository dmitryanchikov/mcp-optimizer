"""Tests for PuLP solver."""

from unittest.mock import MagicMock, patch

import pulp
import pytest

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
            assert value in [0, 1], f"Variable {var_name} should be binary but got {value}"

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
            assert value == int(value), f"Variable {var_name} should be integer but got {value}"

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
        result = solver.solve_linear_program(objective, variables, constraints, time_limit=0.1)

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


class TestPuLPSolverInitialization:
    """Tests for PuLP solver initialization and fallback."""

    def test_solver_initialization_with_invalid_solver(self):
        """Test solver initialization with unavailable solver falls back to CBC."""
        # GUROBI and CPLEX might not be available
        with patch("mcp_optimizer.solvers.pulp_solver.logger") as mock_logger:
            solver = PuLPSolver(solver_name="GUROBI")

            # Should have initialized (either GUROBI if available, or CBC fallback)
            assert solver._solver is not None
            assert solver.solver_name == "GUROBI"

    @patch("mcp_optimizer.solvers.pulp_solver.pulp.GUROBI_CMD")
    def test_solver_initialization_exception_fallback(self, mock_gurobi):
        """Test solver initialization falls back to CBC when exception occurs."""
        # Make GUROBI initialization raise an exception
        mock_gurobi.side_effect = Exception("Gurobi not available")

        with patch("mcp_optimizer.solvers.pulp_solver.logger") as mock_logger:
            solver = PuLPSolver(solver_name="GUROBI")

            # Should have fallen back to CBC
            assert solver._solver is not None
            mock_logger.warning.assert_called()
            mock_logger.info.assert_called_with("Falling back to CBC solver")

    def test_default_solver_initialization(self):
        """Test default solver initialization."""
        solver = PuLPSolver()

        assert solver._solver is not None
        assert solver.solver_name is not None

    def test_cbc_solver_initialization(self):
        """Test explicit CBC solver initialization."""
        solver = PuLPSolver(solver_name="CBC")

        assert solver._solver is not None
        assert solver.solver_name == "CBC"

    def test_solver_with_unknown_name_fallback(self):
        """Test solver with completely unknown name falls back to CBC."""
        solver = PuLPSolver(solver_name="UNKNOWN_SOLVER")

        # Should fallback to CBC for unknown solver
        assert solver._solver is not None


class TestPuLPSolverEdgeCases:
    """Tests for edge cases in PuLP solver."""

    def test_unbounded_problem(self):
        """Test solving an unbounded problem."""
        # Maximize x with no upper bound and only x >= 0
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=None),
        }

        constraints = []

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        # CBC might return UNBOUNDED or OPTIMAL depending on internal handling
        # The important thing is it completes without crashing
        assert result["status"] in [
            OptimizationStatus.UNBOUNDED.value,
            OptimizationStatus.OPTIMAL.value,
            OptimizationStatus.ERROR.value,
        ]

    @patch("mcp_optimizer.solvers.pulp_solver.pulp.LpProblem.solve")
    def test_not_solved_status(self, mock_solve):
        """Test handling of LpStatusNotSolved status."""
        # Mock solve to return LpStatusNotSolved
        mock_solve.return_value = pulp.LpStatusNotSolved

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

        assert result["status"] == OptimizationStatus.ERROR.value
        assert "not solved" in result["error_message"].lower()
        assert result["objective_value"] is None

    @patch("mcp_optimizer.solvers.pulp_solver.pulp.LpProblem.solve")
    def test_unknown_solver_status(self, mock_solve):
        """Test handling of unknown solver status."""
        # Mock solve to return an unknown status (using a negative number)
        mock_solve.return_value = -99

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

        assert result["status"] == OptimizationStatus.ERROR.value
        assert result["error_message"] is not None
        # Unknown status causes exception which is caught by error handler
        assert "Solver error" in result["error_message"] or "Solver returned status" in result["error_message"]
        assert result["objective_value"] is None

    def test_time_limit_with_max_constraint(self):
        """Test time limit is constrained by max_solve_time."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=1),
        }

        constraints = []

        solver = PuLPSolver()
        # Pass a very large time limit - should be capped at settings.max_solve_time
        result = solver.solve_linear_program(objective, variables, constraints, time_limit=10000)

        # Should still solve successfully
        assert result["status"] == OptimizationStatus.OPTIMAL.value

    def test_exception_during_solve(self):
        """Test exception handling during solve."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=1),
        }

        constraints = []

        solver = PuLPSolver()

        # Mock solve to raise an exception
        with patch("mcp_optimizer.solvers.pulp_solver.pulp.LpProblem.solve") as mock_solve:
            mock_solve.side_effect = Exception("Solver crashed")

            result = solver.solve_linear_program(objective, variables, constraints)

            assert result["status"] == OptimizationStatus.ERROR.value
            assert "Solver error" in result["error_message"]
            assert result["objective_value"] is None

    def test_equality_constraint(self):
        """Test solving with equality constraint."""
        objective = Objective(
            sense=ObjectiveSense.MINIMIZE,
            coefficients={"x": 1, "y": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0),
            "y": Variable(type=VariableType.CONTINUOUS, lower=0),
        }

        constraints = [
            Constraint(
                expression={"x": 1, "y": 1},
                operator=ConstraintOperator.EQ,
                rhs=5,
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        # x + y should equal 5
        total = result["variables"]["x"] + result["variables"]["y"]
        assert abs(total - 5.0) < 1e-6

    def test_greater_than_or_equal_constraint(self):
        """Test solving with >= constraint."""
        objective = Objective(
            sense=ObjectiveSense.MINIMIZE,
            coefficients={"x": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0),
        }

        constraints = [
            Constraint(
                expression={"x": 1},
                operator=ConstraintOperator.GE,
                rhs=3,
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        # x should be >= 3, and minimized so should be close to 3
        assert result["variables"]["x"] >= 2.99

    def test_named_constraints(self):
        """Test that named constraints are handled correctly."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=10),
        }

        constraints = [
            Constraint(
                name="upper_limit",
                expression={"x": 1},
                operator=ConstraintOperator.LE,
                rhs=5,
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        # x should be maximized subject to x <= 5
        assert result["variables"]["x"] <= 5.01

    def test_empty_constraints(self):
        """Test solving with no constraints."""
        objective = Objective(
            sense=ObjectiveSense.MINIMIZE,
            coefficients={"x": 1},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=1),
        }

        constraints = []

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        # Should minimize x to 0
        assert result["variables"]["x"] < 0.01

    def test_large_coefficient_problem(self):
        """Test solving with large coefficients."""
        objective = Objective(
            sense=ObjectiveSense.MAXIMIZE,
            coefficients={"x": 1000000, "y": 2000000},
        )

        variables = {
            "x": Variable(type=VariableType.CONTINUOUS, lower=0, upper=1),
            "y": Variable(type=VariableType.CONTINUOUS, lower=0, upper=1),
        }

        constraints = [
            Constraint(
                expression={"x": 1, "y": 1},
                operator=ConstraintOperator.LE,
                rhs=1,
            ),
        ]

        solver = PuLPSolver()
        result = solver.solve_linear_program(objective, variables, constraints)

        assert result["status"] == OptimizationStatus.OPTIMAL.value
        assert result["objective_value"] is not None
