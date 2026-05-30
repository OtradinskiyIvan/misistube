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

# Health-check
```bash
curl -s http://127.0.0.1:8000/health | jq
```

### Очистка и переустановка
```bash
# Очистить кэш pip
pip cache purge

# Переустановить зависимости
pip uninstall -y player-search-service misistube-shared
pip install -e ".[dev]"

# Пересобрать Docker-образы (если меняли Dockerfile)
docker compose build --no-cache
```