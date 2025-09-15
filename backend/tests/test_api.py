#!/usr/bin/env python3
"""
Test script for PDF Processor API
"""

import requests
import time
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
            return True
        else:
            print("❌ Health check failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Health check error:", e)
        return False

def test_pdf_upload(pdf_path):
    """Test PDF upload"""
    print(f"📄 Testing PDF upload: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return None
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload-pdf", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PDF uploaded successfully:")
            print(f"   Processing ID: {data['processing_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            return data['processing_id']
        else:
            print("❌ PDF upload failed:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ PDF upload error:", e)
        return None

def test_status_check(processing_id):
    """Test status checking"""
    print(f"⏳ Checking status for processing ID: {processing_id}")
    
    max_attempts = 30  # 30 seconds timeout
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE_URL}/status/{processing_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                print(f"   Status: {status} - {data['message']}")
                
                if status == 'completed':
                    print("✅ Processing completed!")
                    print("\n📊 Results:")
                    result = data.get('result', {})
                    
                    if 'extraction' in result:
                        extraction = result['extraction']
                        print(f"   📄 Pages: {extraction['page_count']}")
                        print(f"   📝 Text preview: {extraction['text'][:200]}...")
                    
                    if 'analysis' in result:
                        analysis = result['analysis']
                        print(f"   🤖 Summary: {analysis['summary']}")
                        print(f"   🎯 Key Points: {', '.join(analysis['key_points'][:3])}")
                        print(f"   😊 Sentiment: {analysis['sentiment']}")
                        print(f"   📚 Topics: {', '.join(analysis['topics'])}")
                        print(f"   🎯 Confidence: {analysis['confidence_score']}")
                    
                    print(f"   ⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
                    return True
                elif status == 'failed':
                    print("❌ Processing failed!")
                    return False
                else:
                    time.sleep(1)
                    attempt += 1
            else:
                print("❌ Status check failed:", response.status_code)
                return False
        except Exception as e:
            print("❌ Status check error:", e)
            return False
    
    print("⏰ Timeout waiting for processing to complete")
    return False

def main():
    """Main test function"""
    print("🚀 PDF Processor API Test")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Make sure the API is running.")
        sys.exit(1)
    
    # Check if PDF file provided
    if len(sys.argv) < 2:
        print("\n📝 Usage: python test_api.py <path_to_pdf_file>")
        print("   Example: python test_api.py ../../sample.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Test PDF upload
    processing_id = test_pdf_upload(pdf_path)
    if not processing_id:
        print("\n❌ PDF upload failed.")
        sys.exit(1)
    
    # Test status checking
    print("\n" + "=" * 50)
    success = test_status_check(processing_id)
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()