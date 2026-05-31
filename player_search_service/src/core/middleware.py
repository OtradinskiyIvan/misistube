import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from shared.logger import correlation_id_var

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Генерируем или берём из заголовка
        cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # Устанавливаем в ContextVar (станет доступен в JSON-логе)
        correlation_id_var.set(cid)
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response