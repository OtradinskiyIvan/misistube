import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

ROOT_DIRECTORY = Path(__file__).resolve().parents[4]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.database.session import Base


class DatabaseManager:
    def __init__(self, database_url: str, echo: bool = False, pool_pre_ping: bool = False) -> None:
        url = str(database_url)
        if "postgresql+asyncpg" not in url and url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self._engine = create_async_engine(url, echo=echo, pool_pre_ping=pool_pre_ping)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self._engine.dispose()

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, Any]:
        async with self._session_factory() as session:
            yield session
