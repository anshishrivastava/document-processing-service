#!/usr/bin/env python3
"""
Test environment variable loading
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

print("Testing environment variable loading...")

# Load .env file from backend directory
load_dotenv(backend_dir / '.env')

# Check if GEMINI_API_KEY is loaded
api_key = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY value: {api_key}")

if api_key:
    print("✅ GEMINI_API_KEY is loaded successfully")
else:
    print("❌ GEMINI_API_KEY is not loaded")
    print("Available environment variables:")
    for key, value in os.environ.items():
        if 'GEMINI' in key or 'API' in key:
            print(f"  {key}: {value}")
