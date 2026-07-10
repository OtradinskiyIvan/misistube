import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.postgres import PostgresContainer

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SHARED = ROOT.parent
for p in (ROOT, SRC, SHARED):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from src.infrastructure.database.manager import Base, DatabaseManager
from src.infrastructure.database.uow import UnitOfWorkImpl
from src.infrastructure.repositories import UserRepositoryImpl


@pytest_asyncio.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresContainer, None]:
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest_asyncio.fixture(scope="session")
async def db_manager(postgres_container: PostgresContainer) -> AsyncGenerator[DatabaseManager, None]:
    raw_url = postgres_container.get_connection_url(driver=None)
    manager = DatabaseManager(raw_url, echo=False, pool_pre_ping=False)
    async with manager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield manager
    async with manager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await manager.close()


@pytest_asyncio.fixture
async def session(db_manager: DatabaseManager) -> AsyncSession:
    s = AsyncSession(db_manager._engine, expire_on_commit=False)
    await s.begin()
    return s


@pytest_asyncio.fixture
def repository(session: AsyncSession) -> UserRepositoryImpl:
    return UserRepositoryImpl(session)


@pytest_asyncio.fixture
def uow(session: AsyncSession) -> UnitOfWorkImpl:
    return UnitOfWorkImpl(session)
