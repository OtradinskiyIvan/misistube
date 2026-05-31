FROM python:3.14-slim
WORKDIR /app
COPY interaction_service/requirements.txt /app/interaction_service/requirements.txt
RUN pip install --no-cache-dir -r /app/interaction_service/requirements.txt
COPY interaction_service/ /app/interaction_service/
COPY shared/ /app/shared/
USER appuser
WORKDIR /app/interaction_service
EXPOSE 8002
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
