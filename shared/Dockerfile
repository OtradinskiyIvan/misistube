FROM python:3.12-slim AS shared-builder
WORKDIR /app
COPY shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/
