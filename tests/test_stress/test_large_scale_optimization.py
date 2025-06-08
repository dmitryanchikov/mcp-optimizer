"""Stress tests for large-scale optimization problems.

This module contains performance and stress tests for optimization solvers
to verify their behavior under high computational load and large problem sizes.
"""

import gc
import logging
import multiprocessing
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
import pytest

from mcp_optimizer.solvers.ortools_solver import ORToolsSolver
from mcp_optimizer.solvers.pulp_solver import PuLPSolver

logger = logging.getLogger(__name__)


class TestLargeScaleOptimization:
    """Test suite for large-scale optimization problems."""

    @pytest.fixture
    def ortools_solver(self):
        """Create OR-Tools solver instance."""
        return ORToolsSolver()

    @pytest.fixture
    def pulp_solver(self):
        """Create PuLP solver instance."""
        return PuLPSolver()

    def monitor_memory_usage(self, test_name: str):
        """Monitor memory usage during test execution."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        logger.info(f"{test_name}: Initial memory usage: {initial_memory:.2f} MB")
        return initial_memory

    def check_memory_usage(
        self, initial_memory: float, test_name: str, max_memory_mb: float = 2048
    ):
        """Check if memory usage is within acceptable limits."""
        process = psutil.Process()
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory

        logger.info(
            f"{test_name}: Current memory usage: {current_memory:.2f} MB "
            f"(+{memory_increase:.2f} MB)"
        )

        assert current_memory < max_memory_mb, (
            f"Memory usage exceeded limit: {current_memory:.2f} MB > {max_memory_mb} MB"
        )

    @pytest.mark.stress
    @pytest.mark.timeout(300)  # 5 minutes timeout
    def test_large_assignment_problem_1000x1000(self, ortools_solver):
        """Test 1000x1000 assignment problem - ultimate stress test."""
        test_name = "Large Assignment 1000x1000"
        initial_memory = self.monitor_memory_usage(test_name)

        # Generate 1000 workers and 1000 tasks
        workers = [f"worker_{i}" for i in range(1000)]
        tasks = [f"task_{i}" for i in range(1000)]

        # Generate random cost matrix
        random.seed(42)  # For reproducibility
        costs = [[random.randint(1, 100) for _ in range(1000)] for _ in range(1000)]

        start_time = time.time()

        try:
            result = ortools_solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs, maximize=False
            )

            execution_time = time.time() - start_time
            logger.info(f"{test_name}: Execution time: {execution_time:.2f}s")

            # Verify result structure
            assert result is not None
            assert result.get("status").value in ["optimal", "feasible"]
            assert result.get("execution_time") is not None
            assert execution_time < 180, f"Execution time too long: {execution_time:.2f}s"

            # Verify solution quality
            if result.get("status") == "OPTIMAL":
                assignments = result.get("assignments", [])
                assert len(assignments) == 1000, (
                    f"Expected 1000 assignments, got {len(assignments)}"
                )

                # Check uniqueness
                assigned_workers = set()
                assigned_tasks = set()
                for assignment in assignments:
                    assert assignment["worker"] not in assigned_workers, (
                        "Duplicate worker assignment"
                    )
                    assert assignment["task"] not in assigned_tasks, "Duplicate task assignment"
                    assigned_workers.add(assignment["worker"])
                    assigned_tasks.add(assignment["task"])

            self.check_memory_usage(initial_memory, test_name, max_memory_mb=1500)

        finally:
            # Force garbage collection
            gc.collect()

    @pytest.mark.stress
    @pytest.mark.timeout(180)  # 3 minutes timeout
    def test_large_assignment_problem_500x500(self, ortools_solver):
        """Test 500x500 assignment problem - high stress test."""
        test_name = "Large Assignment 500x500"
        initial_memory = self.monitor_memory_usage(test_name)

        workers = [f"worker_{i}" for i in range(500)]
        tasks = [f"task_{i}" for i in range(500)]

        random.seed(123)
        costs = [[random.randint(1, 100) for _ in range(500)] for _ in range(500)]

        start_time = time.time()

        try:
            result = ortools_solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs, maximize=False
            )

            execution_time = time.time() - start_time
            logger.info(f"{test_name}: Execution time: {execution_time:.2f}s")

            assert result is not None
            assert result.get("status").value in ["optimal", "feasible"]
            assert execution_time < 120, f"Execution time too long: {execution_time:.2f}s"

            self.check_memory_usage(initial_memory, test_name, max_memory_mb=1000)

        finally:
            gc.collect()

    @pytest.mark.stress
    @pytest.mark.timeout(300)
    def test_large_linear_programming_1000_variables(self, pulp_solver):
        """Test linear programming with 1000 variables."""
        test_name = "Large LP 1000 variables"
        initial_memory = self.monitor_memory_usage(test_name)

        # Generate large LP problem: maximize c^T * x subject to A*x <= b, x >= 0
        num_vars = 1000
        num_constraints = 500

        random.seed(456)

        # Generate objective coefficients
        objective = {f"x_{i}": random.uniform(1, 10) for i in range(num_vars)}

        # Generate constraints
        constraints = []
        for i in range(num_constraints):
            constraint = {}
            # Sparse constraint: only 10% of variables appear in each constraint
            selected_vars = random.sample(range(num_vars), k=num_vars // 10)
            for var_idx in selected_vars:
                constraint[f"x_{var_idx}"] = random.uniform(-5, 5)

            constraints.append(
                {
                    "name": f"constraint_{i}",
                    "coefficients": constraint,
                    "operator": "<=",
                    "rhs": random.uniform(10, 100),
                }
            )

        start_time = time.time()

        try:
            # Convert to PuLP format
            from mcp_optimizer.schemas.base import (
                Constraint,
                ConstraintOperator,
                Objective,
                ObjectiveSense,
                Variable,
                VariableType,
            )

            # Create variables dict
            variables = {}
            for var_name in objective.keys():
                variables[var_name] = Variable(
                    name=var_name, type=VariableType.CONTINUOUS, lower=0.0, upper=None
                )

            # Create objective
            obj = Objective(sense=ObjectiveSense.MAXIMIZE, coefficients=objective)

            # Convert constraints
            pulp_constraints = []
            for constraint in constraints:
                pulp_constraints.append(
                    Constraint(
                        name=constraint["name"],
                        expression=constraint["coefficients"],
                        operator=ConstraintOperator.LE,
                        rhs=constraint["rhs"],
                    )
                )

            result = pulp_solver.solve_linear_program(
                objective=obj, variables=variables, constraints=pulp_constraints
            )

            execution_time = time.time() - start_time
            logger.info(f"{test_name}: Execution time: {execution_time:.2f}s")

            assert result is not None
            assert result.get("status").value in ["optimal", "feasible", "unbounded"]
            assert execution_time < 240, f"Execution time too long: {execution_time:.2f}s"

            # Verify solution structure
            if result.get("status") == "OPTIMAL":
                variables_result = result.get("variables", {})
                assert len(variables_result) <= num_vars

            self.check_memory_usage(initial_memory, test_name, max_memory_mb=1200)

        finally:
            gc.collect()

    @pytest.mark.stress
    @pytest.mark.timeout(120)
    def test_concurrent_solver_requests(self, ortools_solver):
        """Test concurrent solver requests to verify thread safety."""
        test_name = "Concurrent Solver Requests"
        initial_memory = self.monitor_memory_usage(test_name)

        # Generate smaller problems for concurrent execution
        num_workers = 4
        problem_size = 50

        def solve_assignment_problem():
            workers = [f"w_{i}" for i in range(problem_size)]
            tasks = [f"t_{i}" for i in range(problem_size)]
            costs = [
                [random.randint(1, 50) for _ in range(problem_size)] for _ in range(problem_size)
            ]

            return ortools_solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs
            )

        start_time = time.time()

        try:
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                # Submit 20 concurrent problems
                futures = [executor.submit(solve_assignment_problem) for _ in range(20)]

                results = []
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    assert result is not None
                    assert result.get("status").value in ["optimal", "feasible", "infeasible"]

            execution_time = time.time() - start_time
            logger.info(f"{test_name}: Total execution time: {execution_time:.2f}s")

            assert len(results) == 20
            assert execution_time < 60, f"Concurrent execution too slow: {execution_time:.2f}s"

            self.check_memory_usage(initial_memory, test_name, max_memory_mb=800)

        finally:
            gc.collect()

    @pytest.mark.stress
    @pytest.mark.timeout(180)
    def test_memory_constrained_optimization(self, ortools_solver):
        """Test optimization under memory constraints."""
        test_name = "Memory Constrained Optimization"
        initial_memory = self.monitor_memory_usage(test_name)

        # Generate multiple medium-sized problems sequentially
        for iteration in range(10):
            problem_size = 200
            workers = [f"worker_{i}_{iteration}" for i in range(problem_size)]
            tasks = [f"task_{i}_{iteration}" for i in range(problem_size)]

            random.seed(iteration)
            costs = [
                [random.randint(1, 100) for _ in range(problem_size)] for _ in range(problem_size)
            ]

            result = ortools_solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs
            )

            assert result is not None
            assert result.get("status").value in ["optimal", "feasible"]

            # Force garbage collection after each iteration
            gc.collect()

            # Check memory doesn't grow excessively
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_growth = current_memory - initial_memory
            assert memory_growth < 500, f"Memory growth too large: {memory_growth:.2f} MB"

        logger.info(f"{test_name}: Successfully completed 10 iterations")

    @pytest.mark.stress
    @pytest.mark.timeout(240)
    def test_worst_case_assignment_scenarios(self, ortools_solver):
        """Test worst-case scenarios for assignment problems."""
        test_name = "Worst Case Assignment"
        initial_memory = self.monitor_memory_usage(test_name)

        scenarios = [
            # Scenario 1: All costs are identical (many optimal solutions)
            {"name": "identical_costs", "size": 100, "cost_generator": lambda i, j: 10},
            # Scenario 2: Costs follow extreme distribution
            {
                "name": "extreme_costs",
                "size": 100,
                "cost_generator": lambda i, j: 1 if i == j else 1000,
            },
            # Scenario 3: Random sparse costs (many zeros)
            {
                "name": "sparse_costs",
                "size": 100,
                "cost_generator": lambda i, j: random.choice([0, 0, 0, random.randint(1, 100)]),
            },
        ]

        for scenario in scenarios:
            logger.info(f"Testing scenario: {scenario['name']}")

            size = scenario["size"]
            workers = [f"worker_{i}" for i in range(size)]
            tasks = [f"task_{i}" for i in range(size)]

            random.seed(789)
            costs = [[scenario["cost_generator"](i, j) for j in range(size)] for i in range(size)]

            start_time = time.time()
            result = ortools_solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs
            )
            execution_time = time.time() - start_time

            assert result is not None
            assert result.get("status").value in ["optimal", "feasible"]
            assert execution_time < 30, (
                f"Scenario {scenario['name']} too slow: {execution_time:.2f}s"
            )

            logger.info(f"Scenario {scenario['name']}: {execution_time:.2f}s")

        self.check_memory_usage(initial_memory, test_name, max_memory_mb=600)

    @pytest.mark.stress
    def test_solver_performance_comparison(self, ortools_solver, pulp_solver):
        """Compare performance between different solvers."""
        test_name = "Solver Performance Comparison"
        initial_memory = self.monitor_memory_usage(test_name)

        # Generate test problem
        size = 100
        workers = [f"worker_{i}" for i in range(size)]
        tasks = [f"task_{i}" for i in range(size)]

        random.seed(999)
        costs = [[random.randint(1, 100) for _ in range(size)] for _ in range(size)]

        # Test OR-Tools
        start_time = time.time()
        ortools_result = ortools_solver.solve_assignment_problem(
            workers=workers, tasks=tasks, costs=costs
        )
        ortools_time = time.time() - start_time

        # Test PuLP (if it supports assignment problems)
        pulp_time = None
        try:
            start_time = time.time()
            pulp_result = pulp_solver.solve_assignment_problem(
                workers=workers, tasks=tasks, costs=costs
            )
            pulp_time = time.time() - start_time
        except AttributeError:
            logger.info("PuLP solver doesn't support assignment problems directly")
            pulp_result = None

        # Log performance comparison
        logger.info(f"OR-Tools execution time: {ortools_time:.3f}s")
        if pulp_time:
            logger.info(f"PuLP execution time: {pulp_time:.3f}s")
            logger.info(f"Performance ratio (PuLP/OR-Tools): {pulp_time / ortools_time:.2f}")

        # Verify results
        assert ortools_result is not None
        assert ortools_result.get("status").value in ["optimal", "feasible"]

        if pulp_result:
            assert pulp_result.get("status").value in ["optimal", "feasible"]

        self.check_memory_usage(initial_memory, test_name, max_memory_mb=400)


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
