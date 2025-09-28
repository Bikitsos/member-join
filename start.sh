#!/bin/bash

# Member Registration App Startup Script
# This script loads environment variables and starts the application

set -e  # Exit on any error

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment loaded"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Start the application
echo "🚀 Starting member registration app..."
uv run main.py