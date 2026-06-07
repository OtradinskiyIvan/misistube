# MisisTube — Video Creation Service

Микросервис загрузки и хранения видео. FastAPI + PostgreSQL + MinIO (S3).

## .env (корень проекта)

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/video_db
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_BUCKET_NAME=videos
VITE_API_BASE_URL=http://localhost:8000
```

## Запуск

```bash
# Из папки creation_service (там лежит docker-compose.yaml)
cd creation_service
docker compose up -d
```

## Пользователи БД

- **`user`** — полный доступ (миграции, вставка, чтение). Используется этим сервисом.
- **`player_search_reader`** — read-only (пароль `player_search_password`). Для микросервиса поиска/плеера (`player_and_search`).

```sql
CREATE USER player_search_reader WITH PASSWORD 'player_search_password';
GRANT CONNECT ON DATABASE video_db TO player_search_reader;
GRANT USAGE ON SCHEMA public TO player_search_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO player_search_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO player_search_reader;
```

## Заменить / проверить перед деплоем

- **Пароли** — `pass`, `minioadmin123`, `colleague_pass` — заменить на реальные
- **CORS** — `src/main.py:10` — `allow_origins=["http://localhost:5173"]` заменить на домен фронта
- **S3 endpoint** — в Docker: `http://minio:9000` (внутренний), локально: `http://localhost:9000`
- **DB URL** — в Docker: `postgresql+asyncpg://user:pass@db:5432/video_db` (имя сервиса `db`)
- **LOG_DIR** — по умолчанию `logs/`, в Docker маппится в `./logs:/logs`

## Тесты

```bash
cd creation_service
pytest tests/ -v
```
