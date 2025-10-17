#!/bin/bash

# Start script for Render deployment
# Forces the use of Gunicorn instead of Flask dev server

echo "🚀 Starting WorkWave Coast Backend on Render..."
echo "Environment: Production"
echo "Using Gunicorn WSGI server"

# Change to backend directory
cd backend

# Export environment variables for production
export FLASK_ENV=production
export DEBUG=false
export RENDER=true

# Start with Gunicorn (DO NOT use python app.py in production)
exec gunicorn --bind 0.0.0.0:$PORT --config gunicorn_config.py app:app
