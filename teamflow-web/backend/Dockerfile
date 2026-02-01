# Stage 1: Dependencies
FROM python:3.13-slim AS deps
WORKDIR /app
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir uv && uv sync

# Stage 2: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
# Install uv to use in this stage
RUN pip install --no-cache-dir uv
COPY --from=deps /app/.venv .venv
COPY pyproject.toml uv.lock* ./
COPY . .
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
COPY --from=builder --chown=appuser:appuser /app/app app

# Set up environment for Dapr
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Dapr configuration (sidecar runs on localhost:3500)
ENV DAPR_HTTP_PORT=3500
ENV DAPR_GRPC_PORT=50001

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Health check - Dapr sidecar must be healthy too
# The health endpoint checks both app and Dapr sidecar availability
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
# Dapr sidecar will be injected by Kubernetes at runtime
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "null"]
