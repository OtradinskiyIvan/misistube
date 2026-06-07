FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY shared/ /app/shared/
RUN pip install --no-cache-dir -e /app/shared/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt uvicorn httpx

COPY authorization_service/ /app/authorization_service/
RUN pip install --no-cache-dir -e /app/authorization_service/

COPY user_service/requirements.txt /app/user_service/requirements.txt
RUN pip install --no-cache-dir -r /app/user_service/requirements.txt
COPY user_service/ /app/user_service/

COPY interaction_service/requirements.txt /app/interaction_service/requirements.txt
RUN pip install --no-cache-dir -r /app/interaction_service/requirements.txt
COPY interaction_service/ /app/interaction_service/

COPY frontend/authorization_service/package*.json /app/frontend/authorization_service/
RUN cd /app/frontend/authorization_service && npm install

COPY frontend/user_service/package*.json /app/frontend/user_service/
RUN cd /app/frontend/user_service && npm install

COPY frontend/interaction_service/package*.json /app/frontend/interaction_service/
RUN cd /app/frontend/interaction_service && npm install

COPY frontend/ /app/frontend/

COPY start-dev.sh /app/start-dev.sh
RUN chmod +x /app/start-dev.sh

EXPOSE 8000 8001 8002 5173 5174 5175

CMD ["/app/start-dev.sh"]
