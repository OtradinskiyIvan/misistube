import sys
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.database.session import Base, init_engine

from src.api.routers import playback, search
from src.core.config import get_settings
from src.core.exceptions import register_rfc7807_handlers
from src.core.logger import setup_service_logger
from src.core.middleware import CorrelationIdMiddleware

load_dotenv()
settings = get_settings()
logger = setup_service_logger("player_search_service", level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения:
    - Startup: инициализация БД, создание таблиц (в dev), подключение к инфраструктуре
    - Shutdown: корректное закрытие соединений
    """
    logger.info("Starting Player & Searching Service... [env=%s]", settings.APP_ENV)

    engine = init_engine(
        database_url=settings.DATABASE_URL,
        echo=settings.APP_ENV == "development"  # логирование SQL-запросов в dev
    )

    # Авто-создание таблиц (ТОЛЬКО для development!)
    if settings.APP_ENV == "development":
        logger.info("🗄 Creating database tables (development mode)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created")

    yield

    logger.info("Shutting down Player & Searching Service...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Player & Searching Service for MISISTUBE",
    docs_url="/docs" if settings.APP_ENV == "development" else None,  # отключаем Swagger в prod
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
    lifespan=lifespan,
)

app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_rfc7807_handlers(app)

app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(playback.router, prefix="/api/v1", tags=["Playback"])

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
