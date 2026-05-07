from fastapi import FastAPI
from src.api.router import router as api_router

app = FastAPI(
    title="User Service",
    description="User management microservice (CRUD, profiles, security)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix="/api/v1")

# Для локального запуска
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)