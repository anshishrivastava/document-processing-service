#!/bin/bash

# Redis Setup Script for PDF Processor App

echo "🔧 Setting up Redis for PDF Processor App..."

# Check if Redis is already running
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is already running"
    exit 0
fi

# Check if Docker is available
if command -v docker > /dev/null 2>&1; then
    echo "🐳 Starting Redis with Docker..."
    docker run -d --name pdf_processor_redis -p 6379:6379 redis:7-alpine
    echo "✅ Redis started with Docker"
    echo "   To stop: docker stop pdf_processor_redis"
    echo "   To remove: docker rm pdf_processor_redis"
elif command -v brew > /dev/null 2>&1; then
    echo "🍺 Installing Redis with Homebrew..."
    brew install redis
    brew services start redis
    echo "✅ Redis installed and started with Homebrew"
else
    echo "❌ Neither Docker nor Homebrew found."
    echo "   Please install Redis manually:"
    echo "   - Docker: docker run -d -p 6379:6379 redis:7-alpine"
    echo "   - Homebrew: brew install redis && brew services start redis"
    echo "   - Or download from: https://redis.io/download"
    exit 1
fi

echo "🎉 Redis setup complete!"
