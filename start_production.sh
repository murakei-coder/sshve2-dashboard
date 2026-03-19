#!/bin/bash
# Production startup script for Linux/Mac
# Linux/Mac用の本番環境起動スクリプト

echo "========================================="
echo "SSHVE2 Dashboard - Production Mode"
echo "========================================="
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update dependencies
echo "Checking dependencies..."
pip install -r requirements_production.txt

# Start Gunicorn
echo ""
echo "Starting Gunicorn server..."
echo "Access URL: http://YOUR_SERVER_IP:8000"
echo ""
echo "To stop: Press Ctrl+C or run: pkill -f gunicorn"
echo "========================================="
echo ""

gunicorn -c gunicorn_config.py wsgi:application
