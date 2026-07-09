import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import uuid4

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SHARED = ROOT.parent
for p in (ROOT, SRC, SHARED):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from src.api.error_handlers import register_exception_handlers
from src.api.router import router
from src.deps import get_current_user_id, get_session, require_admin
from src.infrastructure.database.manager import Base, DatabaseManager

TEST_DATABASE_URL = "postgresql+asyncpg://misistube:misistube_secret@localhost:5432/misistube_users"


@pytest_asyncio.fixture(scope="session")
async def db_manager() -> AsyncGenerator[DatabaseManager, None]:
    manager = DatabaseManager(TEST_DATABASE_URL, echo=False, pool_pre_ping=False)
    async with manager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield manager
    async with manager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await manager.close()


@pytest_asyncio.fixture
async def session(db_manager: DatabaseManager) -> AsyncGenerator[AsyncSession, None]:
    async with db_manager._session_factory() as s:
        yield s


@pytest_asyncio.fixture
async def client(db_manager: DatabaseManager) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with db_manager._session_factory() as s:
            yield s

    test_app = FastAPI()
    register_exception_handlers(test_app)
    test_app.include_router(router, prefix="/api/v1")
    test_app.dependency_overrides[get_session] = override_get_session
    test_app.dependency_overrides[get_current_user_id] = lambda: uuid4()
    test_app.dependency_overrides[require_admin] = lambda: {"sub": str(uuid4()), "roles": ["admin"]}

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test",
    ) as ac:
        yield ac
