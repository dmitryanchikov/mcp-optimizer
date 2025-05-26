# Linear Programming - Usage Examples

## Description
Linear programming allows solving optimization problems with linear constraints and linear objective functions.

## Example Prompts for LLM

### Example 1: Production Problem
```
Help me solve a production problem using MCP Optimizer.

I have a factory that produces two types of products: tables and chairs.
- Producing one table requires 4 hours of work and 2 kg of material
- Producing one chair requires 2 hours of work and 1 kg of material
- Profit from a table is $30, from a chair - $20
- 40 hours of work and 20 kg of material are available per day

Find the optimal number of tables and chairs to maximize profit.
```

### Example 2: Diet Problem
```
Use MCP Optimizer to solve a diet planning problem.

I need to create a diet from three foods:
- Bread: 2g protein, 50g carbs, 1g fat per 100g, cost $3/kg
- Meat: 20g protein, 0g carbs, 15g fat per 100g, cost $50/kg
- Milk: 3g protein, 5g carbs, 3g fat per 100g, cost $6/kg

Requirements:
- Minimum 60g protein per day
- Minimum 300g carbs per day
- Maximum 50g fat per day

Find the minimum cost diet.
```

### Example 3: Transportation Problem
```
Solve a transportation problem using MCP Optimizer.

A company has 3 warehouses and 4 stores:

Warehouses (supply):
- Warehouse A: 100 units
- Warehouse B: 150 units
- Warehouse C: 200 units

Stores (demand):
- Store 1: 80 units
- Store 2: 120 units
- Store 3: 100 units
- Store 4: 150 units

Transportation costs ($/unit):
From A: [5, 8, 6, 9]
From B: [7, 4, 5, 8]
From C: [6, 7, 4, 6]

Find the optimal delivery plan with minimum costs.
```

### Example 4: Blending Problem
```
Help solve a fuel blending problem with MCP Optimizer.

An oil refinery produces gasoline by blending 4 components:
- Component A: octane rating 95, cost $4.5/liter
- Component B: octane rating 87, cost $3.8/liter
- Component C: octane rating 92, cost $4.2/liter
- Component D: octane rating 98, cost $5.0/liter

Requirements for the final gasoline:
- Octane rating at least 91
- Production volume 1000 liters
- Component A should be at most 40% of the blend
- Component D should be at least 10% of the blend

Find the optimal blend composition to minimize cost.
```

## Request Structure for MCP Optimizer

For all problems, use the following structure:

```json
{
  "objective": {
    "sense": "maximize" | "minimize",
    "coefficients": {"variable1": coefficient1, "variable2": coefficient2}
  },
  "variables": {
    "variable1": {"type": "continuous", "lower": 0, "upper": null},
    "variable2": {"type": "continuous", "lower": 0, "upper": null}
  },
  "constraints": [
    {
      "expression": {"variable1": coefficient1, "variable2": coefficient2},
      "operator": "<=",
      "rhs": right_hand_side
    }
  ]
}
```

## Typical Activation Phrases

- "Solve a linear programming problem"
- "Find the optimal solution for..."
- "Maximize/minimize subject to constraints..."
- "Help with production/resource/cost optimization"
- "Create an optimal plan..." 