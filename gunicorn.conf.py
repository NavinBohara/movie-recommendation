# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 1
timeout = 300
worker_class = "sync"
preload_app = True
max_requests = 1000
max_requests_jitter = 100 