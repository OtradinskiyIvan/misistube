# src/main.py
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import Base, init_engine, dispose_engine
from shared.logger import get_logger, configure_logging

from src.api.routers import search, playback
from src.core.config import settings
from src.core.exceptions import register_exception_handlers


load_dotenv()

configure_logging()
logger = get_logger("player_search_service", level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения:
    - Startup: инициализация БД, создание таблиц (в dev), подключение к инфраструктуре
    - Shutdown: корректное закрытие соединений
    """
    logger.info("Starting Player & Searching Service...", env=settings.app_env)
    
    engine = init_engine(
        database_url=settings.database_url,
        echo=settings.app_env == "development"  # логирование SQL-запросов в dev
    )
    
    # Авто-создание таблиц (ТОЛЬКО для development!)
    if settings.app_env == "development":
        logger.info("🗄 Creating database tables (development mode)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created")
    
    yield
    
    logger.info("Shutting down Player & Searching Service...")
    await dispose_engine()
    logger.info("Shutdown layer & Searching Service complete")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Player & Searching Service for MISISTUBE",
    docs_url="/docs" if settings.app_env == "development" else None,  # отключаем Swagger в prod
    redoc_url="/redoc" if settings.app_env == "development" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else ["https://misistube.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(playback.router, prefix="/api/v1", tags=["Playback"])

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Player & Searching Service is running", "docs": "/docs"}