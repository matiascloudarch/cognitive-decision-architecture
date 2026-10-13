# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

FROM python:3.9-slim

WORKDIR /app

# Copy dependency files
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy full application code
COPY . .

# Ensure execution permissions for audit and utility scripts
RUN chmod +x ./cda/scripts/*.sh 2>/dev/null || true

# Expose server port
EXPOSE 8002

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV CDA_SECRET_HEX=707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f

# Default command to run the unified server
CMD ["uvicorn", "cda.server:app", "--host", "0.0.0.0", "--port", "8002"]