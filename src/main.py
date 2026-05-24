from fastapi import FastAPI
from src.api.routes import videos   # пока не создали, закомментируем

app = FastAPI(title="Video Studio Service")

@app.get("/health")
async def health():
    return {"status": "ok"}

# Подключение роутеров (раскомментировать, когда создадите videos.py)
app.include_router(videos.router)