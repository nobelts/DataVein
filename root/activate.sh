#!/bin/sh
# Helper script to activate the Python virtual environment
if [ -f .venv/bin/activate ]; then
    . .venv/bin/activate
else
    echo "Virtual environment not found. Run 'make setup' first."
fi
