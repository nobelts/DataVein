#!/bin/bash

# Celery Worker Startup Script for DataVein Pipeline Processing
# This script starts the Celery worker for processing pipeline tasks

echo "Starting DataVein Celery Worker..."

# Set environment variables if not already set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start Celery worker
echo "Starting Celery worker for pipeline processing..."
celery -A backend.app.pipeline.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=10 \
    --time-limit=1800 \
    --soft-time-limit=1500

echo "Celery worker stopped."
