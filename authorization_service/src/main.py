from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.logger import get_logger
from shared.database.session import init_engine, Base
from .core.settings import AuthSettings
from .presentations.routers.auth import router as auth_router
from .presentations.routers.health import router as health_router
from .presentations.error_handlers import register_exception_handlers
from dotenv import load_dotenv

load_dotenv()
settings = AuthSettings()
logger = get_logger(settings.APP_NAME, settings.LOG_LEVEL)



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Authorization Service...")
    engine = init_engine(settings.DATABASE_URL, echo=settings.APP_ENV == "development")

    # В development-режиме таблицы создаются автоматически. В prod используйте Alembic.
    if settings.APP_ENV == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield
    logger.info("Shutting down Authorization Service...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Заменить на конкретные домены фронтенда в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(health_router)