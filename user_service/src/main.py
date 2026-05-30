import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from .api.error_handlers import register_exception_handlers
from .api.router import router as api_router
from .core.logging import configure_structlog
from .core.middleware import CorrelationIDMiddleware
from .core.settings import settings
from .deps import init_db_manager
from .infrastructure.database.manager import DatabaseManager

configure_structlog(log_level=settings.LOG_LEVEL, service_name=settings.APP_NAME)

db_manager: DatabaseManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global db_manager

    db_url = str(settings.DATABASE_URL)
    db_manager = init_db_manager(db_url, echo=settings.DATABASE_ECHO)

    await db_manager.create_tables()

    yield

    await db_manager.close()


app = FastAPI(
    title=settings.APP_NAME,
    description="User management microservice (CRUD, profiles, security)",
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(CorrelationIDMiddleware)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
