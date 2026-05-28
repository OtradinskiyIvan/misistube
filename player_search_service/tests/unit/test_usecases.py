import pytest
from unittest.mock import AsyncMock
from src.usecases.search import SearchVideoUseCase
from src.api.schemas import SearchQuery

@pytest.fixture
def mock_cache():
    c = AsyncMock(); c.get.return_value = None; return c

@pytest.mark.asyncio
async def test_search_miss(mock_cache):
    uc = SearchVideoUseCase(mock_cache)
    r = await uc.execute(SearchQuery(q="t", limit=5, offset=0))
    mock_cache.get.assert_called_once()
    mock_cache.set.assert_called_once()
    assert r.total == 1