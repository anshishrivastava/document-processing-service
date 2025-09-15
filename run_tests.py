#!/usr/bin/env python3
"""
Test runner for PDF Processor - can be run from root directory
"""

import sys
import os
import subprocess
from pathlib import Path

def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running Unit Tests")
    print("=" * 30)
    
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(backend_dir / "tests" / "test_pdf_processor.py"),
            "-v", 
            "--tb=short",
            "--color=yes"
        ], cwd=backend_dir, check=True)
        print("✅ Unit tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Unit tests failed with exit code {e.returncode}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests")
    print("=" * 30)
    
    backend_dir = Path(__file__).parent / "backend"
    
    # Test environment
    print("1. Testing environment...")
    try:
        result = subprocess.run([
            sys.executable, "tests/test_env.py"
        ], cwd=backend_dir, check=True, capture_output=True, text=True)
        print("✅ Environment test passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Environment test failed: {e.stderr}")
        return False
    
    # Test quick API check
    print("2. Testing API availability...")
    try:
        result = subprocess.run([
            sys.executable, "tests/test_quick.py"
        ], cwd=backend_dir, check=True, capture_output=True, text=True)
        print("✅ API test passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ API test failed: {e.stderr}")
        print("   Make sure the API is running with: ./start.sh")
        return False
    
    return True

def run_api_tests():
    """Run API tests with sample PDF"""
    print("\n📡 Running API Tests")
    print("=" * 30)
    
    backend_dir = Path(__file__).parent / "backend"
    sample_pdf = Path(__file__).parent / "sample.pdf"
    
    if not sample_pdf.exists():
        print("❌ Sample PDF not found. Please ensure sample.pdf exists in the root directory.")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "tests/test_api.py", str(sample_pdf)
        ], cwd=backend_dir, check=True)
        print("✅ API tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ API tests failed with exit code {e.returncode}")
        return False

def main():
    """Main test runner"""
    print("🚀 PDF Processor Test Suite")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    success = True
    
    if test_type in ["all", "unit"]:
        success &= run_unit_tests()
    
    if test_type in ["all", "integration"]:
        success &= run_integration_tests()
    
    if test_type in ["all", "api"]:
        success &= run_api_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
