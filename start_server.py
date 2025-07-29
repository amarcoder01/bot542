#!/usr/bin/env python3
"""
Startup script for Render deployment
This script properly handles the PORT environment variable and starts the aiohttp server
"""

import os
import sys
from aiohttp import web
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import create_app

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    
    logger.info(f"Starting server on {host}:{port}")
    
    # Create the application
    app = create_app()
    
    # Start the web server
    web.run_app(
        app,
        host=host,
        port=port,
        access_log=logger
    )

if __name__ == '__main__':
    main()