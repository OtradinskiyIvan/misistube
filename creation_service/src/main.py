from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from src.core.config import settings

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

SENSITIVE_HEADERS = frozenset({"authorization", "cookie", "x-api-key", "set-cookie"})

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "creation_service.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.infrastructure.database.models import Base
    from src.infrastructure.database.session import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import text
        await conn.execute(
            text("UPDATE videos SET user_id = '00000000-0000-0000-0000-000000000000' WHERE user_id IS NULL")
        )
        try:
            await conn.execute(
                text("ALTER TABLE videos ALTER COLUMN user_id SET NOT NULL")
            )
        except Exception:
            pass
    yield
    await engine.dispose()

app = FastAPI(title="Video Studio Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.routes import videos
app.include_router(videos.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    safe_headers = {
        k: v if k.lower() not in SENSITIVE_HEADERS else "***"
        for k, v in request.headers.items()
    }
    logging.info(f"{request.method} {request.url} - headers: {safe_headers}")
    try:
        response = await call_next(request)
    except Exception as e:
        logging.exception(f"Unhandled exception processing {request.method} {request.url}")
        raise
    if response.status_code >= 500:
        logging.error(f"{request.method} {request.url} -> {response.status_code}")
    return response

@app.get("/health")
async def health():
    return {"status": "ok"}
