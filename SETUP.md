# DataVein Setup Guide

## Prerequisites
- Python 3.11+ 
- Node.js 16+
- Docker & Docker Compose

## Quick Start

### 1. Environment Setup
```bash
# Clone and navigate
git clone <repository-url>
cd datavein-work

# Copy environment template
cp .env.example .env
# Update .env with your configuration
```

### 2. Automated Setup (Recommended)
```bash
# Complete setup with Makefile
make setup      # Install dependencies
source activate.sh  # Activate environment
make up         # Start all services
```

### 3. Manual Setup (Alternative)

**Start Infrastructure:**
```bash
cd root/infra
docker-compose up -d
```

**Backend Setup:**
```bash
cd root
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# Start backend
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
cd root/frontend
npm install
npm run dev
```

### 4. Verify Installation
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: `curl http://localhost:8000/health`

## Services
- **PostgreSQL**: Database (port 5432)
- **Redis**: Caching (port 6379)
- **MinIO**: Object Storage (port 9000)

## Development Commands
```bash
# Run tests
make test           # Backend tests
make frontend-test  # Frontend tests

# Code formatting
make fmt

# Stop services
make down
```

## Project Structure
```
root/
├── backend/           # FastAPI API
├── worker/            # Celery tasks
├── frontend/          # React + TypeScript
├── infra/             # Docker configs
├── scripts/           # Utilities
└── tests/             # Test suites
```

## Troubleshooting

**Python Dependencies:**
```bash
# Ensure correct Python version
pyenv install 3.11.9
pyenv local 3.11.9

# Reset environment
rm -rf .venv
make setup
```

**Docker Issues:**
```bash
# Check container status
docker-compose -f infra/docker-compose.yml ps

# Restart services
docker-compose -f infra/docker-compose.yml down
docker-compose -f infra/docker-compose.yml up -d
```

**Port Conflicts:**
Ensure ports 3000, 8000, 5432, 6379, 9000 are available.

## Environment Variables
Key variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection
- `SECRET_KEY`: JWT secret (change in production)
- `REDIS_URL`: Redis connection
- `AWS_ACCESS_KEY_ID/SECRET`: MinIO credentials
