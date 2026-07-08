import uuid
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from shared.database.session import Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.api.schemas import SearchQuery
from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.search.repository import SQLAlchemyVideoRepository
from src.usecases.search import SearchVideoUseCase


@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest_asyncio.fixture
async def db_engine(postgres_container):
    engine = create_async_engine(postgres_container, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.mark.asyncio
async def test_search_with_db_port(db_session: AsyncSession):
    """Тест поиска с реальной БД (testcontainers)"""
    user_id = uuid.uuid4()

    video = Video(
        title="Test Video",
        storage_key="videos/test/master.m3u8",
        status=VideoStatus.READY,
        duration_seconds=120,
        user_id=user_id,
    )
    db_session.add(video)
    await db_session.commit()

    repo = SQLAlchemyVideoRepository(session=db_session)
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    uc = SearchVideoUseCase(cache=mock_cache, search_port=repo)
    query = SearchQuery(q="Test", offset=0, limit=10)

    result = await uc.execute(query)

    assert result.total >= 1
    assert any("Test Video" in item.title for item in result.items)
    assert any(item.user_id == str(user_id) for item in result.items)
