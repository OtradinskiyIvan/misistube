from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic import PostgresDsn
from typing import Any


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory = None


def init_engine(database_url: PostgresDsn | str, echo: bool = False):
    global _engine, _session_factory
    url = str(database_url)
    if "postgresql+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://")

    _engine = create_async_engine(url, echo=echo, pool_pre_ping=True)
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return _engine


async def get_async_session() -> AsyncSession:
    if not _session_factory:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise