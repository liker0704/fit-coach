# ============================================================================
# Production Dockerfile for FitCoach Backend
# Multi-stage build with security best practices
# ============================================================================

# ============================================================================
# Stage 1: Base - Python dependencies and system packages
# ============================================================================
FROM python:3.11-slim AS base

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client for health checks
    postgresql-client \
    # Required for psycopg2
    libpq-dev \
    # Required for some Python packages
    gcc \
    python3-dev \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r fitcoach && \
    useradd -r -g fitcoach -u 1000 -m -s /bin/bash fitcoach

# Set working directory
WORKDIR /app

# ============================================================================
# Stage 2: Dependencies - Install Python packages
# ============================================================================
FROM base AS dependencies

# Copy only dependency files for better layer caching
COPY --chown=fitcoach:fitcoach requirements.txt pyproject.toml ./

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 3: Production - Final optimized image
# ============================================================================
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Security: Prevent container from running as root
    USER=fitcoach \
    UID=1000 \
    GID=1000

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (matching the UID from dependencies stage)
RUN groupadd -r fitcoach -g ${GID} && \
    useradd -r -g fitcoach -u ${UID} -m -s /bin/bash fitcoach

# Set working directory
WORKDIR /app

# Copy Python packages from dependencies stage
COPY --from=dependencies --chown=fitcoach:fitcoach /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies --chown=fitcoach:fitcoach /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=fitcoach:fitcoach ./app ./app
COPY --chown=fitcoach:fitcoach ./alembic ./alembic
COPY --chown=fitcoach:fitcoach ./alembic.ini ./alembic.ini

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/uploads && \
    chown -R fitcoach:fitcoach /app

# Switch to non-root user
USER fitcoach

# Expose port (documenta purpose only, not opening ports)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ============================================================================
# Labels for metadata
# ============================================================================
LABEL maintainer="FitCoach Team" \
      version="1.0.0" \
      description="FitCoach Backend - Production Ready" \
      security.non-root="true" \
      security.user="fitcoach:1000"

# ============================================================================
# Stage 4: Development - For local development with hot reload
# ============================================================================
FROM dependencies AS development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest>=7.4.0 \
    pytest-asyncio>=0.21.0 \
    httpx>=0.26.0 \
    black>=24.0.0 \
    ruff>=0.2.0 \
    mypy>=1.8.0

# Copy application code
COPY --chown=fitcoach:fitcoach . .

# Switch to non-root user
USER fitcoach

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
