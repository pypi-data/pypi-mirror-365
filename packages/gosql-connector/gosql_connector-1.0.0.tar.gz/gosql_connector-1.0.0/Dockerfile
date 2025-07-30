# Multi-stage Dockerfile for GoSQL development and production

# Build stage - Go compilation
FROM golang:1.21-alpine AS go-builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Set working directory
WORKDIR /app

# Copy Go source code
COPY ../go/ ./go/

# Build Go shared library
WORKDIR /app/go
RUN CGO_ENABLED=1 go build -buildmode=c-shared -o libgosql.so main.go

# Python build stage
FROM python:3.10-slim AS python-builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python package source
COPY . .

# Copy Go shared library from previous stage
COPY --from=go-builder /app/go/libgosql.so ./gosql/lib/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Build Python package
RUN python -m build

# Production stage
FROM python:3.10-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash gosql

# Set working directory
WORKDIR /app

# Copy built package from builder stage
COPY --from=python-builder /app/dist/*.whl /tmp/

# Install GoSQL
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Switch to non-root user
USER gosql

# Set entrypoint
ENTRYPOINT ["python"]

# Development stage
FROM python-builder AS development

# Install additional development tools
RUN pip install --no-cache-dir \
    jupyter \
    ipython \
    pytest-xdist \
    pytest-benchmark

# Install GoSQL in development mode
RUN pip install -e .

# Expose Jupyter port
EXPOSE 8888

# Set development entrypoint
ENTRYPOINT ["/bin/bash"]

# Testing stage
FROM development AS testing

# Copy test files
COPY tests/ ./tests/
COPY benchmarks/ ./benchmarks/

# Run tests
RUN pytest tests/ -v

# Benchmark stage  
FROM testing AS benchmark

# Install benchmark dependencies
RUN pip install --no-cache-dir \
    mysql-connector-python \
    psycopg2-binary \
    pyodbc \
    matplotlib \
    pandas \
    seaborn

# Run benchmarks
RUN python -m gosql.benchmarks.benchmark --output benchmark_results.json

# Documentation stage
FROM development AS docs

# Install documentation dependencies
RUN pip install --no-cache-dir \
    sphinx \
    sphinx-rtd-theme \
    myst-parser \
    sphinx-autodoc-typehints

# Copy documentation source
COPY docs/ ./docs/

# Build documentation
RUN cd docs && make html

# Expose documentation server port
EXPOSE 8000

# Start documentation server
CMD ["python", "-m", "http.server", "8000", "--directory", "docs/_build/html"]
