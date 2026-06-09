import sys
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.database.session import init_engine

from core.logger import correlation_id_var
from src.api.deps import get_storage_adapter
from src.api.routers import playback, search, videos
from src.core.config import get_settings
from src.core.exceptions import register_rfc7807_handlers
from src.core.logger import setup_service_logger
from src.core.middleware import CorrelationIdMiddleware

settings = get_settings()
logger = setup_service_logger("player_search_service", level=settings.LOG_LEVEL)

_db_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения:
    - Startup: инициализация БД, создание таблиц (в dev), подключение к инфраструктуре
    - Shutdown: корректное закрытие соединений
    """
    global _db_engine

    correlation_id_var.set("startup")
    logger.info("Starting Player & Searching Service... [env=%s]", settings.APP_ENV)

    _db_engine = init_engine(
        database_url=str(settings.DATABASE_URL),
        echo=settings.APP_ENV == "development"
    )

    yield

    correlation_id_var.set("shutdown")
    logger.info("Shutting down Player & Searching Service...")
    if _db_engine is not None:
        logger.info("Closing database connections...")
        await _db_engine.dispose()
        logger.info("Database connections closed.")

    storage = get_storage_adapter()
    await storage.close()

    logger.info("Service shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Player & Searching Service for MISISTUBE",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
    lifespan=lifespan,
)

app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_rfc7807_handlers(app)

app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(playback.router, prefix="/api/v1", tags=["Playback"])
app.include_router(videos.router, prefix="/api/v1", tags=["videos"])



@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Player & Searching Service is running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": f"{settings.APP_NAME}",
        "env": f"{settings.APP_ENV}",
    }
