import uuid

import pytest
import pytest_asyncio
from shared.database.session import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.search.repository import SQLAlchemyVideoRepository

# ─── ФИКСТУРЫ ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
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
    """Создаёт сессию для каждого теста с очисткой перед тестом"""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        await session.execute(text("TRUNCATE TABLE videos CASCADE"))
        await session.commit()

        yield session

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
        """Поиск возвращает только видео со статусом 'ready'"""
        user_id = uuid.uuid4()

        test_videos = [
            Video(
                title="Ready Video 1",
                storage_key="videos/ready1/master.m3u8",
                status=VideoStatus.READY,
                duration_seconds=120,
                user_id=user_id,
            ),
            Video(
                title="Processing Video",
                storage_key="videos/processing1/master.m3u8",
                status=VideoStatus.PROCESSING,
                duration_seconds=60,
                user_id=user_id,
            ),
            Video(
                title="Ready Video 2",
                storage_key="videos/ready2/master.m3u8",
                status=VideoStatus.READY,
                duration_seconds=180,
                user_id=user_id,
            ),
        ]

        db_session.add_all(test_videos)
        await db_session.commit()

        results, total = await repository.search(query="", offset=0, limit=10)

        assert total == 2
        assert len(results) == 2
        assert all("Ready Video" in r.title for r in results)
        assert "Processing Video" not in [r.title for r in results]
        assert all(r.user_id == str(user_id) for r in results)

    @pytest.mark.asyncio
    async def test_search_ilike_title(self, repository, db_session):
        """Поиск по заголовку (регистронезависимый, ILIKE)"""
        user_id = uuid.uuid4()

        db_session.add(
            Video(
                title="Кот играет c мячом",
                storage_key="videos/cat1/master.m3u8",
                status=VideoStatus.READY,
                duration_seconds=90,
                user_id=user_id,
            )
        )
        await db_session.commit()

        results1, total1 = await repository.search(query="кот", offset=0, limit=10)
        _results2, total2 = await repository.search(query="КОТ", offset=0, limit=10)

        assert total1 == 1
        assert total2 == 1
        assert "Кот" in results1[0].title
        assert results1[0].user_id == str(user_id)

    @pytest.mark.asyncio
    async def test_search_pagination(self, repository, db_session):
        """Пагинация: offset и limit"""
        user_id = uuid.uuid4()

        for i in range(5):
            db_session.add(
                Video(
                    title=f"Video {i}",
                    storage_key=f"videos/v{i}/master.m3u8",
                    status=VideoStatus.READY,
                    duration_seconds=60,
                    user_id=user_id,
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

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, db_session):
        """get_by_id возвращает видео, если оно существует"""
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

        result = await repository.get_by_id(str(video.id))

        assert result is not None
        assert result.title == "Test Video"
        assert result.storage_key == "videos/test/master.m3u8"
        assert result.duration_seconds == 120
        assert result.user_id == user_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, db_session):
        """get_by_id возвращает None, если видео не найдено"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        result = await repository.get_by_id(fake_uuid)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_invalid_uuid(self, repository, db_session):
        """get_by_id возвращает None для невалидного UUID"""
        result = await repository.get_by_id("not-a-uuid")

        assert result is None
