# DataVein - Data Processing Platform

A data processing platform that accepts file uploads (CSV/JSON), processes them through pipeline stages, and outputs Parquet files. Built with FastAPI, PostgreSQL, Celery, and React.

## Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Update .env with your configuration
# At minimum, change the SECRET_KEY for production
```

### 2. Start Infrastructure (Docker)
```bash
# Start database, Redis, and MinIO
cd infra
docker-compose up -d
```

### 3. Setup Python Environment
```bash
# From project root
cd root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 4. Initialize Database
```bash
# Run database migration
python scripts/migrate_db.py
```

### 5. Start Services

**Terminal 1 - Backend API:**
```bash
cd root
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
cd root
source venv/bin/activate
./scripts/start_worker.sh
```

**Terminal 3 - Frontend (optional):**
```bash
cd root/frontend
npm install
npm run dev
```

## API Usage

### 1. Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 3. Upload File
```bash
# Get presigned URL
curl -X POST "http://localhost:8000/uploads/presigned-url" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "data.csv", "file_size": 1024}'

# Upload file to the presigned URL (use the response from above)
# Then complete the upload
curl -X POST "http://localhost:8000/uploads/1/complete" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Start Pipeline
```bash
curl -X POST "http://localhost:8000/pipeline/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"upload_id": 1, "config": {"synthetic_multiplier": 2}}'
```

### 5. Check Pipeline Status
```bash
curl -X GET "http://localhost:8000/pipeline/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Project Structure

```
root/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── pipeline/  # Pipeline processing
│   │   ├── models.py  # Database models
│   │   └── main.py    # FastAPI app
│   └── requirements.txt
├── frontend/          # React frontend (optional)
├── scripts/           # Deployment scripts
│   ├── migrate_db.py  # Database setup
│   └── start_worker.sh # Celery worker
└── infra/             # Infrastructure (Docker)
```

## Pipeline Stages

1. **VALIDATE** - Checks file format and structure
2. **PROFILE** - Analyzes data types, distributions, quality
3. **AUGMENT** - Generates synthetic data (stub)
4. **PARQUETIZE** - Converts to Parquet format (stub)
5. **FINALIZE** - Cleanup and metadata (stub)

Stages 1-2 are fully implemented. Stages 3-5 are stubs for MVP demonstration.

## Alternative Quick Start (Legacy)

```sh
make setup
source activate.sh
make up
# (Optional) Run backend tests locally:
make test
# (Optional) Run frontend tests:
make frontend-test
```
```

> **Tip:** `make up` uses Docker Compose to start backend, worker (Celery), Redis, Postgres, and MinIO. No need to start Redis or the Celery worker manually for normal development.

# Title: Datavein {...}


## Overview
This project is a full-stack application that utilizes FastAPI for the backend, Celery for asynchronous task processing, and React with Tailwind CSS for the frontend. The application is containerized using Docker and orchestrated with Docker Compose.

## Project Structure
```
root
├── backend           # FastAPI API
├── worker            # Celery tasks
├── frontend          # React + Tailwind (Vite)
├── infra             # Docker, configs
├── scripts           # Seeds, utilities
├── tests             # Unit/integration tests
├── .env.example      # Environment variable example
├── .gitignore        # Git ignore file
├── Makefile          # Development commands
├── .prettierrc       # Prettier configuration
├── .eslintrc.js      # ESLint configuration
├── pyproject.toml    # Python project configuration
├── ruff.toml         # Ruff configuration
└── .github           # GitHub workflows
```

## Getting Started



### Prerequisites
- Docker
- Docker Compose
- Python 3.11 or 3.12 (use [pyenv](https://github.com/pyenv/pyenv) for easy switching)
- Node.js 18+ (recommended)
- npm (for frontend)


### Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```


2. Create a `.env` file based on the `.env.example` file and fill in the required environment variables. Both backend and worker use this file for configuration. The most important variable for local dev is `CELERY_BROKER_URL` (set to `redis://redis:6379/0` for Docker Compose, or `redis://localhost:6379/0` for local-only testing).

3. Build and start the services:
   ```
   make up
   ```

4. Verify that the backend is running by checking the health endpoint:
   ```
   curl localhost:8000/health
   ```



### Running Tests
- To run all backend Python tests (with correct import paths):
  ```sh
  make test
  ```

- To run frontend tests (using Vitest):
  ```sh
  make frontend-test
  ```

### Development Commands
- To format the code:
  ```
  make fmt
  ```

## Python Environment & Automated Setup

This project requires Python 3.11 (recommended) or 3.12. The required version is specified in the `.python-version` file for use with [pyenv](https://github.com/pyenv/pyenv).

To set up your environment and install all Python dependencies, just run:

```sh
make setup
```

Afterwards, activate your environment with:
```sh
source activate.sh
```



## Dependency Management & Troubleshooting

All Python dependencies are installed automatically by `make setup`, which installs requirements for both backend and worker. No manual steps required.

> **Note:** The Makefile ensures `PYTHONPATH=. pytest` is used so all modules are importable during tests. Always use `make test` for backend tests.


### If you see errors about `asyncpg`, missing packages, or Redis connection:

1. **Ensure you are using Python 3.11.9 (or 3.12) with pyenv:**
   ```sh
   pyenv install 3.11.9  # if not already installed
   pyenv local 3.11.9
   ```
2. **Delete any old virtual environment:**
   ```sh
   rm -rf .venv
   ```
3. **Re-run setup and activate:**
   ```sh
   make setup
   source activate.sh
   ```


4. **For local Celery/worker tests:**
   - No manual steps are needed! Just use `make up` to start all services (backend, worker, Redis, Postgres, MinIO) via Docker Compose. The Celery worker and Redis are started automatically and are available for both development and testing.
   - To run backend tests:
     ```sh
     make test
     ```
   - To run frontend tests:
     ```sh
     make frontend-test
     ```
   > **Note:** If you encounter issues with worker tests, ensure `make up` is running and all containers are healthy. Use `docker-compose -f infra/docker-compose.yml ps` to check container status.

Import for local dev:
-  Make sure the Celery worker is running and connected to the same Redis instance as your tests. If using Docker Compose, this is automatic.
-  Stop all services by `docker-compose -f infra/docker-compose.yml down`.


This ensures all dependencies are installed with the correct Python version and your tests will work, including Celery/worker tests.

## Acceptance Criteria
- `make up` spins up all services.
- `curl localhost:8000/health` returns a 200 status.
- `make test` runs and passes a sample backend test.
- `make frontend-test` works for the frontend.

## License
