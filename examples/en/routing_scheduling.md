# Routing & Scheduling - Usage Examples

## Description
Routing and scheduling problems optimize the sequence of operations, route construction, and resource allocation over time to minimize costs and time.

## Example Prompts for LLM

### Example 1: Traveling Salesman Problem (TSP)
```
Help me solve a traveling salesman problem using MCP Optimizer.

A sales representative must visit 8 cities and return to the starting point:

Cities: New York, Boston, Philadelphia, Washington, Baltimore, Richmond, Norfolk, Raleigh

Distance matrix (miles):
         NYC  BOS  PHL  WAS  BAL  RIC  NOR  RAL
New York  0   215  95   230  185  290  340  480
Boston   215   0   310  440  395  500  550  690
Philadelphia 95 310   0   135  100  205  255  395
Washington 230 440  135   0    40  110  160  300
Baltimore 185 395  100   40    0   150  200  340
Richmond  290 500  205  110  150   0    50  190
Norfolk   340 550  255  160  200   50    0   140
Raleigh   480 690  395  300  340  190  140    0

Additional conditions:
- Start and end route in New York
- Working hours: 8 hours per day
- Average speed: 60 mph
- Need to spend 1 hour in each city

Find the shortest route to visit all cities.
```

### Example 2: Vehicle Routing Problem (VRP)
```
Use MCP Optimizer to plan delivery routes.

A delivery service has:
- 4 trucks with different capacities
- 15 delivery points
- Central warehouse

Trucks:
- Truck 1: capacity 5 tons, cost $200/day
- Truck 2: capacity 3 tons, cost $150/day
- Truck 3: capacity 8 tons, cost $300/day
- Truck 4: capacity 2 tons, cost $120/day

Delivery points (cargo weight in tons):
1. Store A: 0.8 tons
2. Store B: 1.2 tons
3. Office C: 0.3 tons
4. Warehouse D: 2.5 tons
5. Restaurant E: 0.6 tons
6. Pharmacy F: 0.2 tons
7. School G: 0.9 tons
8. Hospital H: 1.1 tons
9. Factory I: 3.2 tons
10. Store J: 0.7 tons
11. Office K: 0.4 tons
12. Warehouse L: 1.8 tons
13. Cafe M: 0.5 tons
14. Gym N: 0.6 tons
15. Library O: 0.3 tons

Delivery time windows:
- Morning (9-12): points 1,3,5,7,11,15
- Afternoon (12-15): points 2,4,6,8,12,14
- Evening (15-18): points 9,10,13

Constraints:
- Working day: 8 hours
- Maximum distance per truck: 200 km
- Mandatory return to warehouse

Minimize total delivery costs.
```

### Example 3: Employee Shift Scheduling
```
Solve a shift scheduling problem with MCP Optimizer.

A 24/7 call center requires coverage with minimum staff:

Shifts:
- Morning (8-16): minimum 15 operators
- Evening (16-24): minimum 20 operators
- Night (0-8): minimum 8 operators

Available employees (25 people):
- Full-time: 15 people (can work any shift)
- Part-time: 10 people (day shifts only)

Constraints:
- Maximum 5 shifts per week per person
- Minimum 2 consecutive days off
- Cannot work consecutive shifts
- Night shifts only for full-time employees

Additional requirements:
- Increase coverage by 20% on weekends
- Experienced operators (5 people) must be in each shift
- New hires (3 people) cannot work nights

Minimize total working hours while ensuring coverage.
```

