# Multi-stage build: Production and Development
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Production stage
FROM base as production

# Copy the application
COPY . .

# Install the package
RUN pip install --no-cache-dir .

# Create non-root user
RUN useradd --create-home --shell /bin/bash dbit
USER dbit

ENTRYPOINT ["dbit"]
CMD ["--help"]

# Development stage
FROM base as development

# Copy the application
COPY . .

# Install the package with development dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Install pre-commit hooks
RUN pre-commit install --install-hooks || true

# Create non-root user
RUN useradd --create-home --shell /bin/bash dbit
USER dbit

# Default to interactive shell for development
ENTRYPOINT ["/bin/bash"]
