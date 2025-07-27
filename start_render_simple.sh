#!/bin/bash

echo "🚀 Starting Movie Recommender System on Render..."

# Print environment info
echo "Port: $PORT"
echo "Environment: $RENDER"

# Start the application
echo "Starting gunicorn..."
exec gunicorn app_render:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 