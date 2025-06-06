# Задачи назначения - Примеры использования

## Описание
Задачи назначения решают проблему оптимального распределения ресурсов (работников, машин, задач) для минимизации общих затрат или максимизации эффективности.

## Примеры промптов для LLM

### Пример 1: Назначение сотрудников на проекты
```
Помоги решить задачу назначения сотрудников с помощью MCP Optimizer.

У меня есть 4 сотрудника и 4 проекта. Каждый сотрудник может работать над любым проектом, но с разной эффективностью (оценка от 1 до 10):

Сотрудники: Алексей, Мария, Дмитрий, Елена
Проекты: Веб-сайт, Мобильное приложение, База данных, Аналитика

Матрица эффективности:
- Алексей: [9, 6, 7, 5]
- Мария: [7, 9, 6, 8]
- Дмитрий: [8, 7, 9, 6]
- Елена: [6, 8, 7, 9]

Найди оптимальное назначение для максимизации общей эффективности.
```

### Пример 2: Распределение машин по заказам
```
Используй MCP Optimizer для решения задачи распределения производственных машин.

На заводе есть 5 станков и 5 заказов. Время выполнения каждого заказа на каждом станке (в часах):

Станки: A, B, C, D, E
Заказы: Заказ1, Заказ2, Заказ3, Заказ4, Заказ5

Матрица времени выполнения:
- Станок A: [12, 15, 13, 11, 14]
- Станок B: [10, 12, 14, 13, 11]
- Станок C: [14, 11, 10, 12, 15]
- Станок D: [13, 14, 12, 10, 13]
- Станок E: [11, 13, 15, 14, 12]

Найди назначение, которое минимизирует общее время производства.
```

### Пример 3: Назначение водителей на маршруты
```
Реши задачу назначения водителей на маршруты с MCP Optimizer.

Транспортная компания имеет 6 водителей и 6 маршрутов. Стоимость назначения каждого водителя на маршрут (в рублях):

Водители: Иван, Петр, Сергей, Андрей, Михаил, Николай
Маршруты: Москва-СПб, Москва-Казань, Москва-Екатеринбург, Москва-Новосибирск, Москва-Краснодар, Москва-Ростов

Матрица стоимости:
- Иван: [5000, 4500, 6000, 8000, 4000, 3500]
- Петр: [4800, 4200, 5800, 7800, 4200, 3800]
- Сергей: [5200, 4800, 6200, 8200, 3800, 3200]
- Андрей: [4600, 4000, 5600, 7600, 4400, 4000]
- Михаил: [5400, 5000, 6400, 8400, 3600, 3000]
- Николай: [4400, 3800, 5400, 7400, 4600, 4200]

Найди назначение с минимальными общими затратами.
```

### Пример 4: Распределение задач между командами
```
Помоги распределить задачи между командами разработки с MCP Optimizer.

IT-отдел имеет 3 команды и 3 крупные задачи. Оценка сложности выполнения (баллы сложности):

Команды: Frontend, Backend, DevOps
Задачи: Новый интерфейс, API интеграция, Инфраструктура

Матрица сложности:
- Frontend: [3, 8, 9]
- Backend: [7, 2, 6]
- DevOps: [9, 5, 1]

Найди назначение, которое минимизирует общую сложность проекта.
```

## Структура запроса к MCP Optimizer

```python
# Пример вызова функции
result = solve_assignment_problem(
    workers=["Работник1", "Работник2", "Работник3"],
    tasks=["Задача1", "Задача2", "Задача3"],
    costs=[
        [стоимость_1_1, стоимость_1_2, стоимость_1_3],
        [стоимость_2_1, стоимость_2_2, стоимость_2_3],
        [стоимость_3_1, стоимость_3_2, стоимость_3_3]
    ]
)
```

## Типичные фразы для активации

- "Реши задачу назначения"
- "Распредели сотрудников/ресурсы оптимально"
- "Найди оптимальное назначение для..."
- "Минимизируй затраты на назначение"
- "Максимизируй эффективность распределения"
- "Помоги с оптимальным распределением задач"

## Применение

Задачи назначения используются в:
- Управлении персоналом
- Планировании производства
- Логистике и транспорте
- Распределении вычислительных ресурсов
- Планировании проектов 