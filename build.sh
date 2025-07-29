#!/bin/bash

# Build script for Render deployment
echo "Starting build process..."

# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Verify gunicorn installation
echo "Verifying gunicorn installation..."
which gunicorn
gunicorn --version

# List installed packages
echo "Installed packages:"
pip list | grep gunicorn

echo "Build completed successfully!"