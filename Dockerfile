# ============================================================================
# SparkMinds AI — Multi-Stage Production Dockerfile
# Stage 1: Build Responsive React + TypeScript + Vite PWA (frontend/dist)
# Stage 2: Run FastAPI + SQLite WAL Production Server serving PWA & /api/*
# ============================================================================

FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS production-runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SPARKMINDS_ENV=production \
    PORT=8000

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

RUN mkdir -p /app/backend/data/backups /app/backend/data/uploads

WORKDIR /app/backend
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

