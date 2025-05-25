Ниже представлены четкие, краткие и практичные варианты API-интерфейсов MCP-серверов для указанных задач, которые могут быть реализованы на основе библиотек PuLP и Google OR-Tools.

---

## 📌 Общая структура REST API (FastAPI)

Каждый сервер реализует примерно следующий набор API-методов:

* **POST /solve** – запустить решение задачи.
* **GET /results/{task\_id}** – получить результаты решения.

---

## 1. 📦 Оптимизатор ресурсов (Resource Allocation MCP)

### 🔹 Запрос (POST `/solve`):

```json
{
  "solver": "pulp",
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

### 🔸 Ответ (GET `/results/{task_id}`):

```json
{
  "task_id": "12345",
  "status": "optimal",
  "allocation": {
    "worker1": ["task3", "task2"],
    "worker2": ["task1"]
  },
  "total_cost": 32
}
```

---

## 2. 🚚 Планировщик маршрутов (Routing MCP)

### 🔹 Запрос (POST `/solve`):

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

### 🔸 Ответ (GET `/results/{task_id}`):

```json
{
  "task_id": "67890",
  "status": "optimal",
  "routes": [
    {"vehicle_id": 1, "route": [1, 3, 2, 1], "route_distance": 45}
  ]
}
```

---

## 3. 📅 Планировщик смен (Workforce Scheduling MCP)

### 🔹 Запрос (POST `/solve`):

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

### 🔸 Ответ (GET `/results/{task_id}`):

```json
{
  "task_id": "24680",
  "status": "optimal",
  "schedule": {
    "Monday": ["Alice"],
    "Tuesday": ["Bob"]
  }
}
```

---

## 4. ⚙️ Оптимизатор производственных задач (Production Planning MCP)

### 🔹 Запрос (POST `/solve`):

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

### 🔸 Ответ (GET `/results/{task_id}`):

```json
{
  "task_id": "13579",
  "status": "optimal",
  "production_plan": {"A": 12, "B": 10},
  "total_profit": 490
}
```

---

## 5. 💰 Финансовый оптимизатор портфеля (Portfolio Optimization MCP)

### 🔹 Запрос (POST `/solve`):

```json
{
  "solver": "pulp",
  "assets": ["stockA", "stockB", "stockC"],
  "expected_returns": {"stockA": 0.1, "stockB": 0.15, "stockC": 0.07},
  "risks": {"stockA": 0.05, "stockB": 0.1, "stockC": 0.02},
  "max_risk": 0.06
}
```

### 🔸 Ответ (GET `/results/{task_id}`):

```json
{
  "task_id": "97531",
  "status": "optimal",
  "portfolio": {"stockA": 50, "stockC": 50},
  "expected_return": 0.085,
  "portfolio_risk": 0.035
}
```

---

## 6. 📦 Оптимизатор загрузки транспорта (Cargo Loading MCP)

### 🔹 Запрос (POST `/solve`):

```json
{
  "solver": "ortools",
  "cargo_items": [
    {"id": "box1", "weight": 10, "volume": 1},
    {"id": "box2", "weight": 20, "volume": 2}
  ],
  "vehicle": {"max_weight": 100, "max_volume": 15}
}
```

### 🔸 Ответ (GET `/results/{task_id}`):

```json
{
  "task_id": "86420",
  "status": "optimal",
  "loaded_items": ["box1", "box2"],
  "used_weight": 30,
  "used_volume": 3
}
```

---

## 🛠️ Используемые библиотеки и примеры реализации:

* **PuLP (Python):**

```python
from pulp import LpProblem, LpMaximize, LpVariable, lpSum

prob = LpProblem("Portfolio", LpMaximize)
x = {a: LpVariable(f"x_{a}", lowBound=0) for a in assets}

prob += lpSum(expected_returns[a]*x[a] for a in assets)
prob += lpSum(risks[a]*x[a] for a in assets) <= max_risk

prob.solve()
```

* **Google OR-Tools (Python):**

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")
x = {item["id"]: solver.BoolVar(item["id"]) for item in cargo_items}

solver.Add(sum(item["weight"] * x[item["id"]] for item in cargo_items) <= max_weight)
solver.Maximize(sum(item["value"] * x[item["id"]] for item in cargo_items))

status = solver.Solve()
```

---

Эти API-определения обеспечивают простоту интеграции, прозрачность постановки задач и удобство анализа результатов, идеально подходя для использования в контексте MCP-серверов, где центральным является автоматическое формирование и решение оптимизационных моделей.
