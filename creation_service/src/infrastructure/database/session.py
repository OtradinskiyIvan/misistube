from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings

# Создаём асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",   # логи SQL в dev-режиме
    future=True,
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency для FastAPI
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session