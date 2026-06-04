# Player & Searching Service

Микросервис для поиска видео и получения presigned URL для HLS-воспроизведения в рамках платформы MISISTUBE.

## Предварительные требования
- Python 3.11+
- Docker + Docker Compose
- `uvicorn`, `pip`

### 1. Установка зависимостей
```bash
cd player_search_service
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -e ".[dev]"
```

### 2. Запуск инфраструктуры
```bash
docker compose up -d redis minio
```

### 3. Запуск бэкенда
```bash
# Из папки player_search_service/
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Проверка работоспособности
```bash
# Health-check
curl -s http://127.0.0.1:8000/health | jq
# → {"status":"ok","service":"player_search_service",...}
```

## Функциональное тестирование
### Поиск видео
Валидный запрос (200 OK):
```bash
curl -s "http://127.0.0.1:8000/api/v1/search?q=cat&limit=5" | jq
```

### Получение presigned URL для воспроизведения
Успешный запрос (200 OK):
```bash
curl -s "http://127.0.0.1:8000/api/v1/playback/a1b2c3d4-..." | jq
```

## API Testing

### Требования

- `curl` — для HTTP-запросов
- `jq` — для форматирования JSON
- `docker` + `docker compose` — для управления Redis
- `bc` — для расчёта времени (обычно предустановлен)

### Установка зависимостей

**Ubuntu/Debian:**
```bash
sudo apt install curl jq bc
```

**ArchLinux:**
```bash
sudo pacman -S curl jq bc
```

### Запуск тестов
```bash
# Разрешить исполнение файла
chmod +x test_api.sh
```

```bash
# Из корня проекта
./tests/test_api.sh
# Из папки tests
cd tests
./test_api.sh
```

### Запуск с кастомным URL (например, для staging)

```bash
BASE_URL=http://staging.misistube.dev ./tests/test_api.sh
```

### Запуск без graceful degradation тестов (если нет docker)

```bash
SKIP_REDIS_TESTS=1 ./tests/test_api.sh
```

### Результаты тестирования
**Все результаты сохраняются в curl_tests.log в корне проекта.**

## Очистка и переустановка
```bash
# Очистить кэш pip
pip cache purge

# Переустановить зависимости
pip uninstall -y player-search-service misistube-shared
pip install -e ".[dev]"

# Пересобрать Docker-образы (из корня проекта misistube/)
docker compose -f player_search_service/docker-compose.yaml build --no-cache --progress=plain

# Запустить полный стек с профилем testing
docker compose -f player_search_service/docker-compose.yaml --profile testing up -d

# Подождать ~25 секунд (БД + MinIO инициализируются)
sleep 25

# Проверить что все контейнеры запущены
docker compose -f player_search_service/docker-compose.yaml --profile testing ps
```

## Проверка docker контейнеров 
```bash
# Health check
curl http://localhost:8000/health | jq

# Поиск (ошибка валидации в формате RFC 7807)
curl -s http://localhost:8000/api/v1/search | jq

# Поиск с запросом (пустой результат, т.к. БД чистая)
curl -s "http://localhost:8000/api/v1/search?q=test&limit=5" | jq

# Playback (presigned URL для несуществующего видео)
curl -s "http://localhost:8000/api/v1/playback/test-video-id" | jq

# Swagger UI (только в development)
# Открой в браузере: http://localhost:8000/docs

# Логи сервиса (если что-то не так)
docker compose -f player_search_service/docker-compose.yaml --profile testing logs -f player_search_service
```

## Остановка 
```bash
# Только базовые сервисы
docker compose down

# Всё, включая тестовые контейнеры и volumes
docker compose --profile testing down -v
```

## Просмотр логов
```bash
# В реальном времени
docker compose logs -f player_search_service

# Только ошибки
docker compose logs --tail=50 player_search_service | grep -i error
```

## Тестирование без docker
```bash
# Копируем (по аналогии) депаем переменные окружения из .env.example в .env
cp .env.example ./.env

