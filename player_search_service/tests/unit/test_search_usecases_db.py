import pytest
from unittest.mock import AsyncMock
from src.usecases.search import SearchVideoUseCase
from src.api.schemas import SearchQuery, VideoResult

@pytest.fixture
def mock_cache():
    c = AsyncMock(); c.get.return_value = None; return c

@pytest.fixture
def mock_search_port():
    p = AsyncMock()
    p.search.return_value = (
        [VideoResult(id="v1", title="Test Video", duration=120, tags=["test"])],
        1
    )
    return p

@pytest.mark.asyncio
async def test_search_with_db_port(mock_cache, mock_search_port):
    uc = SearchVideoUseCase(cache=mock_cache, search_port=mock_search_port)
    result = await uc.execute(SearchQuery(q="test", limit=5))
    
    mock_search_port.search.assert_called_once_with(query="test", tags=None, offset=0, limit=5)
    mock_cache.set.assert_called_once()  # результат сохранён в кеш
    assert result.total == 1
    assert result.items[0].title == "Test Video"