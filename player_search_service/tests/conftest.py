import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from shared.database.session import get_async_session

# ─── ФИКСТУРЫ С МОКАМИ (нужны только для unit-тестов) ──────────────────

@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.get.return_value = None  # имитируем промах кеша
    return cache

@pytest.fixture
def mock_search_port():
    port = AsyncMock()
    port.search.return_value = (
        [{"id": "mock-1", "title": "Mock Video", "duration": 120, "tags": ["test"]}],
        1
    )
    return port

@pytest.fixture
def mock_storage():
    storage = AsyncMock()
    storage.generate_presigned_url.return_value = ("https://fake-s3.url/video.m3u8", None)
    return storage

# ─── НОВАЯ ФИКСТУРА: HTTP Client ─────────────────────────────────────
@pytest.fixture
def client():
    """
    TestClient для интеграционных тестов эндпоинтов.
    Импортируем app локально, чтобы избежать ошибок при сборе тестов.
    """
    # Локальный импорт — выполняется только при вызове фикстуры
    from fastapi.testclient import TestClient
    from src.main import app
    
    # В тестах отключаем документацию, чтобы не грузить лишнее
    app.docs_url = None
    app.redoc_url = None
    
    return TestClient(app)