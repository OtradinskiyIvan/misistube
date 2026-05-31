## User Service API Documentation

### Overview
REST API для управления пользователями с полной CRUD функциональностью.

Все endpoints находятся под `/api/v1/users`.

---

### Endpoints

#### 1. Create User
```
POST /api/v1/users
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "StrongPass1"
}
```

**Validation Rules:**
- `username`: 3–255 chars, alphanumeric + `_` and `-`
- `email`: valid email format
- `password`: 8–128 chars, at least one uppercase, one lowercase, one digit

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "status": "active",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00"
}
```

**Error Examples:**
- `422 VALIDATION_ERROR`: Invalid field format
- `400 USER_ALREADY_EXISTS`: Username or email already taken

---

#### 2. Get User by ID
```
GET /api/v1/users/{user_id}
```

**Path Parameters:**
- `user_id`: UUID пользователя

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "status": "active",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T00:00:00"
}
```

**Error Examples:**
- `404 USER_NOT_FOUND`: User не существует

---

#### 3. List Users (Paginated)
```
GET /api/v1/users?skip=0&limit=100
```

**Query Parameters:**
- `skip`: int (default: 0, min: 0) - количество пропускаемых записей
- `limit`: int (default: 100, min: 1, max: 1000) - количество записей на странице

**Response (200):**
```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "email": "john@example.com",
      "status": "active",
      "created_at": "2026-01-01T00:00:00",
      "updated_at": "2026-01-01T00:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

---

#### 4. Update User
```
PUT /api/v1/users/{user_id}
```

**Path Parameters:**
- `user_id`: UUID пользователя

**Request Body (все поля опциональны):**
```json
{
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "password": "NewPass123",
  "status": "inactive"
}
```

`status` может быть: `active`, `inactive`, `banned`, `suspended`.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "status": "inactive",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-01T01:00:00"
}
```

**Error Examples:**
- `404 USER_NOT_FOUND`: User не существует
- `400 USER_ALREADY_EXISTS`: Username/email already taken

---

#### 5. Delete User
```
DELETE /api/v1/users/{user_id}
```

**Path Parameters:**
- `user_id`: UUID пользователя

**Response (204):** No Content

**Error Examples:**
- `404 USER_NOT_FOUND`: User не существует

---

### Error Response Format

Все ошибки возвращаются в формате:

```json
{
  "error": "ERROR_CODE",
  "detail": "Human-readable message",
  "status_code": 400,
  "correlation_id": "uuid"
}
```

**Common Error Codes:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request body failed validation |
| `USER_ALREADY_EXISTS` | 400 | Username or email already taken |
| `INVALID_USER_DATA` | 400 | Business rule violation |
| `USER_NOT_FOUND` | 404 | User doesn't exist |
| `USER_DELETION_FAILED` | 500 | Database error during deletion |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

### Health Check
```
GET /api/v1/health
```

**Response (200):**
```json
{
  "status": "ok",
  "service": "user-service",
  "version": "0.1.0"
}
```

---

### Headers

**Required Headers:**
- `X-Correlation-ID`: Request tracking ID (UUID v4, auto-generated if not provided). Возвращается в заголовке ответа и в теле ошибки.

**Example:**
```
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000
X-Correlation-ID: abc-123-def-456
```

---

### Architecture

- **Domain Layer**: Business entities and rules
- **Infrastructure Layer**: Database operations (SQLAlchemy, asyncpg)
- **Services Layer**: Business logic (CRUD, validation via Pydantic DTOs)
- **API Layer**: HTTP endpoints (clean, no business logic or SQL)
- **Dependency Injection**: Via FastAPI `Depends()`
- **Exception Handling**: Centralized mapping to JSON `{error, detail, status_code, correlation_id}`
- **Logging**: Structured JSON logging via structlog with correlation IDs

---

### Validation Rules

**Username:**
- Minimum 3 characters
- Maximum 255 characters
- Alphanumeric + underscore/hyphen only
- Must be unique

**Email:**
- Valid email format
- Maximum 255 characters
- Must be unique

**Password:**
- Minimum 8 characters
- Maximum 128 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Status:**
- One of: `active`, `inactive`, `banned`, `suspended`

---

### Running the Service

```bash
cd user_service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Access documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
