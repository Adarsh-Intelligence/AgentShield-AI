# ==============================================================================
# AgentShield AI - Production Dockerfile
# Base Image: Python 3.12 Slim (Minimal & Secure)
# ==============================================================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies for compilation if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt


# ==============================================================================
# Runtime Stage
# ==============================================================================
FROM python:3.12-slim AS runtime

# Security hardening: Create non-root user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Install runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Ensure user binaries are on PATH
ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Copy application source code
COPY --chown=appuser:appgroup alembic.ini .
COPY --chown=appuser:appgroup migrations ./migrations
COPY --chown=appuser:appgroup backend ./backend

USER appuser

EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production startup command
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
