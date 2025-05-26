# Knapsack Selection Problems - Usage Examples

## Description
Knapsack selection problems solve the optimal selection of items with limited capacity to maximize total value or minimize costs.

## Example Prompts for LLM

### Example 1: Classic Knapsack Problem
```
Help me solve a knapsack problem using MCP Optimizer.

I have a backpack with 50 kg capacity and the following items for hiking:

Items:
- Tent: weight 8 kg, value 100 points
- Sleeping bag: weight 3 kg, value 70 points
- Food for 3 days: weight 6 kg, value 90 points
- Water 5L: weight 5 kg, value 80 points
- Stove: weight 2 kg, value 60 points
- First aid kit: weight 1 kg, value 50 points
- Flashlight: weight 0.5 kg, value 40 points
- Spare clothes: weight 4 kg, value 30 points
- Book: weight 1 kg, value 20 points
- Camera: weight 2 kg, value 85 points

Find the optimal set of items to maximize hiking utility.
```

### Example 2: Investment Portfolio with Limited Budget
```
Use MCP Optimizer to select investment projects.

A company has a budget of $10 million for investments in the following projects:

Projects:
- New production line: cost $3M, NPV $5M
- Warehouse modernization: cost $2M, NPV $3.5M
- IT system: cost $1.5M, NPV $2.8M
- Marketing campaign: cost $1M, NPV $1.8M
- Staff training: cost $0.5M, NPV $1.2M
- Research & development: cost $4M, NPV $6M
- Office expansion: cost $2.5M, NPV $3M
- Process automation: cost $3.5M, NPV $4.5M

Additional constraints:
- Maximum 5 projects can be selected
- IT system and automation are interdependent (both or neither)
- Staff training is mandatory if new production line is selected

Maximize total NPV while meeting all constraints.
```

### Example 3: Cargo Container Optimization
```
Solve a container loading problem with MCP Optimizer.

A shipping container has constraints:
- Maximum weight: 25 tons
- Maximum volume: 60 m³

Goods to ship:
- Electronics: 2 tons, 5 m³, value $500,000
- Clothing: 1 ton, 8 m³, value $200,000
- Furniture: 5 tons, 15 m³, value $300,000
- Auto parts: 3 tons, 4 m³, value $400,000
- Books: 4 tons, 6 m³, value $150,000
- Toys: 1.5 tons, 10 m³, value $250,000
- Sports goods: 2.5 tons, 7 m³, value $180,000
- Appliances: 6 tons, 12 m³, value $600,000

Additional conditions:
- Fragile goods (electronics, appliances) cannot be overloaded
- Priority given to goods with high value per kg

Maximize cargo value in the container.
```

### Example 4: Restaurant Menu Planning
```
Help plan a restaurant menu with MCP Optimizer.

The restaurant has constraints:
- Food procurement budget: $10,000/week
- Cooking time: maximum 200 hours/week
- Refrigeration space: 50 m³

Menu dishes:
- Steak: cost $80, time 0.5h, space 0.2 m³, profit $120
- Pasta: cost $20, time 0.3h, space 0.1 m³, profit $40
- Caesar salad: cost $30, time 0.2h, space 0.3 m³, profit $50
- Soup of the day: cost $15, time 0.4h, space 0.1 m³, profit $25
- Grilled fish: cost $60, time 0.4h, space 0.4 m³, profit $90
- Pizza: cost $40, time 0.3h, space 0.2 m³, profit $70
- Dessert: cost $25, time 0.2h, space 0.2 m³, profit $45
- Burger: cost $35, time 0.25h, space 0.3 m³, profit $55

Expected demand (portions/week):
Steak: 50, Pasta: 120, Caesar: 80, Soup: 100, Fish: 60, Pizza: 90, Dessert: 70, Burger: 85

Maximize restaurant profit.
```

### Example 5: Advertising Budget Optimization
```
Optimize advertising budget allocation with MCP Optimizer.

Marketing department has:
- Total budget: $5 million
- Time constraint: 3 months until launch
- Maximum 8 advertising channels

Advertising channels:
- TV advertising: cost $1.5M, reach 2M people, conversion 2%
- Internet advertising: cost $800K, reach 1.5M, conversion 3.5%
- Radio: cost $400K, reach 800K, conversion 1.5%
- Outdoor advertising: cost $600K, reach 1M, conversion 1%
- Social media: cost $300K, reach 1.2M, conversion 4%
- Email marketing: cost $100K, reach 500K, conversion 5%
- Search advertising: cost $500K, reach 800K, conversion 6%
- Influencers: cost $700K, reach 600K, conversion 3%
- Print media: cost $350K, reach 400K, conversion 1.2%
- Trade shows: cost $900K, reach 200K, conversion 8%

Constraints:
- Must include internet advertising
- TV and radio cannot be used simultaneously
- Minimum 3 digital channels

Maximize number of potential customers.
```

