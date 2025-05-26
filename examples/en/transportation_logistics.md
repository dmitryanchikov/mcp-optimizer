# Transportation & Logistics - Usage Examples

## Description
Transportation and logistics problems optimize the movement of goods, route planning, and supply chain management to minimize costs and delivery times.

## Example Prompts for LLM

### Example 1: Classic Transportation Problem
```
Help me solve a transportation problem using MCP Optimizer.

A company has 3 factories and 4 warehouses:

Factories (production in tons):
- Factory A: 300 tons
- Factory B: 400 tons
- Factory C: 500 tons

Warehouses (demand in tons):
- Warehouse 1: 250 tons
- Warehouse 2: 350 tons
- Warehouse 3: 300 tons
- Warehouse 4: 300 tons

Transportation costs ($/ton):
From A: [8, 6, 10, 9]
From B: [9, 12, 13, 7]
From C: [14, 9, 16, 5]

Find the transportation plan with minimum costs.
```

### Example 2: Multi-Product Logistics
```
Use MCP Optimizer to optimize multi-product supply operations.

A company supplies 3 types of goods from 2 distribution centers to 4 stores:

Products: Electronics, Clothing, Food

Distribution Centers (inventory):
- DC New York: [500, 800, 1200] units
- DC Chicago: [400, 600, 1000] units

Stores (demand):
- Store 1: [200, 300, 400] units
- Store 2: [150, 250, 350] units
- Store 3: [300, 400, 500] units
- Store 4: [250, 450, 950] units

Transportation costs by product ($/unit):
Electronics - from NY: [15, 18, 12, 20], from Chicago: [25, 10, 22, 16]
Clothing - from NY: [8, 10, 6, 12], from Chicago: [14, 5, 11, 8]
Food - from NY: [3, 4, 2, 5], from Chicago: [6, 2, 4, 3]

Minimize total logistics costs.
```

### Example 3: Supply Chain Planning
```
Solve a supply chain planning problem with MCP Optimizer.

The supply network includes:
- 2 raw material suppliers
- 3 manufacturing plants
- 4 distribution centers
- 5 retail locations

Suppliers (capacity tons/month):
- Supplier 1: 1000 tons
- Supplier 2: 1500 tons

Plants (capacity tons/month):
- Plant A: 800 tons
- Plant B: 900 tons
- Plant C: 700 tons

Distribution Centers (capacity):
- DC 1: 600 tons
- DC 2: 500 tons
- DC 3: 550 tons
- DC 4: 650 tons

Retail Locations (demand):
- Store 1: 300 tons
- Store 2: 250 tons
- Store 3: 400 tons
- Store 4: 350 tons
- Store 5: 200 tons

Transportation costs:
Suppliers → Plants: [[20, 25, 30], [22, 20, 28]]
Plants → DCs: [[15, 18, 20, 16], [17, 15, 19, 18], [19, 16, 15, 20]]
DCs → Stores: [[10, 12, 8, 11, 14], [11, 9, 10, 13, 12], [13, 11, 9, 10, 15], [12, 14, 11, 9, 13]]

Optimize the entire supply chain to minimize total costs.
```

### Example 4: Fleet Planning
```
Help optimize fleet utilization with MCP Optimizer.

A transportation company has:
- 5 types of trucks with different capacities
- 8 delivery routes
- Time and fuel constraints

Truck Types:
- Small (3 tons): 10 units, 12 L/100km consumption, $80/day cost
- Medium (5 tons): 8 units, 18 L/100km consumption, $120/day cost
- Large (8 tons): 6 units, 25 L/100km consumption, $180/day cost
- Semi (15 tons): 4 units, 35 L/100km consumption, $250/day cost
- Heavy (20 tons): 2 units, 40 L/100km consumption, $300/day cost

Routes (cargo in tons, distance in km):
- Route 1: 12 tons, 150 km
- Route 2: 8 tons, 200 km
- Route 3: 25 tons, 300 km
- Route 4: 6 tons, 100 km
- Route 5: 18 tons, 250 km
- Route 6: 4 tons, 80 km
- Route 7: 30 tons, 400 km
- Route 8: 15 tons, 180 km

Fuel price: $1.50/liter

Find optimal truck assignment to routes to minimize total costs.
```

### Example 5: Warehouse Logistics
```
Optimize warehouse operations using MCP Optimizer.

A distribution center processes orders for an e-commerce company:

Warehouse Zones:
- Zone A (electronics): 500 m², storage cost $10/m²/day
- Zone B (clothing): 800 m², storage cost $6/m²/day
- Zone C (food): 600 m², storage cost $8/m²/day
- Zone D (furniture): 400 m², storage cost $12/m²/day

Product Groups (volume m³, required area m²):
- Smartphones: 200 m³, 150 m²
- Laptops: 300 m³, 200 m²
- Jackets: 400 m³, 300 m²
- Shoes: 350 m³, 250 m²
- Canned goods: 500 m³, 200 m²
- Beverages: 600 m³, 300 m²
- Tables: 250 m³, 180 m²
- Chairs: 300 m³, 220 m²

Compatibility constraints:
- Food cannot be stored with electronics
- Furniture requires separate zone
- Clothing is compatible with any products

Minimize storage costs while meeting all constraints.
```

