import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from shared.database.session import Base
from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.search.repository import SQLAlchemyVideoRepository


# ─── ФИКСТУРЫ ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def postgres_container():
    """Запускает изолированный PostgreSQL контейнер для тестов"""
    with PostgresContainer("postgres:15-alpine", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest_asyncio.fixture(scope="function")  # 🔹 ИСПРАВЛЕНО: было scope="module"
async def db_engine(postgres_container):
    """Создаёт engine для каждого теста"""
    engine = create_async_engine(postgres_container, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Создаёт сессию для каждого теста с очисткой перед тестом"""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with session_factory() as session:
        # Очищаем таблицу перед каждым тестом
        await session.execute(text("TRUNCATE TABLE videos CASCADE"))
        await session.commit()
        
        yield session
        
        # Очищаем таблицу после теста
        await session.execute(text("TRUNCATE TABLE videos CASCADE"))
        await session.commit()


# ─── ТЕСТЫ ─────────────────────────────────────────────────────────────

class TestSQLAlchemyVideoRepository:
    """Интеграционные тесты репозитория c реальной PostgreSQL (testcontainers)"""

    @pytest_asyncio.fixture
    async def repository(self, db_session: AsyncSession):
        """Фикстура репозитория c тестовой сессией"""
        return SQLAlchemyVideoRepository(session=db_session)

    @pytest.mark.asyncio
    async def test_search_returns_ready_videos_only(self, repository, db_session):
        """Поиск возвращает только видео co статусом 'ready'"""
        test_videos = [
            Video(
                title="Ready Video 1",
                storage_key="videos/ready1/master.m3u8",
                status=VideoStatus.READY,
                duration_seconds=120
            ),
            Video(
                title="Processing Video",
                storage_key="videos/processing1/master.m3u8",
                status=VideoStatus.PROCESSING,
                duration_seconds=60
            ),
            Video(
                title="Ready Video 2",
                storage_key="videos/ready2/master.m3u8",
                status=VideoStatus.READY,
                duration_seconds=180
            ),
        ]

        db_session.add_all(test_videos)
        await db_session.commit()

        results, total = await repository.search(query="", offset=0, limit=10)

        assert total == 2
        assert len(results) == 2
        assert all("Ready Video" in r.title for r in results)
        assert "Processing Video" not in [r.title for r in results]

    @pytest.mark.asyncio
    async def test_search_ilike_title(self, repository, db_session):
        """Поиск по заголовку (регистронезависимый, ILIKE)"""
        db_session.add(
            Video(
                title="Кот играет c мячом",
                storage_key="videos/cat1/master.m3u8",
                status=VideoStatus.READY,
                duration_seconds=90
            )
        )
        await db_session.commit()

        results1, total1 = await repository.search(query="кот", offset=0, limit=10)
        _results2, total2 = await repository.search(query="КОТ", offset=0, limit=10)

        assert total1 == 1
        assert total2 == 1
        assert "Кот" in results1[0].title

    @pytest.mark.asyncio
    async def test_search_pagination(self, repository, db_session):
        """Пагинация: offset и limit"""
        for i in range(5):
            db_session.add(
                Video(
                    title=f"Video {i}",
                    storage_key=f"videos/v{i}/master.m3u8",
                    status=VideoStatus.READY,
                    duration_seconds=60
                )
            )
        await db_session.commit()

        results1, total1 = await repository.search(query="", offset=0, limit=2)
        results2, total2 = await repository.search(query="", offset=2, limit=2)

        assert total1 == 5
        assert total2 == 5
        assert len(results1) == 2
        assert len(results2) == 2
        assert results1[0].title != results2[0].title