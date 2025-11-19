#!/bin/bash
set -e

echo "======================================================================"
echo "SoSens Deployment Starting"
echo "======================================================================"

# Change to app directory
cd /opt/render/project/src/app || cd app

echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la

echo ""
echo "Checking Python version:"
python --version

echo ""
echo "Checking pip packages:"
pip list | grep -E "fastapi|uvicorn|sqlalchemy|bcrypt|passlib" || true

echo ""
echo "Checking model files:"
if [ -d "models" ]; then
    echo "Models directory exists:"
    ls -la models/
else
    echo "Creating models directory..."
    mkdir -p models
fi

echo ""
echo "======================================================================"
echo "Starting Uvicorn Server"
echo "======================================================================"

# Run the app
uvicorn app:app \
    --host 0.0.0.0 \
    --port ${PORT:-10000} \
    --workers 1 \
    --loop uvloop \
    --http httptools