#!/bin/bash

echo "🔧 Setting up Gemini API for PDF Processor"
echo "=========================================="
echo ""

echo "📋 To get a valid Gemini API key:"
echo "1. Go to: https://makersuite.google.com/app/apikey"
echo "2. Sign in with your Google account"
echo "3. Click 'Create API Key'"
echo "4. Copy the generated API key"
echo ""

read -p "Enter your Gemini API key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

echo ""
echo "🧪 Testing the API key..."

# Test the API key
python3 -c "
import google.generativeai as genai
try:
    genai.configure(api_key='$api_key')
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content('Hello, respond with API working')
    print('✅ API key is valid!')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'❌ API key test failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🔧 Setting up environment..."
    
    # Create .env file
    cat > .env << EOF
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Google Gemini API
GEMINI_API_KEY=$api_key

# API Configuration
API_BASE_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO
EOF

    echo "✅ Created .env file with your API key"
    echo ""
    echo "🚀 Now you can run:"
    echo "   docker-compose -f docker/docker-compose.yml up --build"
    echo ""
    echo "💡 The API key will be automatically loaded from the .env file"
else
    echo "❌ API key test failed. Please check your key and try again."
    exit 1
fi

