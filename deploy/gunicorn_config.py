#!/usr/bin/env python3
"""
Gunicorn configuration for Render deployment
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes - Reduced for memory optimization on Render
workers = 1  # Single worker to minimize memory usage
worker_class = "aiohttp.GunicornWebWorker"
worker_connections = 500  # Reduced connections per worker
timeout = 60  # Increased timeout for complex operations
keepalive = 2

# Restart workers more frequently to prevent memory leaks
max_requests = 500  # More frequent restarts
max_requests_jitter = 25

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "tradeai_bot"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None