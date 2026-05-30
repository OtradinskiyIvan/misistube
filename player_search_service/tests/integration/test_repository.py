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
async def db_session(postgres_container):
    """
    Создаёт чистую сессию БД для каждого теста.
    1. Создаёт таблицы
    2. Возвращает сессию
    3. Очищает данные после теста (TRUNCATE)
    """
    # Создаём engine для тестовой БД
    engine = create_async_engine(postgres_container, echo=False)

    # Создаём таблицы (Base импортирован из shared)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Фабрика сессий
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Возвращаем сессию в тест
    async with session_factory() as session:
        yield session

    # 🔹 CLEANUP: Удаляем все данные после теста, но не дропаем таблицы
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE videos CASCADE"))

    await engine.dispose()


# ─── ТЕСТЫ ─────────────────────────────────────────────────────────────

class TestSQLAlchemyVideoRepository:
    """Интеграционные тесты репозитория c реальной PostgreSQL"""

    @pytest_asyncio.fixture
    async def repository(self, db_session: AsyncSession):
        """Фикстура репозитория c тестовой сессией"""
        return SQLAlchemyVideoRepository(session=db_session)

    @pytest.mark.asyncio
    async def test_search_returns_ready_videos_only(self, repository, db_session):
        """Поиск возвращает только видео co статусом 'ready'"""
        # Создаём тестовые данные
        test_videos = [
            Video(
                title="Ready Video 1",
                storage_key="videos/ready1/master.m3u8",
                status=VideoStatus.READY,
                tags=["test", "ready"]
            ),
            Video(
                title="Processing Video",
                storage_key="videos/processing1/master.m3u8",
                status=VideoStatus.PROCESSING,  # ← He должен попасть в выдачу
                tags=["test"]
            ),
            Video(
                title="Ready Video 2",
                storage_key="videos/ready2/master.m3u8",
                status=VideoStatus.READY,
                tags=["test"]
            ),
        ]

        db_session.add_all(test_videos)
        await db_session.commit()

        # Поиск: пустой запрос → все готовые видео
        results, total = await repository.search(query="", tags=None, offset=0, limit=10)

        # Проверка: только 2 готовых видео
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
                tags=["cats"]
            )
        )
        await db_session.commit()

        # Поиск c разными регистрами
        results1, total1 = await repository.search(query="кот", offset=0, limit=10)
        results2, total2 = await repository.search(query="KOT", offset=0, limit=10)

        assert total1 == 1
        assert total2 == 1
        assert "Кот" in results1[0].title

    @pytest.mark.asyncio
    async def test_search_by_tags(self, repository, db_session):
        """Фильтрация по тегам (ARRAY overlap)"""
        videos = [
            Video(
                title="Python Tutorial",
                storage_key="videos/py1/master.m3u8",
                status=VideoStatus.READY,
                tags=["python", "tutorial", "programming"]
            ),
            Video(
                title="Docker Guide",
                storage_key="videos/docker1/master.m3u8",
                status=VideoStatus.READY,
                tags=["docker", "devops"]
            ),
        ]
        db_session.add_all(videos)
        await db_session.commit()

        # Поиск по тегу "python"
        results, total = await repository.search(
            query="", tags=["python"], offset=0, limit=10
        )

        assert total == 1
        assert results[0].title == "Python Tutorial"
        assert "python" in results[0].tags

    @pytest.mark.asyncio
    async def test_search_pagination(self, repository, db_session):
        """Пагинация: offset и limit"""
        # Создаём 5 видео
        for i in range(5):
            db_session.add(
                Video(
                    title=f"Video {i}",
                    storage_key=f"videos/v{i}/master.m3u8",
                    status=VideoStatus.READY,
                    tags=[]
                )
            )
        await db_session.commit()

        # Первая страница
        results1, total1 = await repository.search(query="", offset=0, limit=2)
        # Вторая страница
        results2, total2 = await repository.search(query="", offset=2, limit=2)

        assert total1 == 5
        assert total2 == 5
        assert len(results1) == 2
        assert len(results2) == 2
        assert results1[0].title != results2[0].title  # разные видео
