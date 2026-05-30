from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Health check возвращает 200"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_validation(client: TestClient):
    """Отсутствие q → 422"""
    response = client.get("/api/v1/search")
    assert response.status_code == 422
    assert "q" in str(response.json())


def test_search_success(client: TestClient):
    """Валидный поиск → 200"""
    response = client.get("/api/v1/search", params={"q": "test", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_playback_success(client: TestClient):
    """Playback → presigned URL"""
    response = client.get("/api/v1/playback/test-video-id")
    assert response.status_code == 200
    data = response.json()
    assert "hls_master_url" in data