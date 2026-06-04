import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from shared.database.session import init_engine
from src.core.config import get_settings


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Инициализирует БД перед тестами"""
    settings = get_settings()
    init_engine(
        database_url=str(settings.DATABASE_URL),
        echo=False
    )
    yield


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
        # limit=0 нарушает ge=1
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