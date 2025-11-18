#!/bin/bash

# Initialize database tables
echo "Initializing database..."
python init_db.py

# Start the FastAPI application
echo "Starting FastAPI server..."
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}