# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 2
timeout = 120
worker_class = "sync" 