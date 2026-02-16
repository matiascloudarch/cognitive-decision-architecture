# Dockerfile 
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for networking and health checks
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy configuration files and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy the remaining application source code
COPY . .

# Set default environment variables
ENV CDA_SECRET_KEY="internal_development_secret_key_fixed_32_chars"
ENV PYTHONPATH=/app

# Informative port exposure
EXPOSE 8000
EXPOSE 8001

# Default command (overridden by docker-compose)
CMD ["python3"]