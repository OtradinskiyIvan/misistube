FROM python:3.12-slim

WORKDIR /app

COPY authorization_service/requirements.txt /app/authorization_service/requirements.txt
RUN pip install --no-cache-dir -r /app/authorization_service/requirements.txt

COPY authorization_service/ /app/authorization_service/
COPY shared/ /app/shared/

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

WORKDIR /app

EXPOSE 8001

CMD ["uvicorn", "authorization_service.src.main:app", "--host", "0.0.0.0", "--port", "8001"]
