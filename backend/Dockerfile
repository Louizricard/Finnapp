# Multi-stage Dockerfile for Finnapp Backend
# Stage 1: Build virtual environment with uv
FROM python:3.12-slim AS builder

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

WORKDIR /build

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies directly into target virtual environment /app/.venv
RUN uv sync --no-dev --no-install-project

# Stage 2: Runtime image
FROM python:3.12-slim AS runner

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY app /app/app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python3", "-m", "uvicorn", "app.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