# Иначе, если для докера всё-таки, то из .env.docker.example
cp .env.docker.example ./.env
```

## -------------------------------------------

### Краткие 3 команды
```bash
# Локальная разработка (всё включено)
docker compose --profile testing up -d

# Продакшен (только сервис + внешние зависимости)
docker compose up -d

# Просмотр логов
docker compose logs -f player_search_service
```

## 📊 Разделы тестирования

### 1. 🏠 Базовые эндпоинты (3 теста)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 1 | `GET /` | 200 OK, сообщение о работе сервиса |
| 2 | `GET /health` | 200 OK, статус "ok", имя сервиса, окружение |
| 3 | `GET /docs` | 200 OK, HTML Swagger UI |

### 2. 🔍 Поиск видео (11 тестов)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 4 | `GET /api/v1/search` | Все видео (default limit=20) |
| 5 | `?limit=2` | Ровно 2 видео |
| 6 | `?offset=0&limit=2` | Первая страница |
| 7 | `?offset=2&limit=2` | Вторая страница |
| 8 | `?q=python` | Поиск по тексту |
| 9 | `?q=КОТ` | Кириллица в запросе |
| 10 | `?q=несуществующее` | Пустой результат |
| 11 | `?tags=python` | Фильтр по тегу |
| 12 | `?tags=коты` | Кириллица в тегах |
| 13 | `?tags=docker&tags=devops` | Множественные теги |
| 14 | `?q=tutorial&tags=python&limit=5` | Комбинированный поиск |

### 3. ⚠️ Валидация ошибок (5 тестов)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 15 | `?limit=0` | 422, `greater_than_equal` |
| 16 | `?limit=1000` | 422, `less_than_equal` |
| 17 | `?limit=abc` | 422, `int_parsing` |
| 18 | `?offset=-5` | 422, `greater_than_equal` |
| 19 | `?q=<300 символов>` | 422, `string_too_long` |

### 4. 🎬 Playback URL (3 теста)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 20 | `GET /api/v1/playback/{valid-uuid}` | Presigned URL |
| 21 | `GET /api/v1/playback/{zero-uuid}` | URL генерируется |
| 22 | `GET /api/v1/playback/not-a-uuid` | URL генерируется (без валидации) |

### 5. 🌐 CORS (2 теста)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 23 | `OPTIONS /api/v1/search` | 200, `access-control-allow-origin` |
| 24 | `GET /api/v1/search` с Origin | CORS заголовки в ответе |

### 6. 🔄 Graceful degradation (6 тестов)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 25-29 | 5 запросов без Redis | Все 200 OK, circuit breaker открывается |
| 30 | Запрос после восстановления Redis | 200 OK, кэш работает |

### 7. ⚡ Кэширование (3 теста)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 31 | Первый запрос | Cache miss (~0.026s) |
| 32 | Повторный запрос | Cache hit (~0.017s) |
| 33 | После `FLUSHALL` | Снова cache miss |

### 8. 🏷️ Correlation ID (2 теста)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 34 | Без заголовка | Автогенерация UUID в `X-Correlation-ID` |
| 35 | С `X-Correlation-ID: my-custom-id-123` | Возвращается тот же ID |

### 9. 🚀 Производительность (1 тест)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 36 | 100 параллельных запросов | Все завершаются за < 2 секунды |

### 10. 🧪 Edge cases (6 тестов)
| # | Тест | Ожидаемый результат |
|---|------|---------------------|
| 37 | `?q=` (пустой) | Все видео |
| 38 | `?q=python%20tutorial` | URL-encoded пробел |
| 39 | `?q=python%26tutorial` | URL-encoded амперсанд |
| 40 | `?tags=милота` | Кириллица в тегах |
| 41 | `?offset=10000&limit=10` | Пустой items, total=4 |
| 42 | `GET /api/v1/nonexistent` | 404 в RFC 7807 формате |