FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt httpx

COPY authorization_service/ /app/authorization_service/

EXPOSE 8000

CMD ["uvicorn", "authorization_service.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
