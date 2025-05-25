# Unified MCP Tools для оптимизации

Обобщенный справочник MCP инструментов для решения задач оптимизации, включающий как stateless подход, так и REST API интерфейсы.

## 🔄 Подходы к реализации

### Stateless MCP Tools
Простые функции без состояния, идеальные для AI-агентов. Принимают JSON с параметрами задачи и возвращают результат.

### REST API MCP Servers
Серверы с асинхронной обработкой, подходящие для сложных и долгих вычислений.

---

## 📐 Общие задачи линейного программирования

### `solve_linear_program`
**Библиотека**: PuLP  
**Описание**: Решает общую задачу линейного программирования

**Stateless Tool Input:**
```json
{
  "objective": {
    "sense": "minimize|maximize",
    "coefficients": {"x": 3, "y": 2, "z": 1}
  },
  "variables": {
    "x": {"type": "continuous", "lower": 0, "upper": null},
    "y": {"type": "continuous", "lower": 0, "upper": 10},
    "z": {"type": "integer", "lower": 0, "upper": null}
  },
  "constraints": [
    {"expression": {"x": 2, "y": 1, "z": 1}, "operator": "<=", "rhs": 20},
    {"expression": {"x": 1, "y": 3, "z": 0}, "operator": ">=", "rhs": 10}
  ],
  "solver": "CBC|GLPK"
}
```

### `solve_integer_program`
**Библиотека**: OR-Tools  
**Описание**: Решает задачу целочисленного программирования

**Stateless Tool Input:**
```json
{
  "objective": {
    "sense": "maximize",
    "coefficients": {"x1": 5, "x2": 3, "x3": 2}
  },
  "variables": {
    "x1": {"type": "integer", "lower": 0, "upper": 100},
    "x2": {"type": "binary"},
    "x3": {"type": "integer", "lower": 0, "upper": null}
  },
  "constraints": [
    {"expression": {"x1": 2, "x2": 8, "x3": 1}, "operator": "<=", "rhs": 15},
    {"expression": {"x1": 1, "x2": 1, "x3": 1}, "operator": "==", "rhs": 1}
  ],
  "time_limit_seconds": 60
}
```

---

## 🎯 Задачи назначений и распределения ресурсов

### `solve_assignment_problem` / Resource Allocation MCP
**Библиотека**: OR-Tools  
**Описание**: Задача о назначениях (работники-задачи) / распределение ресурсов

**Stateless Tool Input:**
```json
{
  "workers": ["Алиса", "Боб", "Чарли"],
  "tasks": ["Задача 1", "Задача 2", "Задача 3"],
  "costs": [
    [90, 80, 75],  // Затраты для Алисы
    [35, 85, 55],  // Затраты для Боба
    [125, 95, 90]  // Затраты для Чарли
  ],
  "maximize": false,
  "constraints": {
    "max_tasks_per_worker": 2
  }
}
```

**REST API (POST `/solve`):**
```json
{
  "solver": "ortools",
  "resources": ["worker1", "worker2"],
  "tasks": ["task1", "task2", "task3"],
  "costs": {
    "worker1": {"task1": 10, "task2": 12, "task3": 8},
    "worker2": {"task1": 9, "task2": 15, "task3": 11}
  },
  "constraints": {
    "max_tasks_per_worker": 2
  }
}
```

**Возвращает**: Оптимальные назначения, общая стоимость/эффективность

### `solve_transportation_problem`
**Библиотека**: OR-Tools  
**Описание**: Транспортная задача (минимизация затрат на перевозки)

**Stateless Tool Input:**
```json
{
  "suppliers": [
    {"name": "Склад A", "supply": 20},
    {"name": "Склад B", "supply": 30}
  ],
  "consumers": [
    {"name": "Магазин 1", "demand": 15},
    {"name": "Магазин 2", "demand": 25},
    {"name": "Магазин 3", "demand": 10}
  ],
  "costs": [
    [4, 2, 3],  // Затраты от склада A
    [2, 5, 1]   // Затраты от склада B
  ]
}
```

---

## 📦 Задачи упаковки и загрузки

### `solve_knapsack_problem` / Cargo Loading MCP
**Библиотека**: OR-Tools  
**Описание**: Задача о рюкзаке / оптимизация загрузки транспорта

