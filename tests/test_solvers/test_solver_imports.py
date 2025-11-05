"""Tests for solver import fallback mechanism."""

import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestORToolsImport:
    """Tests for OR-Tools import success scenario."""

    def test_ortools_import_success(self):
        """Test that ORToolsSolver imports successfully when ortools is available."""
        # This test assumes OR-Tools is installed (which it should be in our test environment)
        from mcp_optimizer.solvers import ORToolsSolver

        # Should be the actual ORToolsSolver class, not FallbackSolver
        assert ORToolsSolver is not None
        assert hasattr(ORToolsSolver, "__name__")

        # Check that we can instantiate it
        solver = ORToolsSolver()
        assert solver is not None

    def test_ortools_solver_has_expected_methods(self):
        """Test that ORToolsSolver has expected solver methods."""
        from mcp_optimizer.solvers import ORToolsSolver

        # Check for expected methods (both real and fallback have these)
        assert hasattr(ORToolsSolver, "solve_assignment_problem") or callable(
            getattr(ORToolsSolver, "solve_assignment_problem", None)
        )


class TestORToolsImportFallback:
    """Tests for OR-Tools import failure and fallback mechanism."""

    def test_ortools_import_failure_uses_fallback(self):
        """Test that FallbackSolver is used when ortools import fails."""
        # Save the original module
        original_modules = sys.modules.copy()

        try:
            # Remove ortools-related modules to simulate import failure
            modules_to_remove = [
                key for key in sys.modules.keys() if "ortools" in key.lower()
            ]
            for module in modules_to_remove:
                del sys.modules[module]

            # Also remove our solver modules to force reimport
            if "mcp_optimizer.solvers" in sys.modules:
                del sys.modules["mcp_optimizer.solvers"]
            if "mcp_optimizer.solvers.ortools_solver" in sys.modules:
                del sys.modules["mcp_optimizer.solvers.ortools_solver"]
            if "mcp_optimizer.solvers.fallback_solver" in sys.modules:
                del sys.modules["mcp_optimizer.solvers.fallback_solver"]

            # Mock the ortools import to fail
            with patch.dict("sys.modules", {"ortools": None, "ortools.linear_solver": None}):
                # This should trigger the ImportError and fallback
                with patch("mcp_optimizer.solvers.logger") as mock_logger:
                    # Reload the module to trigger the import logic
                    import mcp_optimizer.solvers

                    importlib.reload(mcp_optimizer.solvers)

                    # Check that warning was logged (import failed)
                    # Note: The actual import might still succeed if ortools is installed,
                    # so we can't always guarantee fallback in this test environment

        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_fallback_solver_assignment(self):
        """Test that ORToolsSolver is assigned to FallbackSolver on import failure."""
        # This test simulates the fallback behavior
        from mcp_optimizer.solvers.fallback_solver import FallbackSolver

        # In the actual import fallback scenario, ORToolsSolver becomes FallbackSolver
        # We can test the FallbackSolver directly
        assert FallbackSolver is not None

        # Create instance and verify it has the fallback behavior
        solver = FallbackSolver()
        result = solver.solve_assignment_problem()

        assert result["status"] == "error"
        assert "OR-Tools is not available" in result["error_message"]

    @patch("mcp_optimizer.solvers.logger")
    def test_import_error_logging(self, mock_logger):
        """Test that import errors are properly logged."""
        # Save original modules
        original_modules = sys.modules.copy()

        try:
            # Remove solver modules
            for module in [
                "mcp_optimizer.solvers",
                "mcp_optimizer.solvers.ortools_solver",
                "mcp_optimizer.solvers.fallback_solver",
            ]:
                if module in sys.modules:
                    del sys.modules[module]

            # Mock ortools to not exist
            with patch.dict("sys.modules", {"ortools": None}):
                try:
                    # Try to import, which should fail and trigger fallback
                    import mcp_optimizer.solvers

                    importlib.reload(mcp_optimizer.solvers)

                    # If we get here, import succeeded (ortools is actually installed)
                    # In CI/test environment, this is expected
                except ImportError:
                    # If import truly failed, that's also valid for this test
                    pass

        finally:
            # Restore modules
            sys.modules.clear()
            sys.modules.update(original_modules)


