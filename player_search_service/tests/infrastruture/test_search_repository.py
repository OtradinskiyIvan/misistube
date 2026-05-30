import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.infrastructure.database.models import Base, Video, VideoStatus
from src.infrastructure.search.repository import SQLAlchemyVideoRepository


@pytest.fixture(scope="session")
def db_url():
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as pg:
        yield pg.get_connection_url()

@pytest.fixture
async def db_session(db_url):
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        # Добавляем тестовые данные
        session.add_all([
            Video(title="Test Cat", storage_key="cat.m3u8", status=VideoStatus.READY, tags=["cats"]),
            Video(title="Processing Dog", storage_key="dog.m3u8", status=VideoStatus.PROCESSING),
        ])
        await session.commit()
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_search_ilike(db_session):
    repo = SQLAlchemyVideoRepository(db_session)
    results, total = await repo.search(query="cat")

    assert total == 1
    assert len(results) == 1
    assert "Cat" in results[0].title

@pytest.mark.asyncio
async def test_search_status_filter(db_session):
    repo = SQLAlchemyVideoRepository(db_session)
    total = await repo.search(query="")  # пустой запрос → все готовые

    assert total == 1  # только "Test Cat", т.к. "Processing Dog" не ready
