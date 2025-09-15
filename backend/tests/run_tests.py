#!/usr/bin/env python3
"""
Test runner for PDF Processor
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests"""
    print("🚀 Running PDF Processor Tests")
    print("=" * 50)
    
    # Get the tests directory
    tests_dir = Path(__file__).parent
    backend_dir = tests_dir.parent
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests")
    print("=" * 30)
    
    tests_dir = Path(__file__).parent
    
    # Test environment
    print("1. Testing environment...")
    try:
        result = subprocess.run([
            sys.executable, "tests/test_env.py"
        ], check=True, capture_output=True, text=True)
        print("✅ Environment test passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Environment test failed: {e.stderr}")
        return False
    
    # Test quick API check
    print("2. Testing API availability...")
    try:
        result = subprocess.run([
            sys.executable, "tests/test_quick.py"
        ], check=True, capture_output=True, text=True)
        print("✅ API test passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ API test failed: {e.stderr}")
        print("   Make sure the API is running with: ./start.sh")
        return False
    
    return True

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--integration":
        success = run_integration_tests()
    else:
        success = run_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
