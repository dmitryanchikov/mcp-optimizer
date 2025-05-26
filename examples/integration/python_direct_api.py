#!/usr/bin/env python3
"""
MCP Optimizer - Direct Python API Examples

This module demonstrates direct usage of the mcp-optimizer package
for various optimization problems.

Installation:
    pip install mcp-optimizer

Usage:
    python python_direct_api.py
"""

import logging
import time
from dataclasses import dataclass

# Import mcp-optimizer components
try:
    from mcp_optimizer import (
        AssignmentSolver,
        KnapsackSolver,
        LinearProgrammingSolver,
        OptimizationEngine,
        OptimizationResult,
        PortfolioOptimizer,
        RoutingSolver,
        SolverConfig,
        TransportationSolver,
    )
except ImportError:
    print(
        "Error: mcp-optimizer package not found. Install with: pip install mcp-optimizer"
    )
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ExampleResult:
    """Container for example execution results."""

    name: str
    success: bool
    execution_time: float
    result: OptimizationResult | None = None
    error: str | None = None


class MCPOptimizerExamples:
    """Comprehensive examples for MCP Optimizer direct API usage."""

    def __init__(self):
        """Initialize the examples class with default configuration."""
        self.config = SolverConfig(
            timeout=300,  # 5 minutes
            max_iterations=10000,
            tolerance=1e-6,
            threads=4,
        )
        self.results: list[ExampleResult] = []

    def run_all_examples(self) -> list[ExampleResult]:
        """Run all optimization examples and return results."""
        logger.info("Starting MCP Optimizer examples...")

        examples = [
            self.linear_programming_example,
            self.assignment_problem_example,
            self.transportation_problem_example,
            self.knapsack_problem_example,
            self.routing_problem_example,
            self.portfolio_optimization_example,
            self.multi_objective_example,
            self.batch_processing_example,
        ]

        for example in examples:
            try:
                start_time = time.time()
                result = example()
                execution_time = time.time() - start_time

                self.results.append(
                    ExampleResult(
                        name=example.__name__,
                        success=True,
                        execution_time=execution_time,
                        result=result,
                    )
                )
                logger.info(f"✅ {example.__name__} completed in {execution_time:.3f}s")

            except Exception as e:
                execution_time = time.time() - start_time
                self.results.append(
                    ExampleResult(
                        name=example.__name__,
                        success=False,
                        execution_time=execution_time,
                        error=str(e),
                    )
                )
                logger.error(f"❌ {example.__name__} failed: {e}")

        return self.results

    def linear_programming_example(self) -> OptimizationResult:
        """
        Example: Production Planning

        A factory produces two products with limited resources.
        Maximize profit subject to resource constraints.
        """
        logger.info("Running Linear Programming example...")

        solver = LinearProgrammingSolver(config=self.config)

        # Problem: Maximize 3x1 + 2x2
        # Subject to: x1 + x2 <= 4, 2x1 + x2 <= 6, x1,x2 >= 0
        problem = {
            "objective": {"coefficients": [3, 2], "direction": "maximize"},
            "constraints": [
                {"coefficients": [1, 1], "operator": "<=", "value": 4},
                {"coefficients": [2, 1], "operator": "<=", "value": 6},
            ],
            "bounds": [(0, None), (0, None)],
            "variable_names": ["Product_A", "Product_B"],
        }

        result = solver.solve(problem)

        logger.info(f"Optimal profit: ${result.objective_value:.2f}")
        logger.info(
            f"Production plan: {dict(zip(problem['variable_names'], result.variables, strict=False))}"
        )

        return result

    def assignment_problem_example(self) -> OptimizationResult:
        """
        Example: Employee-Task Assignment

        Assign 4 employees to 4 tasks to minimize total cost.
        """
        logger.info("Running Assignment Problem example...")

        solver = AssignmentSolver(config=self.config)

        # Cost matrix: employees x tasks
        cost_matrix = [
            [9, 2, 7, 8],  # Employee 1
            [6, 4, 3, 7],  # Employee 2
            [5, 8, 1, 8],  # Employee 3
            [7, 6, 9, 4],  # Employee 4
        ]

        problem = {
            "cost_matrix": cost_matrix,
            "employee_names": ["Alice", "Bob", "Charlie", "Diana"],
            "task_names": ["Task_A", "Task_B", "Task_C", "Task_D"],
        }

        result = solver.solve(problem)

        logger.info(f"Minimum total cost: ${result.objective_value}")

        # Display assignments
        assignments = result.get_assignments()
        for emp, task in assignments.items():
            logger.info(f"{emp} → {task}")

        return result

    def transportation_problem_example(self) -> OptimizationResult:
        """
        Example: Supply Chain Optimization

        Transport goods from suppliers to customers minimizing cost.
        """
        logger.info("Running Transportation Problem example...")

        solver = TransportationSolver(config=self.config)

        problem = {
            "supply": [300, 400, 500],  # Supplier capacities
            "demand": [250, 350, 300, 300],  # Customer demands
            "costs": [
                [8, 6, 10, 9],  # Supplier 1 to customers
                [9, 12, 13, 7],  # Supplier 2 to customers
                [14, 9, 16, 5],  # Supplier 3 to customers
            ],
            "supplier_names": ["Warehouse_A", "Warehouse_B", "Warehouse_C"],
            "customer_names": ["Store_1", "Store_2", "Store_3", "Store_4"],
        }

        result = solver.solve(problem)

        logger.info(f"Minimum transportation cost: ${result.objective_value}")

        # Display transportation plan
        plan = result.get_transportation_plan()
        for route, quantity in plan.items():
            if quantity > 0:
                logger.info(f"{route}: {quantity} units")

        return result

    def knapsack_problem_example(self) -> OptimizationResult:
        """
        Example: Investment Portfolio Selection

        Select investments to maximize return within budget constraint.
        """
        logger.info("Running Knapsack Problem example...")

        solver = KnapsackSolver(config=self.config)

        # Investment opportunities
        investments = [
            {"name": "Tech_Startup", "cost": 100000, "return": 150000},
            {"name": "Real_Estate", "cost": 200000, "return": 250000},
            {"name": "Bonds", "cost": 50000, "return": 60000},
            {"name": "Stocks", "cost": 80000, "return": 120000},
            {"name": "Commodities", "cost": 120000, "return": 160000},
        ]

        problem = {
            "items": [
                {
                    "name": inv["name"],
                    "weight": inv["cost"],
                    "value": inv["return"] - inv["cost"],  # Net profit
                }
                for inv in investments
            ],
            "capacity": 300000,  # Budget constraint
            "knapsack_type": "0-1",  # Binary selection
        }

        result = solver.solve(problem)

        logger.info(f"Maximum profit: ${result.objective_value}")

        selected_items = result.get_selected_items()
        total_investment = sum(item["weight"] for item in selected_items)
        logger.info(f"Total investment: ${total_investment}")
        logger.info("Selected investments:")
        for item in selected_items:
            logger.info(f"  - {item['name']}: ${item['value']} profit")

        return result

    def routing_problem_example(self) -> OptimizationResult:
        """
        Example: Delivery Route Optimization (TSP)

        Find shortest route visiting all customers and returning to depot.
        """
        logger.info("Running Routing Problem example...")

        solver = RoutingSolver(config=self.config)

        # Distance matrix between locations
        locations = ["Depot", "Customer_A", "Customer_B", "Customer_C", "Customer_D"]
        distance_matrix = [
            [0, 10, 15, 20, 25],  # From Depot
            [10, 0, 35, 25, 30],  # From Customer_A
            [15, 35, 0, 30, 20],  # From Customer_B
            [20, 25, 30, 0, 15],  # From Customer_C
            [25, 30, 20, 15, 0],  # From Customer_D
        ]

        problem = {
            "distance_matrix": distance_matrix,
            "locations": locations,
            "start_location": 0,  # Start from depot
            "problem_type": "TSP",
        }

        result = solver.solve(problem)

        logger.info(f"Shortest route distance: {result.objective_value}")

        route = result.get_route()
        route_names = [locations[i] for i in route]
        logger.info(f"Optimal route: {' → '.join(route_names)}")

        return result

    def portfolio_optimization_example(self) -> OptimizationResult:
        """
        Example: Modern Portfolio Theory

        Optimize asset allocation to maximize return for given risk level.
        """
        logger.info("Running Portfolio Optimization example...")

        optimizer = PortfolioOptimizer(config=self.config)

        # Historical returns and covariance matrix
        assets = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        expected_returns = [0.12, 0.15, 0.10, 0.14, 0.20]

        # Simplified covariance matrix
        covariance_matrix = [
            [0.04, 0.02, 0.01, 0.02, 0.03],
            [0.02, 0.06, 0.02, 0.03, 0.04],
            [0.01, 0.02, 0.03, 0.01, 0.02],
            [0.02, 0.03, 0.01, 0.05, 0.03],
            [0.03, 0.04, 0.02, 0.03, 0.08],
        ]

        problem = {
            "assets": assets,
            "expected_returns": expected_returns,
            "covariance_matrix": covariance_matrix,
            "target_return": 0.13,
            "risk_tolerance": 0.05,
            "constraints": {
                "min_weight": 0.05,  # Minimum 5% in each asset
                "max_weight": 0.40,  # Maximum 40% in each asset
            },
        }

        result = optimizer.solve(problem)

        logger.info(f"Portfolio return: {result.expected_return:.2%}")
        logger.info(f"Portfolio risk: {result.risk:.2%}")
        logger.info("Asset allocation:")

        for asset, weight in zip(assets, result.weights, strict=False):
            logger.info(f"  {asset}: {weight:.1%}")

        return result

    def multi_objective_example(self) -> OptimizationResult:
        """
        Example: Multi-Objective Optimization

        Optimize multiple conflicting objectives simultaneously.
        """
        logger.info("Running Multi-Objective Optimization example...")

        engine = OptimizationEngine(config=self.config)

        # Example: Minimize cost and maximize quality
        problem = {
            "objectives": [
                {
                    "coefficients": [2, 3, 1],
                    "direction": "minimize",
                    "weight": 0.6,
                },  # Cost
                {
                    "coefficients": [1, 2, 3],
                    "direction": "maximize",
                    "weight": 0.4,
                },  # Quality
            ],
            "constraints": [
                {"coefficients": [1, 1, 1], "operator": "<=", "value": 100},
                {"coefficients": [2, 1, 3], "operator": ">=", "value": 50},
            ],
            "bounds": [(0, 50), (0, 50), (0, 50)],
            "variable_names": ["Product_X", "Product_Y", "Product_Z"],
        }

        result = engine.solve_multi_objective(problem)

        logger.info("Pareto optimal solution found")
        logger.info(f"Weighted objective value: {result.objective_value:.2f}")

        for name, value in zip(
            problem["variable_names"], result.variables, strict=False
        ):
            logger.info(f"{name}: {value:.2f}")

        return result

    def batch_processing_example(self) -> list[OptimizationResult]:
        """
        Example: Batch Processing Multiple Problems

        Solve multiple optimization problems efficiently.
        """
        logger.info("Running Batch Processing example...")

        engine = OptimizationEngine(config=self.config)

        # Create multiple similar problems with different parameters
        problems = []
        for i in range(5):
            problem = {
                "objective": {"coefficients": [3 + i, 2 + i], "direction": "maximize"},
                "constraints": [
                    {"coefficients": [1, 1], "operator": "<=", "value": 4 + i},
                    {"coefficients": [2, 1], "operator": "<=", "value": 6 + i},
                ],
                "bounds": [(0, None), (0, None)],
                "problem_id": f"batch_problem_{i + 1}",
            }
            problems.append(problem)

        # Solve all problems in batch
        results = engine.solve_batch(problems, parallel=True)

        logger.info(f"Solved {len(results)} problems in batch")

        for i, result in enumerate(results):
            logger.info(f"Problem {i + 1}: Objective = {result.objective_value:.2f}")

        return results

    def print_summary(self):
        """Print summary of all example results."""
        print("\n" + "=" * 60)
        print("MCP OPTIMIZER EXAMPLES SUMMARY")
        print("=" * 60)

        successful = sum(1 for r in self.results if r.success)
        total = len(self.results)

        print(f"Total examples: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success rate: {successful / total * 100:.1f}%")

        print("\nDetailed Results:")
        print("-" * 60)

        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} {result.name:<30} ({result.execution_time:.3f}s)")

            if not result.success and result.error:
                print(f"     Error: {result.error}")

        total_time = sum(r.execution_time for r in self.results)
        print(f"\nTotal execution time: {total_time:.3f}s")


def main():
    """Main function to run all examples."""
    print("MCP Optimizer - Direct Python API Examples")
    print("=" * 50)

    # Create examples instance
    examples = MCPOptimizerExamples()

    # Run all examples
    results = examples.run_all_examples()

    # Print summary
    examples.print_summary()

    # Example of accessing specific results
    print("\nExample: Accessing specific results")
    print("-" * 40)

    for result in results:
        if result.success and result.result:
            print(f"{result.name}: {result.result.objective_value:.2f}")


if __name__ == "__main__":
    main()
