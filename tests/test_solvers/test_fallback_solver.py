"""Tests for fallback solver when OR-Tools is not available."""

import platform
from unittest.mock import patch

import pytest

from mcp_optimizer.solvers.fallback_solver import FallbackSolver


class TestFallbackSolverInit:
    """Tests for FallbackSolver initialization."""

    def test_init(self):
        """Test FallbackSolver initialization."""
        solver = FallbackSolver()
        assert solver is not None
        assert solver.solver_name == "Fallback"

    def test_solver_name_attribute(self):
        """Test that solver_name is set correctly."""
        solver = FallbackSolver()
        assert hasattr(solver, "solver_name")
        assert isinstance(solver.solver_name, str)
        assert solver.solver_name == "Fallback"


class TestGetInstallationMessage:
    """Tests for platform-specific installation messages."""

    @patch("platform.system", return_value="Darwin")
    def test_get_installation_message_macos(self, mock_system):
        """Test installation message for macOS."""
        solver = FallbackSolver()
        message = solver._get_installation_message()

        assert "OR-Tools is not available" in message
        assert "macOS" in message
        assert "brew install or-tools" in message
        assert "pip install ortools" in message
        assert "python -m venv venv" in message
        assert "uvx" in message
        assert "native library paths" in message

    @patch("platform.system", return_value="Linux")
    def test_get_installation_message_linux(self, mock_system):
        """Test installation message for Linux."""
        solver = FallbackSolver()
        message = solver._get_installation_message()

        assert "OR-Tools is not available" in message
        assert "pip install ortools" in message
        # Linux message should be simpler than macOS
        assert "brew install" not in message
        assert "macOS" not in message

    @patch("platform.system", return_value="Windows")
    def test_get_installation_message_windows(self, mock_system):
        """Test installation message for Windows."""
        solver = FallbackSolver()
        message = solver._get_installation_message()

        assert "OR-Tools is not available" in message
        assert "pip install ortools" in message
        # Windows message should be simpler than macOS
        assert "brew install" not in message
        assert "macOS" not in message

    def test_get_installation_message_real_platform(self):
        """Test installation message with actual platform."""
        solver = FallbackSolver()
        message = solver._get_installation_message()

        # Should always contain basic message
        assert "OR-Tools is not available" in message
        assert "pip install ortools" in message

        # Platform-specific checks
        current_platform = platform.system()
        if current_platform == "Darwin":
            assert "macOS" in message
            assert "brew install" in message
        else:
            assert "brew install" not in message


