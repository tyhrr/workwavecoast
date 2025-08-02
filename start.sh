#!/bin/bash

# Start script for Render deployment
# This script runs to start the application

echo "Starting WorkWave Coast Backend..."

# Change to backend directory
cd backend

# Use Gunicorn instead of Flask development server
exec gunicorn --config gunicorn_config.py app:app
