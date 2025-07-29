#!/bin/bash

# Build script for Render deployment
echo "Starting build process..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv /opt/render/project/src/venv
source /opt/render/project/src/venv/bin/activate

# Upgrade pip in virtual environment
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements in virtual environment
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