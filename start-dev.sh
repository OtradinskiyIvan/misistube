#!/bin/bash
set -e

cleanup() {
    echo "Stopping all services..."
    kill -- -$$ 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "Starting backend services..."

cd /app/authorization_service
DATABASE_URL="${AUTH_DB_URL:-postgresql+asyncpg://misistube:misistube_secret@localhost:5433/misistube_auth}" \
APP_ENV="${APP_ENV:-development}" \
JWT_SECRET="${JWT_SECRET:-dev-secret-key-not-for-production}" \
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &

cd /app/user_service
DATABASE_URL="${USER_DB_URL:-postgresql+asyncpg://misistube:misistube_secret@localhost:5432/misistube_users}" \
APP_ENV="${APP_ENV:-development}" \
DATABASE_ECHO="${DATABASE_ECHO:-false}" \
LOG_LEVEL="${LOG_LEVEL:-INFO}" \
JWT_SECRET="${JWT_SECRET:-dev-secret-key-not-for-production}" \
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload &

cd /app/interaction_service
DATABASE_URL="${INTERACTION_DB_URL:-postgresql+asyncpg://misistube:misistube_secret@localhost:5434/misistube_interactions}" \
APP_ENV="${APP_ENV:-development}" \
DATABASE_ECHO="${DATABASE_ECHO:-false}" \
LOG_LEVEL="${LOG_LEVEL:-INFO}" \
JWT_SECRET="${JWT_SECRET:-dev-secret-key-not-for-production}" \
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload &

echo "Starting frontend services..."

cd /app/frontend/authorization_service
VITE_AUTH_PROXY_TARGET="${VITE_AUTH_PROXY_TARGET:-http://localhost:8000}" \
npm run dev -- --host 0.0.0.0 &

cd /app/frontend/user_service
VITE_AUTH_PROXY_TARGET="${VITE_AUTH_PROXY_TARGET:-http://localhost:8000}" \
VITE_USER_PROXY_TARGET="${VITE_USER_PROXY_TARGET:-http://localhost:8001}" \
npm run dev -- --host 0.0.0.0 &

cd /app/frontend/interaction_service
VITE_INTERACTION_PROXY_TARGET="${VITE_INTERACTION_PROXY_TARGET:-http://localhost:8002}" \
npm run dev -- --host 0.0.0.0 &

echo "All services started. Waiting..."
wait