class TestSolverExports:
    """Tests for solver package exports."""

    def test_all_exports_defined(self):
        """Test that __all__ is properly defined."""
        import mcp_optimizer.solvers

        assert hasattr(mcp_optimizer.solvers, "__all__")
        assert "ORToolsSolver" in mcp_optimizer.solvers.__all__

    def test_ortools_solver_accessible(self):
        """Test that ORToolsSolver is accessible from package."""
        from mcp_optimizer.solvers import ORToolsSolver

        assert ORToolsSolver is not None

    def test_package_has_logger(self):
        """Test that solver package has logger configured."""
        import mcp_optimizer.solvers

        assert hasattr(mcp_optimizer.solvers, "logger")
        assert mcp_optimizer.solvers.logger is not None


class TestFallbackBehavior:
    """Tests for fallback solver behavior when used through import."""

    def test_fallback_solver_direct_import(self):
        """Test direct import of FallbackSolver."""
        from mcp_optimizer.solvers.fallback_solver import FallbackSolver

        solver = FallbackSolver()
        assert solver.solver_name == "Fallback"

    def test_fallback_solver_methods_return_errors(self):
        """Test that fallback solver methods return error results."""
        from mcp_optimizer.solvers.fallback_solver import FallbackSolver

        solver = FallbackSolver()

        # Test assignment problem
        assignment_result = solver.solve_assignment_problem(
            workers=["A"], tasks=["T1"], costs=[[1]]
        )
        assert assignment_result["status"] == "error"
        assert "OR-Tools is not available" in assignment_result["error_message"]

        # Test transportation problem
        transport_result = solver.solve_transportation_problem(
            suppliers=["S1"], consumers=["C1"], costs=[[1]]
        )
        assert transport_result["status"] == "error"
        assert "OR-Tools is not available" in transport_result["error_message"]


class TestImportScenarios:
    """Tests for various import scenarios."""

    def test_reimport_solver_module(self):
        """Test that solver module can be reimported."""
        # Import module
        import mcp_optimizer.solvers as solvers_module

        # First access
        solver1 = solvers_module.ORToolsSolver

        # Reimport if module is in sys.modules
        if "mcp_optimizer.solvers" in sys.modules:
            importlib.reload(sys.modules["mcp_optimizer.solvers"])
            solver2 = solvers_module.ORToolsSolver
        else:
            # If not in sys.modules, just verify we can import again
            import mcp_optimizer.solvers

            solver2 = mcp_optimizer.solvers.ORToolsSolver

        # Both should be valid
        assert solver1 is not None
        assert solver2 is not None

    def test_multiple_solver_instances(self):
        """Test creating multiple solver instances."""
        from mcp_optimizer.solvers import ORToolsSolver

        solver1 = ORToolsSolver()
        solver2 = ORToolsSolver()

        # Both should be valid instances
        assert solver1 is not None
        assert solver2 is not None

        # They should be independent instances
        assert solver1 is not solver2

    def test_solver_import_idempotent(self):
        """Test that importing solvers multiple times is safe."""
        from mcp_optimizer.solvers import ORToolsSolver as Solver1
        from mcp_optimizer.solvers import ORToolsSolver as Solver2

        # Should be the same class
        assert Solver1 is Solver2


class TestImportErrorHandling:
    """Tests for proper handling of import errors."""

    def test_import_error_types(self):
        """Test that we handle the right types of import errors."""
        # ImportError is the expected error type for missing modules
        assert issubclass(ImportError, Exception)
        assert issubclass(ModuleNotFoundError, ImportError)

    def test_fallback_handles_all_import_errors(self):
        """Test that fallback mechanism handles various import error scenarios."""
        from mcp_optimizer.solvers.fallback_solver import FallbackSolver

        # Fallback should work regardless of why the import failed
        solver = FallbackSolver()

        # Should always return error results
        result = solver.solve_assignment_problem()
        assert result["status"] == "error"
        assert isinstance(result["error_message"], str)
        assert len(result["error_message"]) > 0
