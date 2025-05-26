# Assignment Problems - Usage Examples

## Description
Assignment problems solve the optimal allocation of resources (workers, machines, tasks) to minimize total costs or maximize efficiency.

## Example Prompts for LLM

### Example 1: Employee-Project Assignment
```
Help me solve an employee assignment problem using MCP Optimizer.

I have 4 employees and 4 projects. Each employee can work on any project, but with different efficiency (rating from 1 to 10):

Employees: Alex, Maria, Dmitry, Elena
Projects: Website, Mobile App, Database, Analytics

Efficiency matrix:
- Alex: [9, 6, 7, 5]
- Maria: [7, 9, 6, 8]
- Dmitry: [8, 7, 9, 6]
- Elena: [6, 8, 7, 9]

Find the optimal assignment to maximize total efficiency.
```

### Example 2: Machine-Order Assignment
```
Use MCP Optimizer to solve a production machine assignment problem.

A factory has 5 machines and 5 orders. Execution time for each order on each machine (in hours):

Machines: A, B, C, D, E
Orders: Order1, Order2, Order3, Order4, Order5

Execution time matrix:
- Machine A: [12, 15, 13, 11, 14]
- Machine B: [10, 12, 14, 13, 11]
- Machine C: [14, 11, 10, 12, 15]
- Machine D: [13, 14, 12, 10, 13]
- Machine E: [11, 13, 15, 14, 12]

Find the assignment that minimizes total production time.
```

### Example 3: Driver-Route Assignment
```
Solve a driver-route assignment problem with MCP Optimizer.

A transportation company has 6 drivers and 6 routes. Cost of assigning each driver to a route (in dollars):

Drivers: John, Peter, Sergey, Andrew, Michael, Nicholas
Routes: NYC-Boston, NYC-Philadelphia, NYC-Washington, NYC-Chicago, NYC-Atlanta, NYC-Miami

Cost matrix:
- John: [500, 450, 600, 800, 400, 350]
- Peter: [480, 420, 580, 780, 420, 380]
- Sergey: [520, 480, 620, 820, 380, 320]
- Andrew: [460, 400, 560, 760, 440, 400]
- Michael: [540, 500, 640, 840, 360, 300]
- Nicholas: [440, 380, 540, 740, 460, 420]

Find the assignment with minimum total costs.
```

### Example 4: Task-Team Assignment
```
Help distribute tasks among development teams with MCP Optimizer.

The IT department has 3 teams and 3 major tasks. Complexity assessment (complexity points):

Teams: Frontend, Backend, DevOps
Tasks: New Interface, API Integration, Infrastructure

Complexity matrix:
- Frontend: [3, 8, 9]
- Backend: [7, 2, 6]
- DevOps: [9, 5, 1]

Find the assignment that minimizes total project complexity.
```

## Request Structure for MCP Optimizer

```python
# Example function call
result = solve_assignment_problem(
    workers=["Worker1", "Worker2", "Worker3"],
    tasks=["Task1", "Task2", "Task3"],
    costs=[
        [cost_1_1, cost_1_2, cost_1_3],
        [cost_2_1, cost_2_2, cost_2_3],
        [cost_3_1, cost_3_2, cost_3_3]
    ]
)
```

## Typical Activation Phrases

- "Solve an assignment problem"
- "Optimally distribute employees/resources"
- "Find optimal assignment for..."
- "Minimize assignment costs"
- "Maximize distribution efficiency"
- "Help with optimal task distribution"

## Applications

Assignment problems are used in:
- Personnel management
- Production planning
- Logistics and transportation
- Computational resource allocation
- Project planning 