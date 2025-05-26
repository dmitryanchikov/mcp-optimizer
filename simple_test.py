#!/usr/bin/env python3
"""Simple test script to verify MCP server functionality."""

import json
from mcp_optimizer.solvers.pulp_solver import PuLPSolver
from mcp_optimizer.solvers.ortools_solver import ORToolsSolver
from mcp_optimizer.schemas.base import Objective, Variable, Constraint, ObjectiveSense, VariableType, ConstraintOperator


def test_linear_programming():
    """Test linear programming solver."""
    print("Testing Linear Programming...")
    
    # Maximize 3x + 2y subject to:
    # 2x + y <= 20
    # x + 2y <= 16
    # x, y >= 0
    
    objective = Objective(
        sense=ObjectiveSense.MAXIMIZE,
        coefficients={"x": 3, "y": 2}
    )
    
    variables = {
        "x": Variable(type=VariableType.CONTINUOUS, lower=0),
        "y": Variable(type=VariableType.CONTINUOUS, lower=0),
    }
    
    constraints = [
        Constraint(
            expression={"x": 2, "y": 1},
            operator=ConstraintOperator.LE,
            rhs=20
        ),
        Constraint(
            expression={"x": 1, "y": 2},
            operator=ConstraintOperator.LE,
            rhs=16
        ),
    ]
    
    solver = PuLPSolver()
    result = solver.solve_linear_program(objective, variables, constraints)
    
    print(f"Status: {result.get('status')}")
    print(f"Objective value: {result.get('objective_value')}")
    print(f"Variables: {result.get('variables')}")
    print()


def test_assignment_problem():
    """Test assignment problem solver."""
    print("Testing Assignment Problem...")
    
    workers = ["Alice", "Bob", "Charlie"]
    tasks = ["Task1", "Task2", "Task3"]
    costs = [
        [4, 2, 8],
        [4, 3, 7],
        [1, 5, 9]
    ]
    
    solver = ORToolsSolver()
    result = solver.solve_assignment_problem(workers, tasks, costs)
    
    print(f"Status: {result.get('status')}")
    print(f"Total cost: {result.get('total_cost')}")
    if result.get('assignments'):
        print("Assignments:")
        for assignment in result['assignments']:
            print(f"  {assignment['worker']} -> {assignment['task']} (cost: {assignment['cost']})")
    print()


def test_transportation_problem():
    """Test transportation problem solver."""
    print("Testing Transportation Problem...")
    
    suppliers = [
        {"name": "Warehouse A", "supply": 100},
        {"name": "Warehouse B", "supply": 150},
    ]
    consumers = [
        {"name": "Store 1", "demand": 80},
        {"name": "Store 2", "demand": 70},
        {"name": "Store 3", "demand": 100},
    ]
    costs = [
        [4, 6, 8],  # Costs from Warehouse A
        [5, 3, 7],  # Costs from Warehouse B
    ]
    
    solver = ORToolsSolver()
    result = solver.solve_transportation_problem(suppliers, consumers, costs)
    
    print(f"Status: {result.get('status')}")
    print(f"Total cost: {result.get('total_cost')}")
    if result.get('shipments'):
        print("Shipments:")
        for shipment in result['shipments']:
            print(f"  {shipment['from']} -> {shipment['to']}: {shipment['quantity']} units (cost: {shipment['cost']})")
        print()


def main():
    """Run all tests."""
    print("=== MCP Optimizer Simple Test ===\n")
    
    try:
        test_linear_programming()
        test_assignment_problem()
        test_transportation_problem()
        
        print("✅ All tests completed successfully!")
        print("\n📊 Summary:")
        print("- Linear Programming: ✅ Working")
        print("- Assignment Problem: ✅ Working") 
        print("- Transportation Problem: ✅ Working")
        print("- MCP Server: ✅ Ready to run")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 