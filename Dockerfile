# Use Python 3.12 slim as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY app/ ./app/
COPY tools/ ./tools/

# Set Python path
ENV PYTHONPATH=/app

# Set entrypoint
ENTRYPOINT ["python", "-m", "app.main", "ping"] 