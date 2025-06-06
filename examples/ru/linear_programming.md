# Линейное программирование - Примеры использования

## Описание
Линейное программирование позволяет решать задачи оптимизации с линейными ограничениями и линейной целевой функцией.

## Примеры промптов для LLM

### Пример 1: Задача производства
```
Помоги мне решить задачу производства с помощью MCP Optimizer.

У меня есть завод, который производит два типа продукции: столы и стулья.
- На производство одного стола требуется 4 часа работы и 2 кг материала
- На производство одного стула требуется 2 часа работы и 1 кг материала
- Прибыль от стола составляет 300 рублей, от стула - 200 рублей
- В день доступно 40 часов работы и 20 кг материала

Найди оптимальное количество столов и стульев для максимизации прибыли.
```

### Пример 2: Задача диеты
```
Используй MCP Optimizer для решения задачи планирования диеты.

Мне нужно составить диету из трех продуктов:
- Хлеб: 2 г белка, 50 г углеводов, 1 г жира на 100г, стоимость 30 руб/кг
- Мясо: 20 г белка, 0 г углеводов, 15 г жира на 100г, стоимость 500 руб/кг  
- Молоко: 3 г белка, 5 г углеводов, 3 г жира на 100г, стоимость 60 руб/кг

Требования:
- Минимум 60 г белка в день
- Минимум 300 г углеводов в день
- Максимум 50 г жира в день

Найди минимальную стоимость диеты.
```

### Пример 3: Задача транспортировки
```
Реши транспортную задачу с помощью MCP Optimizer.

У компании есть 3 склада и 4 магазина:

Склады (предложение):
- Склад A: 100 единиц товара
- Склад B: 150 единиц товара  
- Склад C: 200 единиц товара

Магазины (спрос):
- Магазин 1: 80 единиц
- Магазин 2: 120 единиц
- Магазин 3: 100 единиц
- Магазин 4: 150 единиц

Стоимость доставки (руб/единица):
От A: [5, 8, 6, 9]
От B: [7, 4, 5, 8]
От C: [6, 7, 4, 6]

Найди оптимальный план доставки с минимальными затратами.
```

### Пример 4: Задача смешивания
```
Помоги решить задачу смешивания топлива с MCP Optimizer.

Нефтеперерабатывающий завод производит бензин, смешивая 4 компонента:
- Компонент A: октановое число 95, стоимость 45 руб/л
- Компонент B: октановое число 87, стоимость 38 руб/л
- Компонент C: октановое число 92, стоимость 42 руб/л
- Компонент D: октановое число 98, стоимость 50 руб/л

Требования к готовому бензину:
- Октановое число не менее 91
- Объем производства 1000 литров
- Компонент A должен составлять не более 40% смеси
- Компонент D должен составлять не менее 10% смеси

Найди оптимальный состав смеси для минимизации стоимости.
```

## Структура запроса к MCP Optimizer

Для всех задач используется следующая структура:

```json
{
  "objective": {
    "sense": "maximize" | "minimize",
    "coefficients": {"переменная1": коэффициент1, "переменная2": коэффициент2}
  },
  "variables": {
    "переменная1": {"type": "continuous", "lower": 0, "upper": null},
    "переменная2": {"type": "continuous", "lower": 0, "upper": null}
  },
  "constraints": [
    {
      "expression": {"переменная1": коэффициент1, "переменная2": коэффициент2},
      "operator": "<=",
      "rhs": правая_часть
    }
  ]
}
```

## Типичные фразы для активации

- "Реши задачу линейного программирования"
- "Найди оптимальное решение для..."
- "Максимизируй/минимизируй при ограничениях..."
- "Помоги с оптимизацией производства/ресурсов/затрат"
- "Составь оптимальный план..." 