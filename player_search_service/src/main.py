from fastapi import FastAPI
from src.api.routers import search, playback

app = FastAPI(
    title="Player & Searching Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(search.router, prefix="/api/v1")
app.include_router(playback.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}