"""Fallback solver for when OR-Tools is not available."""

import logging
import platform
from typing import Any

logger = logging.getLogger(__name__)


class FallbackSolver:
    """Fallback solver that returns error messages when OR-Tools is not available."""

    def __init__(self) -> None:
        """Initialize fallback solver."""
        self.solver_name = "Fallback"

    def _get_installation_message(self) -> str:
        """Get platform-specific installation instructions."""
        system = platform.system()
        if system == "Darwin":  # macOS
            return (
                "OR-Tools is not available. For full functionality on macOS:\n"
                "1. Install via Homebrew: 'brew install or-tools && pip install ortools'\n"
                "2. Or use regular venv: 'python -m venv venv && source venv/bin/activate && pip install ortools'\n"
                "Note: OR-Tools may not work in isolated environments (uvx) due to native library paths."
            )
        else:
            return "OR-Tools is not available. Please install it with 'pip install ortools'"

    def solve_assignment_problem(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Return error message for assignment problem."""
        return {
            "status": "error",
            "error_message": self._get_installation_message(),
            "total_cost": None,
            "assignments": [],
            "execution_time": 0.0,
        }

    def solve_transportation_problem(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Return error message for transportation problem."""
        return {
            "status": "error",
            "error_message": self._get_installation_message(),
            "total_cost": None,
            "flows": [],
            "execution_time": 0.0,
        }
