# Multi-stage build for Refyne API

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-api.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-api.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 refyne && \
    mkdir -p /app/storage/{uploads,outputs,temp} && \
    chown -R refyne:refyne /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=refyne:refyne src/ ./src/
COPY --chown=refyne:refyne api/ ./api/
COPY --chown=refyne:refyne data/sample/ ./data/sample/

# Switch to non-root user
USER refyne

# Expose port (Railway sets PORT dynamically)
EXPOSE 8000

# Run the API (use PORT env var for Railway compatibility)
CMD sh -c "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"