**Stateless Tool Input:**
```json
{
  "items": [
    {"name": "Предмет 1", "value": 60, "weight": 10, "volume": 1},
    {"name": "Предмет 2", "value": 100, "weight": 20, "volume": 2},
    {"name": "Предмет 3", "value": 120, "weight": 30, "volume": 3}
  ],
  "capacity": 50,
  "volume_capacity": 15,
  "knapsack_type": "0-1|multiple",
  "max_items_per_type": 3
}
```

**REST API (POST `/solve`):**
```json
{
  "solver": "ortools",
  "cargo_items": [
    {"id": "box1", "weight": 10, "volume": 1, "value": 60},
    {"id": "box2", "weight": 20, "volume": 2, "value": 100}
  ],
  "vehicle": {"max_weight": 100, "max_volume": 15}
}
```

---

## 🗺️ Задачи маршрутизации

### `solve_traveling_salesman` / Routing MCP
**Библиотека**: OR-Tools  
**Описание**: Задача коммивояжера

**Stateless Tool Input:**
```json
{
  "locations": [
    {"name": "Депо", "lat": 55.7558, "lng": 37.6176},
    {"name": "Точка A", "lat": 55.7558, "lng": 37.6176},
    {"name": "Точка B", "lat": 55.7558, "lng": 37.6176}
  ],
  "distance_matrix": [
    [0, 10, 15],
    [10, 0, 20],
    [15, 20, 0]
  ],
  "start_location": 0
}
```

**REST API (POST `/solve`):**
```json
{
  "solver": "ortools",
  "locations": [
    {"id": 1, "x": 10, "y": 20},
    {"id": 2, "x": 15, "y": 30},
    {"id": 3, "x": 5, "y": 25}
  ],
  "vehicles": 1,
  "depot": 1
}
```

### `solve_vehicle_routing`
**Библиотека**: OR-Tools  
**Описание**: Задача маршрутизации транспорта

**Stateless Tool Input:**
```json
{
  "locations": [
    {"name": "Депо", "demand": 0},
    {"name": "Клиент 1", "demand": 10},
    {"name": "Клиент 2", "demand": 15}
  ],
  "distance_matrix": [[0, 5, 8], [5, 0, 3], [8, 3, 0]],
  "vehicles": [
    {"capacity": 50, "start_location": 0, "end_location": 0},
    {"capacity": 40, "start_location": 0, "end_location": 0}
  ],
  "max_vehicle_distance": 100
}
```

---

## 📅 Задачи планирования

### `solve_job_scheduling`
**Библиотека**: OR-Tools CP-SAT  
**Описание**: Планирование работ на машинах

**Stateless Tool Input:**
```json
{
  "jobs": [
    {
      "id": "job1",
      "tasks": [
        {"machine": 0, "duration": 3},
        {"machine": 1, "duration": 2}
      ]
    },
    {
      "id": "job2", 
      "tasks": [
        {"machine": 1, "duration": 4},
        {"machine": 0, "duration": 1}
      ]
    }
  ],
  "machines": ["Машина A", "Машина B"],
  "horizon": 20
}
```

### `solve_shift_scheduling` / Workforce Scheduling MCP
**Библиотека**: OR-Tools CP-SAT / PuLP  
**Описание**: Планирование смен сотрудников

**Stateless Tool Input:**
```json
{
  "employees": ["Анна", "Борис", "Вера"],
  "shifts": [
    {"name": "Утро", "start": 8, "end": 16, "required_staff": 2},
    {"name": "День", "start": 16, "end": 24, "required_staff": 1}
  ],
  "days": 7,
  "employee_constraints": {
    "Анна": {"max_shifts_per_week": 5, "unavailable_shifts": ["Ночь"]},
    "Борис": {"max_shifts_per_week": 6}
  }
}
```

**REST API (POST `/solve`):**
```json
{
  "solver": "pulp",
  "employees": ["Alice", "Bob"],
  "days": ["Monday", "Tuesday"],
  "preferences": {
    "Alice": {"Monday": 1, "Tuesday": 0},
    "Bob": {"Monday": 1, "Tuesday": 1}
  },
  "requirements": {
    "Monday": 1,
    "Tuesday": 1
  }
}
```

