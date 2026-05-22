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
  "display_name": "John Doe"  // optional
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "display_name": "John Doe",
  "is_active": true,
  "created_at": "2024-05-22T10:00:00+00:00",
  "updated_at": "2024-05-22T10:00:00+00:00"
}
```

**Error Examples:**
- `400 VALIDATION_ERROR`: Username already exists / Invalid email
- `400 INVALID_USER_DATA`: Username < 3 chars

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
  "display_name": "John Doe",
  "is_active": true,
  "created_at": "2024-05-22T10:00:00+00:00",
  "updated_at": "2024-05-22T10:00:00+00:00"
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
      "display_name": "John Doe",
      "is_active": true,
      "created_at": "2024-05-22T10:00:00+00:00",
      "updated_at": "2024-05-22T10:00:00+00:00"
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
  "display_name": "John Doe Updated",
  "is_active": false
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "display_name": "John Doe Updated",
  "is_active": false,
  "created_at": "2024-05-22T10:00:00+00:00",
  "updated_at": "2024-05-22T11:00:00+00:00"
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

Все ошибки возвращаются в формате (вдохновлено RFC 7807):

```json
{
  "error": "ERROR_CODE",
  "detail": "Human-readable message",
  "status_code": 400
}
```

**Common Error Codes:**
- `VALIDATION_ERROR` (400): Validation failed
- `USER_NOT_FOUND` (404): User doesn't exist
- `USER_ALREADY_EXISTS` (400): User with same username/email exists
- `INVALID_USER_DATA` (400): Invalid data format
- `USER_DELETION_FAILED` (500): Database error during deletion
- `INTERNAL_ERROR` (500): Unexpected server error

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

**Recommended Headers:**
- `X-Correlation-ID`: Request tracking ID (auto-generated if not provided)
  
**Example:**
```
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000
X-Correlation-ID: abc-123-def-456
```

---

### Architecture

- **Domain Layer**: Business entities and rules
- **Infrastructure Layer**: Database operations (SQLAlchemy)
- **Services Layer**: Business logic (validation, CRUD)
- **API Layer**: HTTP endpoints (clean, no business logic)
- **Dependency Injection**: Via FastAPI `Depends()`
- **Exception Handling**: Centralized mapping to JSON responses
- **Logging**: Structured logging with correlation IDs

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

**Display Name:**
- Maximum 255 characters
- Optional

---

### Running the Service

```bash
cd user_service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Access documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
