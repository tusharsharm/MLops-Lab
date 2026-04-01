# Multi-target Dockerfile for MLops-Lab (workspace root)

### Frontend target (dev)
FROM node:18-bullseye-slim AS frontend
WORKDIR /app
COPY ipc-rag-predictor/frontend/package.json ipc-rag-predictor/frontend/package-lock.json ./
RUN npm install --silent --no-audit --no-fund
COPY ipc-rag-predictor/frontend/ ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

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
