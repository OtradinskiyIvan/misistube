import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI

ROOT_DIRECTORY = Path(__file__).resolve().parents[2]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from src.api.router import router as api_router
from src.api.error_handlers import register_exception_handlers
from src.core.logging import configure_structlog
from src.core.settings import settings
from src.deps import get_correlation_id
from shared.database.session import init_engine

configure_structlog(log_level=settings.LOG_LEVEL, service_name=settings.APP_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    # Use PostgreSQL if configured, otherwise fallback to SQLite in-memory for development
    db_url = settings.DATABASE_URL or "sqlite+aiosqlite:///:memory:"
    init_engine(db_url, echo=settings.DATABASE_ECHO)
    
    # Auto-create tables for in-memory/file SQLite
    if not settings.DATABASE_URL or "sqlite" in str(settings.DATABASE_URL):
        from shared.database.session import _engine
        from src.infrastructure.models import Base
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="User management microservice (CRUD, profiles, security)",
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    dependencies=[Depends(get_correlation_id)],
    lifespan=lifespan,
)

# Register exception handlers
register_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")

# Для локального запуска
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)