### Example 6: International Logistics
```
Solve an international shipping problem with MCP Optimizer.

A global company ships products from 3 producing countries to 6 consuming countries:

Producing Countries (capacity thousand units/month):
- China: 5000 units
- Germany: 3000 units
- USA: 4000 units

Consuming Countries (demand thousand units/month):
- Russia: 1500 units
- Brazil: 2000 units
- India: 2500 units
- France: 1800 units
- Japan: 2200 units
- Australia: 1000 units

Shipping costs ($/unit):
From China: [8, 15, 6, 12, 4, 10]
From Germany: [12, 18, 14, 3, 11, 16]
From USA: [14, 8, 16, 9, 13, 12]

Customs duties (%):
To Russia: [5, 8, 12]
To Brazil: [10, 6, 15]
To India: [8, 12, 10]
To France: [3, 0, 7]
To Japan: [6, 4, 8]
To Australia: [7, 5, 9]

Delivery time (days):
From China: [25, 35, 20, 30, 10, 15]
From Germany: [20, 40, 25, 5, 15, 30]
From USA: [30, 15, 35, 10, 20, 25]

Optimize shipments considering costs, duties, and delivery times.
```

### Example 7: Last-Mile Urban Logistics
```
Optimize last-mile delivery using MCP Optimizer.

A delivery service operates in a city with 50 delivery points:

Depot: Central warehouse (coordinates 0, 0)

Couriers:
- 10 walking couriers (3 km radius, 8 orders/day, $50/day)
- 8 bike couriers (8 km radius, 15 orders/day, $80/day)
- 6 motorcycle couriers (15 km radius, 25 orders/day, $120/day)
- 4 van drivers (25 km radius, 40 orders/day, $200/day)

Orders by district:
- Downtown (0-5 km): 120 orders, high priority
- Midtown (5-12 km): 180 orders, medium priority
- Suburbs (12-20 km): 100 orders, low priority
- Outskirts (20+ km): 50 orders, low priority

Delivery time windows:
- Morning (9-12): 30% of orders
- Afternoon (12-15): 40% of orders
- Evening (15-18): 30% of orders

Late delivery penalties:
- High priority: $20/order
- Medium priority: $10/order
- Low priority: $5/order

Find optimal courier distribution and routes.
```

### Example 8: Railway Transportation Optimization
```
Help optimize railway freight transportation with MCP Optimizer.

A railway company transports cargo between 8 cities:

Cities: New York, Chicago, Los Angeles, Houston, Phoenix, Philadelphia, San Antonio, San Diego

Car Types:
- Boxcars (40 tons): 200 cars, $150/day
- Flatcars (60 tons): 150 cars, $200/day
- Tank cars (50 tons): 100 cars, $180/day
- Hoppers (70 tons): 80 cars, $220/day

Cargo flows (tons/week):
- New York → Chicago: 2000 (containers)
- Los Angeles → New York: 3000 (steel)
- Houston → Chicago: 1500 (grain)
- Phoenix → San Antonio: 1000 (chemicals)
- Philadelphia → New York: 2500 (food)
- San Diego → New York: 1800 (containers)

Distances between cities (miles):
8x8 distance matrix with actual railway distances

Transit time (days):
- Up to 500 miles: 2 days
- 500-1000 miles: 4 days
- 1000-2000 miles: 7 days
- Over 2000 miles: 10 days

Constraints:
- Containers only in boxcars
- Steel only on flatcars
- Grain only in hoppers
- Chemicals only in tank cars

Minimize total transportation costs considering delivery time.
```

## Request Structure for MCP Optimizer

```python
# Example for transportation problem
result = solve_transportation_problem(
    supply=[300, 400, 500],  # supply
    demand=[250, 350, 300, 300],  # demand
    costs=[
        [8, 6, 10, 9],
        [9, 12, 13, 7],
        [14, 9, 16, 5]
    ]
)
```

## Typical Activation Phrases

- "Solve a transportation problem"
- "Optimize delivery logistics"
- "Find optimal shipping routes"
- "Minimize transportation costs"
- "Plan supply chain"
- "Optimize fleet operations"
- "Help with warehouse planning"

## Applications

Transportation and logistics problems are used in:
- Freight transportation and logistics
- Supply chain planning
- Warehouse operations management
- Fleet optimization
- International trade
- Urban logistics
- Railway transportation 