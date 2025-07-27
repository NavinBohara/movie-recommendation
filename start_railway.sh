#!/bin/bash

echo "Starting Movie Recommender System on Railway..."

# Check if data files exist
if [ ! -f "movies.csv" ]; then
    echo "Error: movies.csv not found!"
    exit 1
fi

if [ ! -f "ratings.csv" ]; then
    echo "Error: ratings.csv not found!"
    exit 1
fi

echo "Data files found. Starting application..."

# Start the application
exec gunicorn app_railway:app --config gunicorn.conf.py 