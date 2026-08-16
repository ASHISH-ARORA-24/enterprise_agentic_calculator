# Multi-stage Dockerfile for the Calculator Service.
#
# Stage 1 (builder): installs dependencies using uv.
# Stage 2 (final):   copies only what is needed to run — no build tools.
#
# This keeps the production image small and reduces the attack surface.

# ---------------------------------------------------------------------------
# Stage 1 — builder
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Install uv — our package manager.
# We copy it from the official uv image rather than installing via pip.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set the working directory inside the container.
WORKDIR /app

# Copy only the files needed to install dependencies first.
# Docker caches each layer — if these files don't change, the install
# layer is reused on the next build (much faster builds).
COPY pyproject.toml .
COPY apps/calculator_service/pyproject.toml apps/calculator_service/

# Install dependencies into a virtual environment inside the container.
# --no-dev skips dev tools (ruff, pytest, etc.) — not needed in production.
# --no-editable installs packages as regular files, not symlinks.
RUN uv sync --package calculator-service --no-dev --no-editable

# ---------------------------------------------------------------------------
# Stage 2 — final image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS final

# Create a non-root user and group for running the service.
# Running as root inside a container is a security risk.
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy the virtual environment from the builder stage.
# We get all the installed packages but none of the build tools.
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code.
COPY apps/calculator_service/app ./app

# Make the virtual environment's Python the default.
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user.
USER appuser

# Document which port the service listens on.
# This does not actually publish the port — that happens at "docker run" time.
EXPOSE 8000

# Health check — Docker will call this periodically.
# If it fails, Docker marks the container as unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"

# Start the service.
# --host 0.0.0.0 means accept connections from outside the container.
# --workers 1 keeps it simple for now.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
