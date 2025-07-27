#!/bin/bash

echo "Starting Movie Recommender System on Render..."

# Check if data files exist
if [ ! -f "movies.csv" ]; then
    echo "Warning: movies.csv not found!"
fi

if [ ! -f "ratings.csv" ]; then
    echo "Warning: ratings.csv not found!"
fi

echo "Starting application with gunicorn..."

# Start the application
exec gunicorn app_railway_simple:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 