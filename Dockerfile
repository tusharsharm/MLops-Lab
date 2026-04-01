# Multi-target Dockerfile for MLops-Lab (workspace root)

### Frontend target (dev)
FROM node:20-bullseye-slim AS frontend
WORKDIR /app
COPY ipc-rag-predictor/frontend/package.json ipc-rag-predictor/frontend/package-lock.json ./
# Install including devDependencies so build tools like `vite` are available
RUN npm install --include=dev
COPY ipc-rag-predictor/frontend/ ./
# Ensure vite CLI is available at build time and build static frontend
RUN npm install -g vite@8 && npx vite build
RUN npm install -g serve --silent --no-audit --no-fund
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]

### API target
FROM python:3.11-slim AS api
WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY ipc-rag-predictor/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY ipc-rag-predictor/app ./app
RUN mkdir -p /app/data /app/mlruns && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
