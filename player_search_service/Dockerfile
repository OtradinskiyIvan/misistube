# player_search_service/Dockerfile
FROM python:3.11-slim-bookworm

# 🔹 Переменные окружения
# 🔹 PYTHONPATH включает и src, и shared для корректных импортов
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src:/shared

# 🔹 Рабочая директория
WORKDIR /app

# 🔹 Системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 🔹 1. Копируем shared/ (путь относительно корня монорепозитория)
COPY shared /shared

# 🔹 2. Копируем pyproject.toml сервиса
COPY player_search_service/pyproject.toml ./

# 🔹 3. Копируем src/ сервиса
COPY player_search_service/src/ ./src/

# 🔹 4. Устанавливаем пакет и зависимости
# Теперь доступны импорты и из src/, и из shared/
RUN pip install --upgrade pip && \
    pip install . && \
    pip install gunicorn uvicorn[standard]

# 🔹 Health check для оркестратора
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 🔹 Запуск через Gunicorn + Uvicorn workers
CMD ["gunicorn", "src.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]