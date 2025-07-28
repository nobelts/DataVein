# Makefile

.PHONY: up test fmt install-deps

up:
	docker-compose -f infra/docker-compose.yml up -d

test:
	PYTHONPATH=. pytest

fmt:
	black backend/ worker/ scripts/
	eslint frontend/src/**/*.ts* frontend/public/**/*.html

health:
	curl localhost:8000/health

frontend-test:
	npm test --prefix frontend




install-deps:
	python3 -m venv .venv || true
	. .venv/bin/activate; pip install --upgrade pip; pip install -r backend/requirements.txt -r worker/requirements.txt
	cd frontend && npm install && npm install --save-dev @vitejs/plugin-react vitest
	@echo "Activate your virtual environment with: source .venv/bin/activate"




setup:
	@command -v pyenv >/dev/null 2>&1 || { echo "pyenv not found. Please install pyenv first: https://github.com/pyenv/pyenv"; exit 1; }
	pyenv install -s 3.11.9
	pyenv local 3.11.9
	python3.11 -m venv .venv
	. .venv/bin/activate; pip install --upgrade pip; pip install -r backend/requirements.txt -r worker/requirements.txt
	cd frontend && npm install && npm install --save-dev @vitejs/plugin-react vitest
	@echo "Setup complete! Activate your environment with: source .venv/bin/activate"

# NOTE: Use Python 3.11 or 3.12 for this project. asyncpg and other dependencies do not support Python 3.13+ yet.
# To create a compatible virtual environment:
# python3.11 -m venv .venv
# source .venv/bin/activate
# make install-deps

all: up test fmt frontend-test