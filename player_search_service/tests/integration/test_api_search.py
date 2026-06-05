import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.main import app
from src.api.deps import get_async_session
from shared.database.session import Base


@pytest.fixture(scope="module")
def postgres_container():
    """Запускает PostgreSQL контейнер для тестов API"""
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest_asyncio.fixture
async def db_session(postgres_container):
    """Создает сессию для каждого теста API"""
    engine = create_async_engine(postgres_container, echo=False)
    
    # Создаем таблицы один раз
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with session_factory() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture(autouse=True)
def override_db_session(db_session: AsyncSession):
    """Подменяет сессию БД в зависимостях FastAPI"""
    async def _get_session():
        yield db_session
    
    app.dependency_overrides[get_async_session] = _get_session
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_endpoint_returns_200():
    """Проверяет, что эндпоинт поиска отвечает 200 OK"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/search?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert data["limit"] == 2


@pytest.mark.asyncio
async def test_search_endpoint_validation_error():
    """Проверяет, что невалидные данные возвращают 422 (RFC 7807)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/search?limit=0")
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["type"] == "https://misistube.dev/errors/validation"
        assert data["title"] == "Validation Error"
        assert data["status"] == 422
        assert "errors" in data
        assert isinstance(data["errors"], list)
        assert any("limit" in err.get("loc", []) for err in data["errors"])


@pytest.mark.asyncio
async def test_search_endpoint_with_tags():
    """Проверяет фильтрацию по тегам"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/search?tags=python&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        if data["total"] > 0:
            assert len(data["items"]) > 0
            has_python_tag = any("python" in item.get("tags", []) for item in data["items"])
            assert has_python_tag


@pytest.mark.asyncio
async def test_health_endpoint():
    """Проверяет, что health check работает"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "service" in data
        assert "env" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Проверяет корневой эндпоинт"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "docs" in data