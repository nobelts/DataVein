#!/bin/bash
# DataVein Status Check Script
# Quickly check if all services are running correctly

echo "DataVein System Status Check"
echo "================================"

# Check Docker containers
echo "Docker Containers:"
docker-compose -f infra/docker-compose.yml ps

echo ""

# Check API health
echo "API Health Check:"
if curl -f -s localhost:8000/health > /dev/null; then
    HEALTH_RESPONSE=$(curl -s localhost:8000/health)
    echo "API is running: $HEALTH_RESPONSE"
else
    echo "API is not responding"
fi

echo ""

# Check database connection
echo "Database Connection:"
if docker-compose -f infra/docker-compose.yml exec -T postgres pg_isready > /dev/null 2>&1; then
    echo "PostgreSQL is ready"
else
    echo "PostgreSQL is not ready"
fi

echo ""

# Check Redis connection  
echo "Redis Connection:"
if docker-compose -f infra/docker-compose.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "Redis is ready"
else
    echo "Redis is not ready"
fi

echo ""

# Check MinIO
echo "MinIO Storage:"
if curl -f -s localhost:9000/minio/health/ready > /dev/null 2>&1; then
    echo "MinIO is ready"
else
    echo "MinIO is not ready"
fi

echo ""

# Check Python environment
echo "Python Environment:"
if [ -d ".venv" ]; then
    echo "Virtual environment exists"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "Python version: $(python --version)"
        echo "Installed packages: $(pip list | wc -l) packages"
    fi
else
    echo "Virtual environment not found - run 'make setup'"
fi

echo ""
echo "Quick Actions:"
echo "  make up      - Start all services"
echo "  make down    - Stop all services" 
echo "  make test    - Run tests"
echo "  make health  - Simple health check"
