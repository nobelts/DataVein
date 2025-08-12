#!/bin/bash
# DataVein Environment Activation Script

if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "DataVein Python environment activated"
    echo "Project root: $(pwd)"
    echo "Python: $(python --version)"
    echo "Pip packages: $(pip list | wc -l) installed"
    echo ""
    echo "Quick commands:"
    echo "  make up      - Start all services"
    echo "  make test    - Run tests"
    echo "  make health  - Check API health"
    echo "  make down    - Stop services"
else
    echo "Virtual environment not found."
    echo "Run 'make setup' first to create the environment."
    exit 1
fi