### Example 4: Production Order Scheduling
```
Help schedule production orders with MCP Optimizer.

A factory has 5 machines and 12 orders to complete:

Machines:
- Machine A: universal, 16 hours/day
- Machine B: lathe, 20 hours/day
- Machine C: milling, 18 hours/day
- Machine D: drilling, 22 hours/day
- Machine E: grinding, 14 hours/day

Orders (processing time in hours on each machine):
         A   B   C   D   E  Due  Priority
Order 1  8   6   -   4   2   3days   1
Order 2  12  -   10  6   4   5days   2
Order 3  6   4   8   -   3   2days   1
Order 4  -   8   12  10  6   7days   3
Order 5  10  6   -   8   5   4days   2
Order 6  4   -   6   3   2   1day    1
Order 7  14  10  16  12  8   10days  3
Order 8  8   6   10  -   4   6days   2
Order 9  -   4   8   6   3   3days   1
Order 10 12  8   -   10  6   8days   3
Order 11 6   -   4   2   1   2days   1
Order 12 10  8   12  8   5   9days   2

Constraints:
- Priority 1 orders must be completed first
- Some operations cannot be done on certain machines (-)
- Machine setup between orders: 1 hour
- Late penalty: $100/day

Minimize total completion time and penalties.
```

### Example 5: School Bus Routing
```
Optimize school bus routes with MCP Optimizer.

A school district serves 3 schools with 6 buses:

Schools:
- Elementary: 450 students, hours 8:00-15:00
- Middle: 600 students, hours 8:30-15:30
- High: 800 students, hours 9:00-16:00

Buses:
- Bus 1: 45 seats, depot A
- Bus 2: 60 seats, depot A
- Bus 3: 45 seats, depot B
- Bus 4: 72 seats, depot B
- Bus 5: 45 seats, depot C
- Bus 6: 60 seats, depot C

Stops (number of students by school):
Stop 1: [25, 15, 20] - elementary, middle, high
Stop 2: [30, 25, 35]
Stop 3: [20, 30, 25]
Stop 4: [35, 20, 30]
Stop 5: [15, 25, 20]
Stop 6: [25, 35, 40]
Stop 7: [40, 30, 35]
Stop 8: [20, 15, 25]
Stop 9: [30, 40, 45]
Stop 10: [25, 20, 30]

Constraints:
- Travel time to school: maximum 45 minutes
- Bus can serve only one school per trip
- Need 2 trips: morning and afternoon
- Distance between stops: 5-15 minutes

Minimize total travel time and number of buses used.
```

### Example 6: Medical Procedure Scheduling
```
Help schedule medical procedures with MCP Optimizer.

A hospital has 4 operating rooms and 15 scheduled surgeries:

Operating Rooms:
- OR 1: general surgery, 12 hours/day
- OR 2: cardiac surgery, 10 hours/day
- OR 3: neurosurgery, 8 hours/day
- OR 4: universal, 14 hours/day

Surgeries:
1. Appendectomy: 2 hours, OR 1 or 4, medium priority
2. Heart surgery: 6 hours, OR 2 only, high priority
3. Brain tumor removal: 8 hours, OR 3 only, high priority
4. Cholecystectomy: 3 hours, OR 1 or 4, low priority
5. Coronary bypass: 5 hours, OR 2 only, high priority
6. Hernia repair: 1.5 hours, OR 1 or 4, low priority
7. Spine surgery: 4 hours, OR 3 or 4, medium priority
8. Gastric resection: 4 hours, OR 1 or 4, medium priority
9. Valve replacement: 7 hours, OR 2 only, high priority
10. Craniotomy: 6 hours, OR 3 only, high priority
11. Laparoscopy: 2 hours, OR 1 or 4, low priority
12. Stenting: 3 hours, OR 2 only, medium priority
13. Cataract removal: 1 hour, OR 4, low priority
14. Arthroscopy: 2.5 hours, OR 4, low priority
15. Tonsillectomy: 1.5 hours, OR 1 or 4, low priority

Constraints:
- High priority surgeries must be completed first
- 30 minutes preparation between surgeries
- Some surgeries require special equipment
- Working day: 7:00-19:00

Maximize number of completed surgeries considering priorities.
```

