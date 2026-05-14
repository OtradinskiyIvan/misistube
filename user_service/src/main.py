from fastapi import Depends, FastAPI
from src.api.router import router as api_router
from src.core.logging import configure_structlog
from src.core.settings import settings
from src.deps import get_correlation_id

configure_structlog(log_level=settings.LOG_LEVEL, service_name=settings.APP_NAME)

app = FastAPI(
    title=settings.APP_NAME,
    description="User management microservice (CRUD, profiles, security)",
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    dependencies=[Depends(get_correlation_id)],
)

app.include_router(api_router, prefix="/api/v1")

# Для локального запуска
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)