# Dockerfile for SSHVE2 Dashboard
# Docker用の設定ファイル

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py

# Run gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "wsgi:application"]
