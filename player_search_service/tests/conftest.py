from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from shared.database.session import Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.api.deps import get_async_session, get_cache_adapter, get_storage_adapter

# ─── ФИКСТУРЫ C МОКАМИ (нужны только для unit-тестов) ──────────────────

@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.get.return_value = None  # имитируем промах кеша
    return cache


@pytest.fixture
def mock_search_port():
    port = AsyncMock()
    # 🔹 Обновлен под новую схему: duration_seconds, storage_key, status, created_at, updated_at
    port.search.return_value = (
        [{
            "id": "mock-1",
            "title": "Mock Video",
            "description": None,
            "storage_key": "videos/mock1/master.m3u8",
            "status": "ready",
            "duration_seconds": 120,
            "created_at": "2026-06-05T10:00:00+00:00",
            "updated_at": "2026-06-05T10:00:00+00:00",
            "tags": None,
            "thumbnail_url": None
        }],
        1
    )
    # 🔹 Добавлен мок для get_by_id (нужен для playback usecase)
    mock_video = AsyncMock()
    mock_video.storage_key = "video-123/master.m3u8"
    port.get_by_id.return_value = mock_video
    return port


@pytest.fixture
def mock_storage():
    storage = AsyncMock()
    storage.generate_presigned_url.return_value = ("https://fake-s3.url/video.m3u8", None)
    return storage


# ─── ФИКСТУРЫ БД ДЛЯ ИНТЕГРАЦИОННЫХ ТЕСТОВ ──────────────────────────────

@pytest.fixture(scope="module")
def postgres_container():
    """Запускает изолированный PostgreSQL контейнер для тестов"""
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest_asyncio.fixture(scope="function")
async def db_engine(postgres_container):
    """Создаёт engine для каждого теста"""
    engine = create_async_engine(postgres_container, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Создаёт сессию для каждого теста"""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with session_factory() as session:
        yield session


@pytest.fixture(autouse=True)
def override_db_session(db_session: AsyncSession):
    """Подменяет сессию БД в зависимостях FastAPI"""
    async def _get_session():
        yield db_session

    from src.main import app
    app.dependency_overrides[get_async_session] = _get_session
    yield
    app.dependency_overrides.clear()


# ─── НОВАЯ ФИКСТУРА: HTTP Client ─────────────────────────────────────

@pytest.fixture
def client():
    """
    TestClient для интеграционных тестов эндпоинтов.
    """
    from src.main import app
    app.docs_url = None
    app.redoc_url = None
    return TestClient(app)


# ─── ОЧИСТКА СОСТОЯНИЯ ───────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_adapters():
    """Сбрасывает lru_cache адаптеров между тестами"""
    get_cache_adapter.cache_clear()
    get_storage_adapter.cache_clear()
    yield
    get_cache_adapter.cache_clear()
    get_storage_adapter.cache_clear()
