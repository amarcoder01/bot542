#!/bin/bash

# Start script for Render deployment
echo "Starting application..."

# Activate virtual environment
echo "Activating virtual environment..."
source /opt/render/project/src/venv/bin/activate

# Add virtual environment bin to PATH
export PATH="/opt/render/project/src/venv/bin:$PATH"

# Verify gunicorn is available
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn not found in virtual environment. Installing..."
    pip install gunicorn==21.2.0
fi

# Show gunicorn location and version
echo "Gunicorn location: $(which gunicorn)"
echo "Gunicorn version: $(gunicorn --version)"

# Start the application
echo "Starting gunicorn server..."
exec gunicorn main:create_app --config gunicorn_config.py