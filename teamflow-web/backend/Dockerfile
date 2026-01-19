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

# Stage 3: Runner
FROM python:3.13-slim AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 appuser
COPY --from=builder /app/.venv .venv
COPY --from=builder --chown=appuser:appuser /app/app app
USER appuser
# Add .venv/bin to PATH for uvicorn
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
