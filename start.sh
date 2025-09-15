#!/bin/bash

# PDF Processor App Startup Script

echo "🚀 Starting PDF Processor Application..."

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f "backend/env.example" ]; then
        cp backend/env.example backend/.env
        echo "📝 Created backend/.env from env.example"
        echo "   You can edit backend/.env to customize your GEMINI_API_KEY"
        echo "   You can get your API key from: https://makersuite.google.com/app/apikey"
    else
        echo "❌ backend/env.example not found. Creating basic .env file..."
        cat > backend/.env << EOF
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Google Gemini API
GEMINI_API_KEY=<insert-GEMINI_API_KEY-here>

# API Configuration
API_BASE_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO
EOF
        echo "📝 Created basic backend/.env file"
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start the application with Docker Compose
echo "🐳 Starting services with Docker Compose..."
cd docker

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in docker directory"
    exit 1
fi

# Start the services
if docker-compose up --build; then
    echo "✅ Application started!"
    echo "📖 API Documentation: http://localhost:8000/docs"
    echo "🔍 Health Check: http://localhost:8000/health"
else
    echo "❌ Failed to start application with Docker Compose"
    echo "💡 Try running 'docker-compose logs' to see error details"
    exit 1
fi
