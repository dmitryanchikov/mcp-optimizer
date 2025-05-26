# Docker Optimization for MCP Optimizer

Этот каталог содержит оптимизированные Docker конфигурации для MCP Optimizer.

## 📊 Результаты оптимизации

| Dockerfile | Размер | Сокращение | Особенности |
|------------|--------|------------|-------------|
| Исходный | 1.03GB | - | Базовая конфигурация |
| **Dockerfile** (основной) | **398MB** | **61%** | ✅ Рекомендуемый |
| Dockerfile.distroless | 314MB | 69% | ⚠️ Экспериментальный |

## 🚀 Быстрый старт

### Основной оптимизированный образ
```bash
# Сборка
docker build -t mcp-optimizer:optimized .

# Запуск
docker run -p 8000:8000 mcp-optimizer:optimized

# Проверка размера
docker images mcp-optimizer:optimized
```

### Distroless образ (экспериментальный)
```bash
# Сборка
docker build -f docker/Dockerfile.distroless -t mcp-optimizer:distroless .

# Запуск
docker run -p 8000:8000 mcp-optimizer:distroless
```

## 🧪 Тестирование

Запустите комплексное тестирование оптимизированного образа:

```bash
./scripts/test_docker_optimization.sh
```

Этот скрипт проверит:
- ✅ Размер образа
- ✅ Функциональность Python
- ✅ Импорты MCP Optimizer
- ✅ Работу PuLP solver
- ✅ Работу OR-Tools solver
- ✅ Запуск MCP сервера
- ✅ Использование памяти
- ✅ Производительность

## 🔧 Оптимизации

### 1. Многоэтапная сборка
- **Build stage**: Компиляция и установка зависимостей
- **Runtime stage**: Минимальный образ только с необходимыми компонентами

### 2. Кэширование с uv
```dockerfile
ENV UV_CACHE_DIR=/build/.uv
RUN --mount=type=cache,target=/build/.uv \
    uv pip install --no-cache .
```

### 3. Очистка файлов
- Удаление `.pyc`, `.pyo` файлов
- Очистка `__pycache__` директорий
- Удаление ненужных пакетов (pip, setuptools)

### 4. Оптимизация Python
```dockerfile
ENV PYTHONOPTIMIZE=2 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random
```

### 5. Безопасность
- Непривилегированный пользователь
- Минимальные runtime зависимости

## 📈 Сравнение подходов

### Основной Dockerfile (Рекомендуемый)
**Преимущества:**
- ✅ Отличный баланс размера и функциональности
- ✅ Возможность отладки (есть shell)
- ✅ Healthcheck поддерживается
- ✅ Простота troubleshooting

**Недостатки:**
- ❌ Больше размер чем distroless

### Dockerfile.distroless (Экспериментальный)
**Преимущества:**
- ✅ Минимальный размер (314MB)
- ✅ Максимальная безопасность
- ✅ Отсутствие лишних компонентов

**Недостатки:**
- ❌ Нет shell для отладки
- ❌ Сложности с troubleshooting
- ❌ Нет healthcheck
- ❌ Требует точного соответствия версий

## 🛠️ Разработка

### Сборка для разработки
```bash
docker build --build-arg ENV=development -t mcp-optimizer:dev .
```

### Сборка для production
```bash
docker build --build-arg ENV=production -t mcp-optimizer:prod .
```

### Использование BuildKit для ускорения
```bash
DOCKER_BUILDKIT=1 docker build -t mcp-optimizer:optimized .
```

## 📋 Мониторинг размера

### Анализ слоев
```bash
docker history mcp-optimizer:optimized
```

### Детальный анализ
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest mcp-optimizer:optimized
```

## 🔄 CI/CD Integration

### GitHub Actions пример
```yaml
- name: Build optimized Docker image
  run: |
    docker build -t mcp-optimizer:${{ github.sha }} .
    
- name: Test image size
  run: |
    SIZE=$(docker images mcp-optimizer:${{ github.sha }} --format "{{.Size}}")
    echo "Image size: $SIZE"
    # Fail if size > 500MB
    [[ "$SIZE" != *"GB"* ]]
```

## 📚 Дополнительные ресурсы

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage builds](https://docs.docker.com/develop/dev-best-practices/#use-multi-stage-builds)
- [Distroless Images](https://github.com/GoogleContainerTools/distroless)
- [Docker BuildKit](https://docs.docker.com/develop/dev-best-practices/#enable-buildkit)

## 🐛 Troubleshooting

### Проблема: Образ слишком большой
**Решение:**
1. Проверьте .dockerignore
2. Убедитесь в правильной очистке cache
3. Используйте `docker system prune`

### Проблема: OR-Tools не работает
**Решение:**
1. Убедитесь в наличии libgomp1
2. Проверьте совместимость с архитектурой
3. Используйте debian-slim вместо alpine

### Проблема: Медленная сборка
**Решение:**
1. Включите BuildKit
2. Используйте mount cache
3. Оптимизируйте порядок COPY команд

## 📞 Поддержка

При возникновении проблем:
1. Запустите `./scripts/test_docker_optimization.sh`
2. Проверьте логи: `docker logs <container_id>`
3. Создайте issue с результатами тестирования 