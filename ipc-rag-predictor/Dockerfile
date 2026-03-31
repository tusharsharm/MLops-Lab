FROM python:3.11-slim

WORKDIR /app

# No apt-get needed — all packages have pre-built wheels
RUN useradd -m -u 1000 appuser

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/

# Create directories
RUN mkdir -p /app/data /app/mlruns && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]