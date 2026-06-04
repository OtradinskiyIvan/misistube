import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from shared.database.session import Base, init_engine

from .core.logger_setup import get_logger_with_file
from .core.settings import AuthSettings
from .presentations.error_handlers import register_exception_handlers
from .presentations.routers.auth import router as auth_router
from .presentations.routers.health import router as health_router

load_dotenv()
settings = AuthSettings()
log_file = Path(__file__).resolve().parents[2] / "logs" / "authorization_service.log"
logger = get_logger_with_file(settings.APP_NAME, settings.LOG_LEVEL, log_file)



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Authorization Service...")
    engine = init_engine(settings.DATABASE_URL, echo=settings.APP_ENV == "development")

    # В development-режиме таблицы создаются автоматически.
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}")

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")

    return response

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
