#!/bin/bash

# Start script for Render deployment
echo "Starting application..."

# Add Python user bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify gunicorn is available
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn not found in PATH. Trying to install..."
    pip install gunicorn>=21.2.0
    export PATH="$HOME/.local/bin:$PATH"
fi

# Show gunicorn location and version
echo "Gunicorn location: $(which gunicorn)"
echo "Gunicorn version: $(gunicorn --version)"

# Start the application
echo "Starting gunicorn server..."
exec gunicorn main:create_app --config gunicorn_config.py