class TestSolveAssignmentProblem:
    """Tests for solve_assignment_problem fallback method."""

    def test_solve_assignment_problem_returns_error(self):
        """Test that solve_assignment_problem returns error result."""
        solver = FallbackSolver()
        result = solver.solve_assignment_problem()

        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert result["error_message"] is not None
        assert "OR-Tools is not available" in result["error_message"]
        assert result["total_cost"] is None
        assert result["assignments"] == []
        assert result["execution_time"] == 0.0

    def test_solve_assignment_problem_ignores_arguments(self):
        """Test that solve_assignment_problem ignores all arguments."""
        solver = FallbackSolver()

        # Should handle any arguments gracefully
        result = solver.solve_assignment_problem(
            workers=["A", "B"],
            tasks=["T1", "T2"],
            costs=[[1, 2], [3, 4]],
            maximize=False,
        )

        assert result["status"] == "error"
        assert "OR-Tools is not available" in result["error_message"]

    def test_solve_assignment_problem_with_args(self):
        """Test solve_assignment_problem with positional args."""
        solver = FallbackSolver()
        result = solver.solve_assignment_problem("arg1", "arg2", "arg3")

        assert result["status"] == "error"
        assert result["assignments"] == []

    def test_solve_assignment_problem_result_structure(self):
        """Test that result has all required fields."""
        solver = FallbackSolver()
        result = solver.solve_assignment_problem()

        required_fields = ["status", "error_message", "total_cost", "assignments", "execution_time"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"


class TestSolveTransportationProblem:
    """Tests for solve_transportation_problem fallback method."""

    def test_solve_transportation_problem_returns_error(self):
        """Test that solve_transportation_problem returns error result."""
        solver = FallbackSolver()
        result = solver.solve_transportation_problem()

        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert result["error_message"] is not None
        assert "OR-Tools is not available" in result["error_message"]
        assert result["total_cost"] is None
        assert result["flows"] == []
        assert result["execution_time"] == 0.0

    def test_solve_transportation_problem_ignores_arguments(self):
        """Test that solve_transportation_problem ignores all arguments."""
        solver = FallbackSolver()

        # Should handle any arguments gracefully
        result = solver.solve_transportation_problem(
            suppliers=["S1", "S2"],
            consumers=["C1", "C2"],
            costs=[[1, 2], [3, 4]],
            supply=[10, 20],
            demand=[15, 15],
        )

        assert result["status"] == "error"
        assert "OR-Tools is not available" in result["error_message"]

    def test_solve_transportation_problem_with_args(self):
        """Test solve_transportation_problem with positional args."""
        solver = FallbackSolver()
        result = solver.solve_transportation_problem("arg1", "arg2")

        assert result["status"] == "error"
        assert result["flows"] == []

    def test_solve_transportation_problem_result_structure(self):
        """Test that result has all required fields."""
        solver = FallbackSolver()
        result = solver.solve_transportation_problem()

        required_fields = ["status", "error_message", "total_cost", "flows", "execution_time"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"


class TestFallbackSolverIntegration:
    """Integration tests for FallbackSolver behavior."""

    def test_fallback_solver_consistent_error_messages(self):
        """Test that error messages are consistent across methods."""
        solver = FallbackSolver()

        assignment_result = solver.solve_assignment_problem()
        transportation_result = solver.solve_transportation_problem()

        # Both should have the same error message
        assert (
            assignment_result["error_message"]
            == transportation_result["error_message"]
        )

    def test_fallback_solver_multiple_calls(self):
        """Test that FallbackSolver can be called multiple times."""
        solver = FallbackSolver()

        # Multiple calls should all return errors
        for _ in range(3):
            result1 = solver.solve_assignment_problem()
            result2 = solver.solve_transportation_problem()

            assert result1["status"] == "error"
            assert result2["status"] == "error"

    @patch("platform.system", return_value="Darwin")
    def test_fallback_solver_macos_specific_integration(self, mock_system):
        """Test FallbackSolver behavior on macOS."""
        solver = FallbackSolver()

        result = solver.solve_assignment_problem()

        assert result["status"] == "error"
        assert "brew install" in result["error_message"]
        assert "macOS" in result["error_message"]

    @patch("platform.system", return_value="Linux")
    def test_fallback_solver_linux_specific_integration(self, mock_system):
        """Test FallbackSolver behavior on Linux."""
        solver = FallbackSolver()

        result = solver.solve_transportation_problem()

        assert result["status"] == "error"
        assert "pip install ortools" in result["error_message"]
        assert "brew install" not in result["error_message"]


class TestFallbackSolverEdgeCases:
    """Edge case tests for FallbackSolver."""

    def test_fallback_solver_with_none_arguments(self):
        """Test that FallbackSolver handles None arguments."""
        solver = FallbackSolver()

        result = solver.solve_assignment_problem(None, None, None)
        assert result["status"] == "error"

    def test_fallback_solver_with_empty_kwargs(self):
        """Test FallbackSolver with empty keyword arguments."""
        solver = FallbackSolver()

        result = solver.solve_assignment_problem(**{})
        assert result["status"] == "error"

    def test_fallback_solver_with_mixed_args_kwargs(self):
        """Test FallbackSolver with mixed args and kwargs."""
        solver = FallbackSolver()

        result = solver.solve_transportation_problem(
            "arg1", "arg2", kwarg1="value1", kwarg2="value2"
        )
        assert result["status"] == "error"

    def test_fallback_solver_instance_independence(self):
        """Test that multiple FallbackSolver instances are independent."""
        solver1 = FallbackSolver()
        solver2 = FallbackSolver()

        result1 = solver1.solve_assignment_problem()
        result2 = solver2.solve_assignment_problem()

        # Results should be identical
        assert result1["status"] == result2["status"]
        assert result1["error_message"] == result2["error_message"]

    def test_fallback_solver_type_annotations(self):
        """Test that FallbackSolver methods return correct types."""
        solver = FallbackSolver()

        assignment_result = solver.solve_assignment_problem()
        transportation_result = solver.solve_transportation_problem()

        assert isinstance(assignment_result, dict)
        assert isinstance(transportation_result, dict)
        assert isinstance(assignment_result["status"], str)
        assert isinstance(assignment_result["assignments"], list)
        assert isinstance(transportation_result["flows"], list)
