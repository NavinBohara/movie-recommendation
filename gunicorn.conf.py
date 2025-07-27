# Gunicorn configuration file for Railway
bind = "0.0.0.0:8000"
workers = 1
timeout = 600
worker_class = "sync"
preload_app = False
max_requests = 100
max_requests_jitter = 10
keepalive = 2
worker_connections = 1000 