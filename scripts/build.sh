#!/bin/bash

# Build script for Render deployment
# This script runs during the build phase

echo "Starting build process..."

# Install Python dependencies
pip install -r backend/requirements.txt

echo "Build completed successfully!"
