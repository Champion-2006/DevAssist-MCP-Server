# Build Stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime Stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser -d /app -s /sbin/nologin mcpuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs && chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LOG_FILE=logs/devassist.log

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import mcp; print('healthy')" || exit 1

# Entry point
ENTRYPOINT ["python", "server.py"]
