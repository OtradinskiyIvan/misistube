FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/

COPY interaction_service/requirements.txt /app/interaction_service/
RUN pip install --no-cache-dir -r /app/interaction_service/requirements.txt

COPY interaction_service/ /app/interaction_service/

EXPOSE 8002

CMD ["uvicorn", "interaction_service.src.main:app", "--host", "0.0.0.0", "--port", "8002"]