---

## 💰 Финансовые задачи

### `solve_portfolio_optimization` / Portfolio Optimization MCP
**Библиотека**: PuLP  
**Описание**: Оптимизация инвестиционного портфеля

**Stateless Tool Input:**
```json
{
  "assets": [
    {"name": "Акция A", "expected_return": 0.12, "risk": 0.2},
    {"name": "Облигация B", "expected_return": 0.08, "risk": 0.1}
  ],
  "budget": 100000,
  "risk_tolerance": 0.15,
  "min_allocation": 0.05,
  "max_allocation": 0.5
}
```

**REST API (POST `/solve`):**
```json
{
  "solver": "pulp",
  "assets": ["stockA", "stockB", "stockC"],
  "expected_returns": {"stockA": 0.1, "stockB": 0.15, "stockC": 0.07},
  "risks": {"stockA": 0.05, "stockB": 0.1, "stockC": 0.02},
  "max_risk": 0.06
}
```

---

## 🏭 Производственные задачи

### `solve_production_planning` / Production Planning MCP
**Библиотека**: PuLP / OR-Tools  
**Описание**: Планирование производства

**Stateless Tool Input:**
```json
{
  "products": [
    {"name": "Продукт A", "profit": 40, "resources": {"сталь": 2, "время": 1}},
    {"name": "Продукт B", "profit": 30, "resources": {"сталь": 1, "время": 2}}
  ],
  "resources": {
    "сталь": {"available": 100, "cost": 0},
    "время": {"available": 80, "cost": 0}
  },
  "demand_constraints": {
    "Продукт A": {"min": 0, "max": 40},
    "Продукт B": {"min": 10, "max": null}
  }
}
```

**REST API (POST `/solve`):**
```json
{
  "solver": "ortools",
  "products": ["A", "B"],
  "profits": {"A": 20, "B": 25},
  "resources": {"steel": 100, "plastic": 80},
  "usage": {
    "A": {"steel": 5, "plastic": 2},
    "B": {"steel": 4, "plastic": 3}
  }
}
```

---

## 🛠️ Утилиты

### `validate_optimization_input`
**Библиотека**: PuLP/OR-Tools  
**Описание**: Проверяет корректность входных данных

**Stateless Tool Input:**
```json
{
  "problem_type": "linear_program|assignment|transportation|knapsack|tsp|vrp|scheduling",
  "input_data": {...}
}
```

**Возвращает**: Отчет о корректности данных и возможных проблемах

---

## 📊 Общие форматы ответов

### Stateless Tools Response
```json
{
  "status": "optimal|feasible|infeasible|unbounded|error",
  "objective_value": 123.45,
  "variables": {...},
  "execution_time": 0.5,
  "solver_info": {...}
}
```

### REST API Response (GET `/results/{task_id}`)
```json
{
  "task_id": "12345",
  "status": "optimal|running|failed",
  "result": {...},
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:00:05Z"
}
```

---

## 🔧 Примеры реализации

### PuLP (Python)
```python
from pulp import LpProblem, LpMaximize, LpVariable, lpSum

prob = LpProblem("Portfolio", LpMaximize)
x = {a: LpVariable(f"x_{a}", lowBound=0) for a in assets}

prob += lpSum(expected_returns[a]*x[a] for a in assets)
prob += lpSum(risks[a]*x[a] for a in assets) <= max_risk

prob.solve()
```

### Google OR-Tools (Python)
```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")
x = {item["id"]: solver.BoolVar(item["id"]) for item in cargo_items}

solver.Add(sum(item["weight"] * x[item["id"]] for item in cargo_items) <= max_weight)
solver.Maximize(sum(item["value"] * x[item["id"]] for item in cargo_items))

status = solver.Solve()
```

---

## ✅ Преимущества объединенного подхода

- **Гибкость**: Выбор между stateless и REST API в зависимости от задачи
- **Совместимость**: Единые форматы данных для обоих подходов
- **Масштабируемость**: От простых до сложных задач оптимизации
- **Простота интеграции**: Четкие API и документация
- **Производительность**: Оптимальный выбор solver'а для каждой задачи

Этот обобщенный набор покрывает все практические задачи оптимизации с максимальной гибкостью реализации.