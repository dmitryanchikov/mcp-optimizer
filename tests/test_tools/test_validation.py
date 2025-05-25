"""Tests for validation tools."""

from mcp_optimizer.tools.validation import (
    validate_assignment_problem,
    validate_linear_program,
)


class TestLinearProgramValidation:
    """Tests for linear program validation."""

    def test_valid_linear_program(self, sample_linear_program):
        """Test validation of valid linear program."""
        result = validate_linear_program(sample_linear_program)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.suggestions) > 0

    def test_missing_objective(self):
        """Test validation with missing objective."""
        data = {"variables": {"x": {"type": "continuous"}}, "constraints": []}

        result = validate_linear_program(data)

        assert not result.is_valid
        assert "Missing required field: objective" in result.errors

    def test_invalid_objective_sense(self):
        """Test validation with invalid objective sense."""
        data = {
            "objective": {"sense": "invalid", "coefficients": {"x": 1}},
            "variables": {"x": {"type": "continuous"}},
            "constraints": [],
        }

        result = validate_linear_program(data)

        assert not result.is_valid
        assert any("sense must be" in error for error in result.errors)

    def test_missing_variables(self):
        """Test validation with missing variables."""
        data = {
            "objective": {"sense": "maximize", "coefficients": {"x": 1}},
            "constraints": [],
        }

        result = validate_linear_program(data)

        assert not result.is_valid
        assert "Missing required field: variables" in result.errors

    def test_undefined_variables_in_objective(self):
        """Test validation with undefined variables in objective."""
        data = {
            "objective": {"sense": "maximize", "coefficients": {"x": 1, "y": 2}},
            "variables": {"x": {"type": "continuous"}},
            "constraints": [],
        }

        result = validate_linear_program(data)

        assert not result.is_valid
        assert any("not defined" in error for error in result.errors)

    def test_no_constraints_warning(self):
        """Test validation with no constraints generates warning."""
        data = {
            "objective": {"sense": "maximize", "coefficients": {"x": 1}},
            "variables": {"x": {"type": "continuous"}},
            "constraints": [],
        }

        result = validate_linear_program(data)

        assert any("unbounded" in warning for warning in result.warnings)


class TestAssignmentProblemValidation:
    """Tests for assignment problem validation."""

    def test_valid_assignment_problem(self, sample_assignment_problem):
        """Test validation of valid assignment problem."""
        result = validate_assignment_problem(sample_assignment_problem)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_workers(self):
        """Test validation with missing workers."""
        data = {"tasks": ["Task1", "Task2"], "costs": [[1, 2], [3, 4]]}

        result = validate_assignment_problem(data)

        assert not result.is_valid
        assert "Missing required field: workers" in result.errors

    def test_mismatched_cost_matrix(self):
        """Test validation with mismatched cost matrix dimensions."""
        data = {
            "workers": ["Alice", "Bob"],
            "tasks": ["Task1", "Task2", "Task3"],
            "costs": [[1, 2], [3, 4]],  # Wrong dimensions
        }

        result = validate_assignment_problem(data)

        assert not result.is_valid
        assert any("must match tasks count" in error for error in result.errors)

    def test_unbalanced_assignment_warning(self):
        """Test validation with unbalanced assignment generates warning."""
        data = {
            "workers": ["Alice", "Bob"],
            "tasks": ["Task1", "Task2", "Task3"],
            "costs": [[1, 2, 3], [4, 5, 6]],
        }

        result = validate_assignment_problem(data)

        assert any("Unbalanced assignment" in warning for warning in result.warnings)
        assert any("dummy" in suggestion for suggestion in result.suggestions)