### Example 7: Tournament Scheduling
```
Plan a tournament schedule with MCP Optimizer.

A football league runs a championship with 12 teams:

Teams: A, B, C, D, E, F, G, H, I, J, K, L

Stadiums:
- Stadium 1: capacity 50,000, rent $10,000/day
- Stadium 2: capacity 30,000, rent $6,000/day
- Stadium 3: capacity 40,000, rent $8,000/day
- Stadium 4: capacity 25,000, rent $5,000/day

Constraints:
- Each team plays every other team twice (home and away)
- Season lasts 22 rounds (6 matches per round)
- Matches on weekends only
- Minimum 2 weeks between home matches for each team
- Derby matches (A-B, C-D, E-F) at large stadiums

Team popularity (expected attendance):
A: 45,000, B: 40,000, C: 35,000, D: 30,000
E: 25,000, F: 20,000, G: 18,000, H: 15,000
I: 12,000, J: 10,000, K: 8,000, L: 6,000

Ticket price: $50 (average)

Maximize ticket revenue minus stadium rent.
```

### Example 8: Equipment Maintenance Scheduling
```
Optimize equipment maintenance schedule with MCP Optimizer.

A manufacturing plant has 20 pieces of equipment and 5 service teams:

Equipment (hours until scheduled maintenance):
1. Machine A1: 120 hours, high criticality
2. Machine A2: 80 hours, medium criticality
3. Conveyor B1: 200 hours, high criticality
4. Conveyor B2: 150 hours, high criticality
5. Press C1: 60 hours, medium criticality
6. Press C2: 90 hours, medium criticality
7. Furnace D1: 300 hours, high criticality
8. Furnace D2: 250 hours, high criticality
9. Compressor E1: 100 hours, low criticality
10. Compressor E2: 140 hours, low criticality
11. Pump F1: 50 hours, medium criticality
12. Pump F2: 70 hours, medium criticality
13. Generator G1: 180 hours, high criticality
14. Generator G2: 160 hours, high criticality
15. Fan H1: 40 hours, low criticality
16. Fan H2: 30 hours, low criticality
17. Crane I1: 110 hours, medium criticality
18. Crane I2: 130 hours, medium criticality
19. Robot J1: 220 hours, high criticality
20. Robot J2: 190 hours, high criticality

Service Teams:
- Team 1: mechanics, 8 hours/day, $500/day
- Team 2: electricians, 8 hours/day, $600/day
- Team 3: universal, 10 hours/day, $700/day
- Team 4: robot specialists, 6 hours/day, $800/day
- Team 5: emergency, 12 hours/day, $1000/day

Maintenance time (hours):
- Machines: 4 hours (teams 1,3)
- Conveyors: 6 hours (teams 1,2,3)
- Presses: 3 hours (teams 1,3)
- Furnaces: 8 hours (teams 2,3)
- Compressors: 2 hours (teams 1,2,3)
- Pumps: 2 hours (teams 1,2,3)
- Generators: 5 hours (teams 2,3)
- Fans: 1 hour (teams 1,2,3)
- Cranes: 3 hours (teams 1,3)
- Robots: 6 hours (teams 3,4)

Constraints:
- Critical equipment cannot be stopped simultaneously
- 4-week planning horizon
- Emergency team only for urgent cases
- Weekends: emergency work only

Minimize maintenance costs while meeting schedule.
```

## Request Structure for MCP Optimizer

```python
# Example for routing problem
result = solve_routing_problem(
    locations=["A", "B", "C", "D"],
    distance_matrix=[
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ],
    problem_type="TSP",  # or "VRP"
    constraints={
        "time_windows": [(8, 17), (9, 16), (10, 18), (8, 15)],
        "capacity": 100
    }
)
```

## Typical Activation Phrases

- "Solve a traveling salesman problem"
- "Optimize delivery routes"
- "Schedule employee shifts"
- "Find optimal operation sequence"
- "Help with resource planning"
- "Create work schedule"
- "Optimize time intervals"

## Applications

Routing and scheduling problems are used in:
- Logistics and delivery
- Production planning
- Personnel management
- Medical scheduling
- Transportation systems
- Sports tournaments
- Equipment maintenance