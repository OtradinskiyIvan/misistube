FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/

COPY user_service/requirements.txt /app/user_service/
RUN pip install --no-cache-dir -r /app/user_service/requirements.txt

COPY user_service/ /app/user_service/

EXPOSE 8001

CMD ["uvicorn", "user_service.src.main:app", "--host", "0.0.0.0", "--port", "8001"]
