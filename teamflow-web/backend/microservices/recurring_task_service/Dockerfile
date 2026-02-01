# T051: Dockerfile for Recurring Task Service Microservice
# Multi-stage Python 3.13-slim build optimized for Dapr sidecar integration

# Stage 1: Dependencies
FROM python:3.13-slim AS deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir uv && uv sync

# Stage 2: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY --from=deps /app/.venv .venv
COPY requirements.txt .
RUN uv sync

# Stage 3: Runner - Optimized for Dapr sidecar integration
FROM python:3.13-slim AS runner
WORKDIR /app

# Install runtime dependencies for Dapr communication
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 appuser

# Copy virtual environment and application code
COPY --from=builder /app/.venv .venv
COPY --from=builder --chown=appuser:appuser /app/main.py main.py

# Set up environment for Dapr
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Dapr configuration (sidecar runs on localhost:3500)
ENV DAPR_HTTP_PORT=3500
ENV DAPR_GRPC_PORT=50001
ENV BACKEND_API_URL="http://teamflow-backend.teamflow.svc.cluster.local:8000"

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8002

# Health check - Dapr sidecar must be healthy too
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

# Start the application
# Dapr sidecar will be injected by Kubernetes at runtime
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--log-config", "null"]
