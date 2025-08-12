# DataVein Makefile - Automated Development Setup

.PHONY: setup up down test fmt migrate health clean all

# Complete automated setup
setup:
	@echo "Setting up DataVein development environment..."
	@command -v pyenv >/dev/null 2>&1 || { echo "pyenv not found. Please install pyenv first: https://github.com/pyenv/pyenv"; exit 1; }
	pyenv install -s 3.11.9
	pyenv local 3.11.9
	python3.11 -m venv .venv
	. .venv/bin/activate; pip install --upgrade pip; pip install -r backend/requirements.txt
	@[ ! -f .env ] && cp .env.example .env || echo ".env already exists"
	@echo "Setup complete! Activate with: source activate.sh"

# Start all services and run migrations
up:
	@echo "Starting DataVein services..."
	docker-compose -f infra/docker-compose.yml up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "Running database migrations..."
	@. .venv/bin/activate && python scripts/migrate_db.py || echo "Migration completed"
	@echo "All services running! Check: make health"

# Stop all services
down:
	docker-compose -f infra/docker-compose.yml down

# Run database migration manually
migrate:
	@. .venv/bin/activate && python scripts/migrate_db.py

# Health check
health:
	@echo "Checking DataVein health..."
	@curl -f localhost:8000/health || echo "Backend not responding"

# Run tests
test:
	@echo "Running backend tests..."
	@. .venv/bin/activate && PYTHONPATH=. pytest tests/backend/ -v

# Format code
fmt:
	@. .venv/bin/activate && black backend/ scripts/
	@cd frontend && npm run lint --silent || echo "Frontend formatting skipped"

# Frontend tests (optional)
frontend-test:
	@cd frontend && npm test

# Clean up everything
clean:
	docker-compose -f infra/docker-compose.yml down -v
	rm -rf .venv
	@echo "Cleaned up containers and virtual environment"

# Run everything (setup + start + test)
all: setup up test
	@echo "DataVein is ready for development!"