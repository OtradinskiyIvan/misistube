# Player & Searching Service

Микросервис для поиска видео и получения presigned URL для HLS-воспроизведения в рамках платформы MISISTUBE.

### Предварительные требования
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

### Функциональное тестирование
# Поиск видео
Валидный запрос (200 OK):
```bash
curl -s "http://127.0.0.1:8000/api/v1/search?q=кот&limit=5" | jq
```

# Получение presigned URL для воспроизведения
Успешный запрос (200 OK):
```bash
curl -s "http://127.0.0.1:8000/api/v1/playback/a1b2c3d4-..." | jq
```

### Очистка и переустановка
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

### Проверка docker контейнеров 
```bash
# Health check
curl http://localhost:8000/health | jq

# Поиск (ошибка валидации в формате RFC 7807)
curl -s http://localhost:8000/api/v1/search | jq

# Поиск с запросом (пустой результат, т.к. БД чистая)
curl -s "http://localhost:8000/api/v1/search?q=тест&limit=5" | jq

# Playback (presigned URL для несуществующего видео)
curl -s "http://localhost:8000/api/v1/playback/test-video-id" | jq

# Swagger UI (только в development)
# Открой в браузере: http://localhost:8000/docs

# Логи сервиса (если что-то не так)
docker compose -f player_search_service/docker-compose.yaml --profile testing logs -f player_search_service
```

### Остановка 
```bash
# Только базовые сервисы
docker compose down

# Всё, включая тестовые контейнеры и volumes
docker compose --profile testing down -v
```

### Просмотр логов
```bash
# В реальном времени
docker compose logs -f player_search_service

# Только ошибки
docker compose logs --tail=50 player_search_service | grep -i error
```

### Тестирование без docker
```bash
# Копируем (по аналогии) депаем переменные окружения из .env.example в .env
cp .env.example ./.env

# Иначе, если для докера всё-таки, то из .env.docker.example
cp .env.docker.example ./.env
```