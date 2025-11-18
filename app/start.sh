#!/bin/bash
set -e

echo "================================"
echo "Starting SoSens API Deployment"
echo "================================"

# Add app directory to Python path
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"

# Initialize database
echo "Initializing database..."
cd app
python init_db.py || echo "Database already initialized or init failed (continuing...)"
cd ..

# Start the FastAPI application
echo "Starting FastAPI server on port ${PORT}..."
uvicorn app.app:app --host 0.0.0.0 --port ${PORT:-8000}