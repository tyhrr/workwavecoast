"""
Gunicorn configuration for WorkWave Coast Backend
Production-ready WSGI server configuration
"""

import os

# Server socket
BIND = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
BACKLOG = 2048

# Worker processes
WORKERS = int(os.environ.get('WEB_CONCURRENCY', 2))
WORKER_CLASS = "sync"
WORKER_CONNECTIONS = 1000
TIMEOUT = 30
KEEPALIVE = 2

# Restart workers after this many requests, to help limit memory leaks
MAX_REQUESTS = 1000
MAX_REQUESTS_JITTER = 100

# Logging
ERRORLOG = '-'
LOGLEVEL = 'info'
ACCESSLOG = '-'
ACCESS_LOG_FORMAT = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
PROC_NAME = 'workwave_coast_api'

# Server mechanics
PRELOAD_APP = True
DAEMON = False
PIDFILE = None
TMP_UPLOAD_DIR = None

# SSL (if needed in the future)
# KEYFILE = None
# CERTFILE = None

# Performance - Use /tmp for better compatibility across platforms
WORKER_TMP_DIR = os.environ.get('WORKER_TMP_DIR', '/tmp')

# Export variables with lowercase names for Gunicorn compatibility
bind = BIND
backlog = BACKLOG
workers = WORKERS
worker_class = WORKER_CLASS
worker_connections = WORKER_CONNECTIONS
timeout = TIMEOUT
keepalive = KEEPALIVE
max_requests = MAX_REQUESTS
max_requests_jitter = MAX_REQUESTS_JITTER
errorlog = ERRORLOG
loglevel = LOGLEVEL
accesslog = ACCESSLOG
access_log_format = ACCESS_LOG_FORMAT
proc_name = PROC_NAME
preload_app = PRELOAD_APP
daemon = DAEMON
pidfile = PIDFILE
tmp_upload_dir = TMP_UPLOAD_DIR
worker_tmp_dir = WORKER_TMP_DIR
