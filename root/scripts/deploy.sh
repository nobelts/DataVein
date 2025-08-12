#!/bin/bash
# DataVein Complete Deployment Script
# Automates the entire setup process for development or production deployment

set -e  # Exit on any error

echo "DataVein Complete Deployment Starting..."
echo "============================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
if ! command_exists python3; then
    echo "Python 3 is required but not installed"
    exit 1
fi

if ! command_exists docker; then
    echo "Docker is required but not installed"
    exit 1
fi

if ! command_exists docker-compose; then
    echo "Docker Compose is required but not installed" 
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 0 ]]; then
    echo "Python 3.11+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "Prerequisites check passed"

# Setup environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please review and update .env file with your configuration"
else
    echo ".env file already exists"
fi

# Setup Python environment
echo "Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate environment and install dependencies
echo "Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet
echo "Python dependencies installed"

# Start infrastructure services
echo "Starting infrastructure services..."
docker-compose -f infra/docker-compose.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run database migration
echo "Setting up database..."
python scripts/migrate_db.py

# Health check
echo "Performing health check..."
sleep 3

# Start the application
echo "Starting DataVein application..."

# Check if we should start in development or production mode
if [ "${DATAVEIN_ENV:-development}" = "production" ]; then
    echo "Starting in PRODUCTION mode..."
    # Production startup (you can customize this)
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
    
    # Start Celery worker
    ./scripts/start_worker.sh &
    
    echo "DataVein started in production mode"
    echo "API available at: http://localhost:8000"
    echo "Health check: http://localhost:8000/health"
    
else
    echo "Development mode - services started via Docker Compose"
    echo ""
    echo "DataVein deployment completed successfully!"
    echo ""
    echo "Quick start commands:"
    echo "  source activate.sh   - Activate Python environment"  
    echo "  make health          - Check if everything is running"
    echo "  make test            - Run tests"
    echo "  make down            - Stop all services"
    echo ""
    echo "API available at: http://localhost:8000"
    echo "Health check: http://localhost:8000/health"
    echo "API docs: http://localhost:8000/docs"
fi

echo ""
echo "DataVein is ready for use!"
