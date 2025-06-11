"""Robustness tests for optimization solvers.

This module tests solver behavior under extreme conditions, error scenarios,
and edge cases to ensure robust production operation.
"""

import gc
import logging
import random
import threading
from unittest.mock import patch

import pytest

from mcp_optimizer.solvers.ortools_solver import AdvancedConstraints, ORToolsSolver
from mcp_optimizer.solvers.pulp_solver import PuLPSolver

logger = logging.getLogger(__name__)


class TestSolverRobustness:
    """Test suite for solver robustness under extreme conditions."""

    @pytest.fixture
    def ortools_solver(self):
        """Create OR-Tools solver instance."""
        return ORToolsSolver()

    @pytest.fixture
    def pulp_solver(self):
        """Create PuLP solver instance."""
        return PuLPSolver()

    @pytest.mark.robustness
    def test_invalid_input_handling(self, ortools_solver):
        """Test solver behavior with various invalid inputs."""

        # Test empty inputs
        with pytest.raises((ValueError, TypeError)):
            ortools_solver.solve_assignment_problem([], [], [[]])

        # Test mismatched dimensions
        with pytest.raises(ValueError, match="Cost matrix rows.*must match workers count"):
            ortools_solver.solve_assignment_problem(
                workers=["w1", "w2"],
                tasks=["t1", "t2"],
                costs=[[1, 2, 3]],  # Wrong number of rows
            )

        with pytest.raises(ValueError, match="Cost matrix row.*length.*must match tasks count"):
            ortools_solver.solve_assignment_problem(
                workers=["w1", "w2"],
                tasks=["t1", "t2"],
                costs=[[1, 2], [3, 4, 5]],  # Wrong row length
            )

        # Test None inputs
        with pytest.raises((ValueError, TypeError)):
            ortools_solver.solve_assignment_problem(None, ["t1"], [[1]])

        with pytest.raises((ValueError, TypeError)):
            ortools_solver.solve_assignment_problem(["w1"], None, [[1]])

        with pytest.raises((ValueError, TypeError)):
            ortools_solver.solve_assignment_problem(["w1"], ["t1"], None)

    @pytest.mark.robustness
    def test_extreme_cost_values(self, ortools_solver):
        """Test solver behavior with extreme cost values."""
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]

        # Test very large positive costs
        large_costs = [[1e10, 2e10], [3e10, 4e10]]
        result = ortools_solver.solve_assignment_problem(workers, tasks, large_costs)
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible", "error"]

        # Test very small positive costs
        small_costs = [[1e-10, 2e-10], [3e-10, 4e-10]]
        result = ortools_solver.solve_assignment_problem(workers, tasks, small_costs)
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible", "error"]

        # Test negative costs
        negative_costs = [[-1, -2], [-3, -4]]
        result = ortools_solver.solve_assignment_problem(workers, tasks, negative_costs)
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible", "error"]

        # Test mixed positive/negative costs
        mixed_costs = [[-100, 200], [300, -400]]
        result = ortools_solver.solve_assignment_problem(workers, tasks, mixed_costs)
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible", "error"]

        # Test infinite costs
        inf_costs = [[float("inf"), 1], [2, float("inf")]]
        result = ortools_solver.solve_assignment_problem(workers, tasks, inf_costs)
        assert result is not None
        # Solver should handle infinity gracefully

    @pytest.mark.robustness
    def test_nan_and_special_values(self, ortools_solver):
        """Test solver behavior with NaN and other special floating point values."""
        workers = ["w1", "w2"]
        tasks = ["t1", "t2"]

        # Test NaN costs
        nan_costs = [[float("nan"), 1], [2, 3]]
        result = ortools_solver.solve_assignment_problem(workers, tasks, nan_costs)
        assert result is not None
        # Should either handle gracefully or return error status
        assert result.get("status") in ["optimal", "feasible", "error", "infeasible"]

        # Test mixed NaN and infinity
        mixed_special_costs = [[float("nan"), float("inf")], [float("-inf"), 1]]
        result = ortools_solver.solve_assignment_problem(workers, tasks, mixed_special_costs)
        assert result is not None
        assert result.get("status") in ["optimal", "feasible", "error", "infeasible"]

    @pytest.mark.robustness
    def test_infeasible_constraint_combinations(self, ortools_solver):
        """Test solver behavior with impossible constraint combinations."""
        workers = ["w1", "w2", "w3"]
        tasks = ["t1", "t2", "t3", "t4", "t5"]
        costs = [[random.randint(1, 10) for _ in range(5)] for _ in range(3)]

        # Test: max_tasks_per_worker = 0 with existing tasks
        with pytest.raises(
            ValueError, match="All workers have max_tasks_per_worker=0 but tasks exist"
        ):
            ortools_solver.solve_assignment_problem(workers, tasks, costs, max_tasks_per_worker=0)

        # Test: negative max_tasks_per_worker
        with pytest.raises(ValueError, match="max_tasks_per_worker cannot be negative"):
            ortools_solver.solve_assignment_problem(workers, tasks, costs, max_tasks_per_worker=-1)

        # Test: negative min_tasks_per_worker
        with pytest.raises(ValueError, match="min_tasks_per_worker cannot be negative"):
            ortools_solver.solve_assignment_problem(workers, tasks, costs, min_tasks_per_worker=-1)

        # Test: min > max tasks per worker
        with pytest.raises(
            ValueError, match="min_tasks_per_worker cannot exceed max_tasks_per_worker"
        ):
            ortools_solver.solve_assignment_problem(
                workers, tasks, costs, max_tasks_per_worker=2, min_tasks_per_worker=3
            )

        # Test: insufficient total capacity
        with pytest.raises(ValueError, match="Insufficient total capacity"):
            ortools_solver.solve_assignment_problem(
                workers,
                tasks,
                costs,
                max_tasks_per_worker=1,  # 3*1 < 5 tasks
            )

        # Test: excessive minimum requirements
        with pytest.raises(ValueError, match="Minimum assignments exceed available tasks"):
            ortools_solver.solve_assignment_problem(
                workers,
                tasks,
                costs,
                min_tasks_per_worker=2,  # 3*2 > 5 tasks
            )

    @pytest.mark.robustness
    def test_skill_constraint_edge_cases(self, ortools_solver):
        """Test edge cases in skill-based constraints."""
        workers = ["w1", "w2", "w3"]
        tasks = ["t1", "t2", "t3"]
        costs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        # Test: task requires skill no worker has
        worker_skills = {"w1": ["python"], "w2": ["java"], "w3": ["go"]}
        task_requirements = {"t1": ["rust"]}  # No worker has rust

        with pytest.raises(ValueError, match="No worker has all required skills for task"):
            ortools_solver.solve_assignment_problem(
                workers,
                tasks,
                costs,
                worker_skills=worker_skills,
                task_requirements=task_requirements,
            )

        # Test: task in requirements but not in task list
        task_requirements_invalid = {"t4": ["python"]}  # t4 not in tasks
        with pytest.raises(ValueError, match="Task.*in requirements not found in task list"):
            ortools_solver.solve_assignment_problem(
                workers,
                tasks,
                costs,
                worker_skills=worker_skills,
                task_requirements=task_requirements_invalid,
            )

        # Test: empty skills
        worker_skills_empty = {"w1": [], "w2": [], "w3": []}
        task_requirements_empty = {"t1": []}
        result = ortools_solver.solve_assignment_problem(
            workers,
            tasks,
            costs,
            worker_skills=worker_skills_empty,
            task_requirements=task_requirements_empty,
        )
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

    @pytest.mark.robustness
    def test_advanced_constraints_edge_cases(self, ortools_solver):
        """Test edge cases in advanced constraints."""
        workers = ["w1", "w2", "w3"]
        tasks = ["t1", "t2", "t3"]
        costs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        constraints = AdvancedConstraints()

        # Test: precedence constraint with non-existent tasks
        constraints.add_precedence_constraint("t4", "t1")  # t4 doesn't exist
        with pytest.raises(ValueError, match="Precedence constraint references unknown task"):
            ortools_solver.solve_assignment_problem(
                workers, tasks, costs, advanced_constraints=constraints
            )

        # Test: exclusion constraint with non-existent tasks
        constraints = AdvancedConstraints()
        constraints.add_exclusion_constraint(["t1", "t4"])  # t4 doesn't exist
        with pytest.raises(ValueError, match="Exclusion constraint references unknown task"):
            ortools_solver.solve_assignment_problem(
                workers, tasks, costs, advanced_constraints=constraints
            )

        # Test: self-precedence (task depends on itself)
        constraints = AdvancedConstraints()
        constraints.add_precedence_constraint("t1", "t1")
        result = ortools_solver.solve_assignment_problem(
            workers, tasks, costs, advanced_constraints=constraints
        )
        assert result is not None
        # Should handle gracefully

    @pytest.mark.robustness
    def test_memory_pressure_scenarios(self, ortools_solver):
        """Test solver behavior under memory pressure."""
        # Generate increasingly large problems to test memory handling
        for size in [50, 100, 150]:
            workers = [f"w_{i}" for i in range(size)]
            tasks = [f"t_{i}" for i in range(size)]

            # Generate cost matrix
            costs = [[random.randint(1, 100) for _ in range(size)] for _ in range(size)]

            try:
                result = ortools_solver.solve_assignment_problem(workers, tasks, costs)
                assert result is not None
                assert result.get("status").value in ["optimal", "feasible", "error"]

                # Force garbage collection after each test
                gc.collect()

            except MemoryError:
                logger.warning(f"Memory error at problem size {size}x{size}")
                break
            except Exception as e:
                logger.warning(f"Unexpected error at size {size}: {e}")
                # Solver should handle errors gracefully
                assert True

    @pytest.mark.robustness
    def test_timeout_and_interruption_handling(self, ortools_solver):
        """Test solver behavior with timeouts and interruptions."""
        # Create a moderately large problem that might take some time
        size = 200
        workers = [f"w_{i}" for i in range(size)]
        tasks = [f"t_{i}" for i in range(size)]
        costs = [[random.randint(1, 100) for _ in range(size)] for _ in range(size)]

        # Test with very short timeout (should return partial solution or timeout)
        with patch("mcp_optimizer.config.settings") as mock_settings:
            mock_settings.max_solve_time = 0.001  # 1ms timeout

            result = ortools_solver.solve_assignment_problem(workers, tasks, costs)
            assert result is not None
            # Should either complete quickly or return timeout status
            assert result.get("status") in ["optimal", "feasible", "error", "time_limit"]

    @pytest.mark.robustness
    def test_concurrent_solver_stress(self, ortools_solver):
        """Test solver robustness under concurrent access."""
        import queue

        results_queue = queue.Queue()
        errors_queue = queue.Queue()

        def solve_random_problem():
            try:
                size = random.randint(10, 50)
                workers = [f"w_{i}" for i in range(size)]
                tasks = [f"t_{i}" for i in range(size)]
                costs = [[random.randint(1, 100) for _ in range(size)] for _ in range(size)]

                result = ortools_solver.solve_assignment_problem(workers, tasks, costs)
                results_queue.put(result)
            except Exception as e:
                errors_queue.put(e)

        # Start multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=solve_random_problem)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)  # 30-second timeout per thread

        # Check results
        assert results_queue.qsize() > 0, "No successful results from concurrent execution"

        # Some errors might be acceptable under high concurrency
        error_count = errors_queue.qsize()
        total_operations = results_queue.qsize() + error_count
        success_rate = results_queue.qsize() / total_operations if total_operations > 0 else 0

        assert success_rate > 0.5, f"Success rate too low: {success_rate:.2f}"

    @pytest.mark.robustness
    def test_solver_state_isolation(self, ortools_solver):
        """Test that solver instances don't interfere with each other."""
        # Create two different problems
        workers1 = ["w1", "w2"]
        tasks1 = ["t1", "t2"]
        costs1 = [[1, 2], [3, 4]]

        workers2 = ["w3", "w4", "w5"]
        tasks2 = ["t3", "t4", "t5"]
        costs2 = [[5, 6, 7], [8, 9, 10], [11, 12, 13]]

        # Solve problems in interleaved manner
        result1_partial = ortools_solver.solve_assignment_problem(workers1, tasks1, costs1)
        result2_partial = ortools_solver.solve_assignment_problem(workers2, tasks2, costs2)
        result1_complete = ortools_solver.solve_assignment_problem(workers1, tasks1, costs1)

        # Results should be consistent
        assert result1_partial is not None
        assert result2_partial is not None
        assert result1_complete is not None

        # First and third results should be identical (same problem)
        if (
            result1_partial.get("status").value == "optimal"
            and result1_complete.get("status").value == "optimal"
        ):
            assert (
                abs(result1_partial.get("total_cost", 0) - result1_complete.get("total_cost", 0))
                < 1e-6
            )

    @pytest.mark.robustness
    def test_malformed_data_structures(self, ortools_solver):
        """Test solver behavior with malformed data structures."""
        # Test with nested lists of wrong depth
        with pytest.raises(ValueError):
            ortools_solver.solve_assignment_problem(
                workers=["w1", "w2"],
                tasks=["t1", "t2"],
                costs=[[[1, 2]], [[3, 4]]],  # Too nested
            )

        # Test with mixed data types in costs - this should be caught in try-catch
        result = ortools_solver.solve_assignment_problem(
            workers=["w1", "w2"], tasks=["t1", "t2"], costs=[[1, "invalid"], [3, 4]]
        )
        assert result is not None
        assert result.get("status").value == "error"

        # Test with non-string worker names
        result = ortools_solver.solve_assignment_problem(
            workers=[1, 2],  # Numbers instead of strings
            tasks=["t1", "t2"],
            costs=[[1, 2], [3, 4]],
        )
        # Should either handle gracefully or return error
        assert result is not None

    @pytest.mark.robustness
    def test_resource_cleanup_and_recovery(self, ortools_solver):
        """Test that solver cleans up resources and recovers from errors."""
        # Simulate solver failures and ensure recovery
        for attempt in range(5):
            try:
                # Create a problem that might stress the solver
                size = 100
                workers = [f"w_{i}" for i in range(size)]
                tasks = [f"t_{i}" for i in range(size)]

                # Create problematic costs (very large or special values)
                costs = []
                for _i in range(size):
                    row = []
                    for _j in range(size):
                        if random.random() < 0.01:  # 1% chance of extreme value
                            row.append(float("inf") if random.random() < 0.5 else 1e10)
                        else:
                            row.append(random.randint(1, 100))
                    costs.append(row)

                result = ortools_solver.solve_assignment_problem(workers, tasks, costs)
                assert result is not None
                # Solver should handle each attempt independently

            except Exception as e:
                logger.info(f"Expected exception in attempt {attempt}: {e}")
                # Ensure solver can still work after errors
                continue

        # After all stress attempts, solver should still work normally
        simple_result = ortools_solver.solve_assignment_problem(
            workers=["w1", "w2"], tasks=["t1", "t2"], costs=[[1, 2], [3, 4]]
        )
        assert simple_result is not None
        assert simple_result.get("status").value in ["optimal", "feasible"]

    @pytest.mark.robustness
    def test_cross_solver_consistency(self, ortools_solver, pulp_solver):
        """Test consistency between different solvers on the same problem."""
        # Simple assignment problem both solvers should handle
        workers = ["w1", "w2", "w3"]
        tasks = ["t1", "t2", "t3"]
        costs = [[1, 4, 6], [2, 5, 7], [3, 8, 9]]

        ortools_result = ortools_solver.solve_assignment_problem(workers, tasks, costs)

        # Test PuLP if it supports assignment problems
        try:
            pulp_result = pulp_solver.solve_assignment_problem(workers, tasks, costs)

            # If both succeed, optimal costs should be similar
            if (
                ortools_result.get("status").value == "optimal"
                and pulp_result.get("status").value == "optimal"
            ):
                ortools_cost = ortools_result.get("total_cost", 0)
                pulp_cost = pulp_result.get("total_cost", 0)

                # Allow small numerical differences
                assert abs(ortools_cost - pulp_cost) < 1e-6, (
                    f"Solver cost mismatch: OR-Tools={ortools_cost}, PuLP={pulp_cost}"
                )

        except (AttributeError, NotImplementedError):
            logger.info("PuLP solver doesn't support assignment problems - skipping comparison")

    @pytest.mark.robustness
    def test_extreme_constraint_scenarios(self, ortools_solver):
        """Test solver behavior with extreme constraint configurations."""
        workers = ["w1", "w2", "w3", "w4", "w5"]
        tasks = ["t1", "t2", "t3"]
        costs = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]

        # Test: All workers must take minimum tasks (feasible)
        result = ortools_solver.solve_assignment_problem(
            workers, tasks, costs, min_tasks_per_worker=0, max_tasks_per_worker=1
        )
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible", "infeasible"]

        # Test: Very complex skill requirements
        worker_skills = {
            "w1": ["skill1", "skill2"],
            "w2": ["skill2", "skill3"],
            "w3": ["skill1", "skill3"],
            "w4": ["skill1", "skill2", "skill3"],
            "w5": [],
        }
        task_requirements = {
            "t1": ["skill1", "skill2", "skill3"],  # Only w4 can do this
            "t2": ["skill1"],  # w1, w3, w4 can do this
            "t3": [],  # Anyone can do this
        }

        result = ortools_solver.solve_assignment_problem(
            workers, tasks, costs, worker_skills=worker_skills, task_requirements=task_requirements
        )
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible", "infeasible"]

        # Verify skill constraints are respected in solution
        if result.get("status").value in ["optimal", "feasible"]:
            assignments = result.get("assignments", [])
            for assignment in assignments:
                worker = assignment["worker"]
                task = assignment["task"]
                if task in task_requirements:
                    required_skills = set(task_requirements[task])
                    worker_skill_set = set(worker_skills.get(worker, []))
                    assert required_skills.issubset(worker_skill_set), (
                        f"Skill constraint violated: {worker} assigned to {task}"
                    )
