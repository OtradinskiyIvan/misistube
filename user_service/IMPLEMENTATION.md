# User Service Implementation Guide

## Summary

Реализован REST API для управления пользователями с архитектурой, разделенной на четыре слоя:
1. **Domain** - бизнес-сущности и правила
2. **Infrastructure** - работа с БД (SQLAlchemy)
3. **Services** - бизнес-логика
4. **API** - HTTP endpoints

## File Structure

```
user_service/src/
├── __init__.py
├── main.py                      # FastAPI приложение + exception handlers
├── deps.py                      # Dependency Injection
│
├── api/                         # API слой (HTTP endpoints)
│   ├── __init__.py
│   ├── router.py                # 5 CRUD endpoints + health check
│   ├── schemas.py               # Pydantic request/response models
│   └── error_handlers.py        # Exception handlers для JSON responses
│
├── domain/                      # Domain слой (бизнес-сущности)
│   ├── __init__.py
│   ├── entities.py              # User entity
│   ├── exceptions.py            # Доменные исключения
│   └── interfaces.py            # UserRepository ABC
│
├── infrastructure/              # Infrastructure слой (БД)
│   ├── __init__.py
│   ├── models.py                # SQLAlchemy ORM models
│   └── repositories.py          # UserRepositoryImpl (DB operations)
│
├── services/                    # Services слой (бизнес-логика)
│   ├── __init__.py
│   └── user_service.py          # UserService (CRUD + validation)
│
└── core/                        # Configuration
    ├── __init__.py
    ├── logging.py               # Structlog configuration
    └── settings.py              # Pydantic settings
```

## Implementation Details

### 1. Domain Layer

**entities.py** - User entity с полями:
- `id` (UUID)
- `username` (str) - уникально
- `email` (str) - уникально
- `display_name` (Optional[str])
- `is_active` (bool)
- `created_at`, `updated_at` (datetime)

**exceptions.py** - Доменные исключения:
- `UserNotFoundError` (404)
- `UserAlreadyExistsError` (400)
- `InvalidUserDataError` (400)
- `UserDeletionError` (500)

**interfaces.py** - Abstract `UserRepository` с методами:
- `get_by_id(user_id: UUID) -> Optional[User]`
- `get_by_username(username: str) -> Optional[User]`
- `get_by_email(email: str) -> Optional[User]`
- `get_all(skip: int, limit: int) -> list[User]`
- `create(user: User) -> User`
- `update(user: User) -> User`
- `delete(user_id: UUID) -> bool`

### 2. Infrastructure Layer

**models.py** - SQLAlchemy `UserModel`:
```python
class UserModel(Base):
    __tablename__ = "users"
    id = Column(SQLA_UUID, primary_key=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    display_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at, updated_at = Column(DateTime, ...)
```

**repositories.py** - `UserRepositoryImpl(UserRepository)`:
- Полная реализация методов из интерфейса
- Преобразование DB model → domain entity методом `_to_entity()`
- Обработка исключений (UserNotFoundError, UserAlreadyExistsError, InfrastructureError)
- Проверка уникальности username/email перед create/update

### 3. Services Layer

**user_service.py** - `UserService(repository)`:
- `create_user()` - валидирует и создает пользователя
- `get_user()` - получает по ID
- `get_all_users()` - список с пагинацией (max 1000)
- `update_user()` - обновляет поля (опционально)
- `delete_user()` - удаляет пользователя
- Валидация:
  - Username: 3-255 chars, alphanumeric + _/-
  - Email: valid format, max 255 chars

### 4. API Layer

**schemas.py** - Pydantic models:
- `UserCreateRequest` - for POST
- `UserUpdateRequest` - for PUT (все поля опциональны)
- `UserResponse` - response model
- `UserListResponse` - for list endpoint
- `ErrorResponse` - RFC 7807-подобный формат

**router.py** - 5 CRUD endpoints + health:
```
POST   /api/v1/users           -> create_user()    (201)
GET    /api/v1/users/{id}      -> get_user()       (200)
GET    /api/v1/users           -> list_users()     (200, с пагинацией)
PUT    /api/v1/users/{id}      -> update_user()    (200)
DELETE /api/v1/users/{id}      -> delete_user()    (204)
GET    /api/v1/health          -> health_check()   (200)
```

Все endpoints:
- Используют `Depends()` для DI (не инициализируют сервисы напрямую)
- Логируют действия с correlation ID
- Возвращают правильные HTTP статусы
- НЕ содержат SQL, бизнес-логику или обращение к внешним клиентам

**error_handlers.py** - Exception handling:
```python
async def app_exception_handler(request, exc: AppBaseError) -> JSONResponse:
    return {
        "error": exc.code,
        "detail": exc.message,
        "status_code": exc.status_code
    }
```

Обработчики зарегистрированы для:
- AppBaseError и всех подклассов
- Unexpected exceptions → 500 INTERNAL_ERROR

### 5. Dependency Injection (deps.py)

```python
async def get_session() -> AsyncSession:
    async for session in get_async_session():
        yield session

async def get_user_repository(session: AsyncSession = Depends(get_session)):
    return UserRepositoryImpl(session)

async def get_user_service(repository = Depends(get_user_repository)):
    return UserService(repository)
```

**Цепь инъекции:**
```
FastAPI Request
  → get_correlation_id()      [HTTP header X-Correlation-ID]
  → get_logger_dep()          [logger with correlation_id]
  → get_user_service()
     → get_user_repository()
        → get_session()       [AsyncSession from DB]
```

### 6. Main Application (main.py)

```python
app = FastAPI(...)
register_exception_handlers(app)  # подключение обработчиков
app.include_router(api_router, prefix="/api/v1")
```

## Key Design Decisions

### ✅ Clean Architecture
- **Domain** - никогда не знает про HTTP/DB
- **Infrastructure** - знает про ORM, но не про API
- **Services** - никогда не знает про HTTP
- **API** - только HTTP, вся логика в нижних слоях

### ✅ Dependency Injection
- Все сервисы и репозитории подаются через `Depends()`
- Легко тестировать (можно подставить mock)
- Нет инициализации сервисов/репозиториев внутри роутеров

### ✅ Error Handling
- Централизованная обработка исключений
- Все ошибки маппятся в структурированный JSON
- Доменные исключения знают свой HTTP status code

### ✅ Validation
- Pydantic валидирует input schemas (email, field lengths)
- Domain service валидирует business rules (username format)
- Repository обеспечивает ограничения БД (unique constraints)

### ✅ Logging & Tracing
- Structlog с JSON output
- Correlation ID через контекст (ContextVar)
- Все операции логируются с уровнем INFO

## Testing Recommendations

1. **Unit Tests** (domain, services):
   - Mock repositories
   - Test business logic and validation

2. **Integration Tests** (API endpoints):
   - Test full flow with real SQLite DB
   - Test error responses

3. **Async Support**:
   - Используйте `pytest-asyncio`
   - Все endpoints асинхронные

## Future Improvements

- [ ] Добавить password hashing для безопасности
- [ ] Добавить role/permission систему
- [ ] Добавить rate limiting
- [ ] Добавить soft delete (is_deleted column)
- [ ] Добавить audit logging (who changed what)
- [ ] Добавить database migrations (alembic)
- [ ] Добавить comprehensive test suite
