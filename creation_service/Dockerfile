FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy asyncpg aiobotocore pydantic pydantic-settings python-dotenv python-multipart
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*