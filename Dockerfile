# syntax=docker/dockerfile:1
# Single-service image: build the React app, then serve it + the API from FastAPI.

# ---- Stage 1: build the React frontend ----
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Production build defaults to same-origin API calls (see src/api.ts).
RUN npm run build

# ---- Stage 2: Python runtime serving API + built frontend ----
FROM python:3.11-slim AS runtime
WORKDIR /app

# Install the backend (fastapi/uvicorn come from pyproject dependencies).
COPY pyproject.toml README.md ./
COPY order_chaos/ ./order_chaos/
COPY api/ ./api/
RUN pip install --no-cache-dir .

# Bring in the built static assets and point the app at them explicitly
# (robust regardless of where the `api` package is imported from).
COPY --from=frontend /app/frontend/dist ./frontend/dist
ENV STATIC_DIR=/app/frontend/dist

ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
