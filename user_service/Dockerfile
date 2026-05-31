FROM python:3.14-slim

WORKDIR /app

COPY user_service/requirements.txt /app/user_service/requirements.txt
RUN pip install --no-cache-dir -r /app/user_service/requirements.txt

COPY user_service/ /app/user_service/
COPY shared/ /app/shared/

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

WORKDIR /app/user_service

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
