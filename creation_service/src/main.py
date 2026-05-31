from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import logging

app = FastAPI(title="Video Studio Service")

origins = [
    "http://localhost:5174",  # Твой фронтенд (Vite)
    "http://localhost:3000",  # Если используешь Create React App
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # или ["*"] для разработки (но осторожно)
    allow_credentials=True,
    allow_methods=["*"],  # разрешаем все методы, включая OPTIONS, POST, GET
    allow_headers=["*"],  # разрешаем все заголовки
)

from src.api.routes import videos
app.include_router(videos.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"{request.method} {request.url} - headers: {dict(request.headers)}")
    response = await call_next(request)
    return response

@app.get("/health")
async def health():
    return {"status": "ok"}

# Подключение роутеров (раскомментировать, когда создадите videos.py)