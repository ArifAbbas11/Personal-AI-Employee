# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install common Python dependencies directly
RUN pip install --no-cache-dir \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client \
    watchdog \
    schedule \
    requests \
    pathlib \
    python-dotenv \
    tweepy \
    groq

# Copy watchers directory
COPY watchers/ ./watchers/
COPY workflows/ ./workflows/

# Copy Ralph Groq orchestrator
COPY ralph_groq_orchestrator.py ./
COPY ralph_groq_setup.sh ./

# Make scripts executable
RUN chmod +x ralph_groq_setup.sh

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VAULT_PATH=/vault
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Default command
CMD ["python3", "watchers/main.py"]
