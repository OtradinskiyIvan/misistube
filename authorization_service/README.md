## Запуск сервиса авторизации и функциональное тестирование
### Запуск бэкенда:
```bash 
uvicorn authorization_service.src.main:app --reload --host 0.0.0.0 --port 8000
```
### Запуск контейнера с бд
```bash
docker run --name misistube-db -e POSTGRES_USER=your_username -e POSTGRES_PASSWORD=your_pg_password -e POSTGRES_DB=misistube -p 5433:5432 -d postgres:15
```
**Вывести всех имеющихся пользователей:**
```bash
psql "postgresql://your_name:your_pg_password@localhost:5433/misistube" -c "SELECT * FROM users;"
```

### Регистрация пользователя
```bash 
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/register   -H "Content-Type: application/json"   -d '{"email":"sectest@example.com","password":"strongpass123"}' | jq
{
"id": "3b2396dc-a1a6-4932-960b-983a04000008",
"email": "sectest@example.com",
"is_active": true,
"created_at": "2026-05-26T17:38:45.629285"
}
```

### Аутентификация пользователя
```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sectest@example.com","password":"strongpass123"}' | jq
```