### Example 6: Project Team Formation
```
Help form a project team with MCP Optimizer.

IT project requires:
- Salary budget: $200,000/month
- Maximum 12 people in team
- Project duration: 6 months

Available specialists:
- Senior developer: $20K/month, skills 95 points, experience 8 years
- Middle developer: $12K/month, skills 75 points, experience 4 years
- Junior developer: $7K/month, skills 50 points, experience 1 year
- Architect: $25K/month, skills 90 points, experience 10 years
- DevOps engineer: $18K/month, skills 80 points, experience 5 years
- Tester: $10K/month, skills 70 points, experience 3 years
- UI/UX designer: $13K/month, skills 85 points, experience 4 years
- Analyst: $14K/month, skills 75 points, experience 5 years
- Project manager: $16K/month, skills 80 points, experience 6 years
- Technical writer: $9K/month, skills 60 points, experience 2 years

Requirements:
- Minimum 1 architect
- Minimum 3 developers
- Mandatory 1 project manager
- Senior:Middle:Junior ratio = 1:2:1

Maximize total team skill level.
```

### Example 7: Production Program Optimization
```
Optimize production program with MCP Optimizer.

Factory has constraints:
- Working time: 2000 hours/month
- Raw material A: 5000 kg/month
- Raw material B: 3000 kg/month
- Storage space: 1000 m²

Products:
- Product 1: time 2h, material A 5kg, material B 2kg, space 1 m², profit $50
- Product 2: time 3h, material A 3kg, material B 4kg, space 1.5 m², profit $70
- Product 3: time 1.5h, material A 4kg, material B 1kg, space 0.8 m², profit $40
- Product 4: time 4h, material A 6kg, material B 5kg, space 2 m², profit $90
- Product 5: time 2.5h, material A 2kg, material B 3kg, space 1.2 m², profit $60

Market constraints (maximum demand):
- Product 1: 800 units
- Product 2: 500 units
- Product 3: 1000 units
- Product 4: 300 units
- Product 5: 600 units

Additional conditions:
- Product 4 can only be produced if Product 2 is produced
- Minimum 100 units of Product 1 (base product)

Maximize monthly profit.
```

### Example 8: Scientific Research Planning
```
Help plan scientific research with MCP Optimizer.

Research institute has:
- Annual budget: $50 million
- Research time: 10,000 person-hours
- Laboratory equipment: 20 units

Research projects:
- Project A (medicine): budget $8M, time 1500h, equipment 3 units, scientific value 90
- Project B (energy): budget $12M, time 2000h, equipment 5 units, scientific value 95
- Project C (materials): budget $6M, time 1200h, equipment 2 units, scientific value 80
- Project D (AI): budget $10M, time 1800h, equipment 1 unit, scientific value 100
- Project E (ecology): budget $4M, time 800h, equipment 2 units, scientific value 70
- Project F (space): budget $15M, time 2500h, equipment 8 units, scientific value 98
- Project G (biotech): budget $7M, time 1300h, equipment 4 units, scientific value 85
- Project H (quantum): budget $20M, time 3000h, equipment 6 units, scientific value 100

Constraints:
- Maximum 5 projects simultaneously
- Project D requires completion of Project C
- Minimum 1 project in medicine or biotechnology

Maximize total scientific value of research.
```

## Request Structure for MCP Optimizer

```python
# Example for knapsack problem
result = solve_knapsack_problem(
    items=[
        {"name": "Item1", "weight": 10, "value": 60},
        {"name": "Item2", "weight": 20, "value": 100},
        {"name": "Item3", "weight": 30, "value": 120}
    ],
    capacity=50,
    knapsack_type="0-1"  # or "bounded", "unbounded"
)
```

## Typical Activation Phrases

- "Solve a knapsack problem"
- "Select optimal set of items"
- "Maximize value with limited capacity"
- "Optimize selection with limited budget"
- "Find best combination of elements"
- "Help with optimal selection"

## Applications

Selection problems are used in:
- Investment planning
- Logistics and transportation
- Resource management
- Team formation
- Production planning
- Scientific research
- Marketing and advertising 