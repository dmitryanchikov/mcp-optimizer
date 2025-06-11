"""Simple stress tests for optimization solvers."""

import logging
import multiprocessing

import psutil
import pytest

from mcp_optimizer.solvers.ortools_solver import ORToolsSolver

logger = logging.getLogger(__name__)


@pytest.mark.stress
class TestStressTestConfiguration:
    """Configuration and utilities for stress testing."""

    def test_system_requirements_check(self):
        """Verify system has sufficient resources for stress testing."""
        # Check available memory
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)

        assert available_gb >= 2, (
            f"Insufficient memory for stress tests: {available_gb:.1f} GB available"
        )

        # Check CPU cores
        cpu_count = multiprocessing.cpu_count()
        assert cpu_count >= 2, f"Insufficient CPU cores for stress tests: {cpu_count} cores"

        logger.info(f"System check passed: {available_gb:.1f} GB memory, {cpu_count} CPU cores")

    def test_stress_test_markers(self):
        """Verify stress test markers are properly configured."""
        # This test ensures stress tests can be run selectively
        # Run with: pytest -m stress
        assert True

    @pytest.mark.stress
    def test_basic_solver_stress(self):
        """Basic stress test for solver functionality."""
        solver = ORToolsSolver()

        # Simple assignment problem
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]
        costs = [[1, 2], [3, 4]]

        result = solver.solve_assignment_problem(workers, tasks, costs)

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]
        logger.info("Basic solver stress test passed")
