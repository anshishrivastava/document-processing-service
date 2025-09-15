#!/bin/bash

# PDF Processor App - Local Development Script

echo "🚀 Starting PDF Processor Application (Local Development)..."

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp backend/env.example backend/.env
    echo "📝 Please edit backend/.env and add your GEMINI_API_KEY"
    echo "   You can get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "Press Enter after adding your API key..."
    read
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Check if Redis is running locally
echo "🔍 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running locally."
    echo "   Please install and start Redis:"
    echo "   brew install redis"
    echo "   brew services start redis"
    echo ""
    echo "   Or use Docker to run Redis:"
    echo "   docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi

echo "✅ Redis is running"

# Start the application
echo "🚀 Starting FastAPI application..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
