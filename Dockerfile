# Use a very small base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install only essential system dependencies and clean up in the same layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements/pyproject first to leverage Docker cache
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Install the package in editable mode for development
RUN pip install -e .

# Command to run the engine
CMD ["python3", "-m", "uvicorn", "cda.kernel.engine:app", "--host", "0.0.0.0", "--port", "8000"]