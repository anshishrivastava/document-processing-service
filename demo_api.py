#!/usr/bin/env python3
"""
PDF Processor API Demo Script

Demonstrates the enhanced PDF processor with multiple parsers:
- PyPDF
- Google Gemini Flash
- Mistral (placeholder)

Usage: python demo_api.py [pdf_file_path]
"""

import requests
import time
import json
import sys
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test API health"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy:", response.json())
            return True
        else:
            print("❌ API health check failed:", response.status_code)
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def upload_pdf(pdf_path, parser="pypdf"):
    """Upload PDF with specified parser"""
    print(f"\n📤 Uploading PDF with {parser} parser: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            data = {'parser': parser}
            
            response = requests.post(
                f"{API_BASE_URL}/upload-pdf",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Processing ID: {result['processing_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Parser: {result['parser']}")
            print(f"   Message: {result['message']}")
            return result['processing_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def check_status(processing_id):
    """Check processing status"""
    print(f"\n⏳ Checking status for: {processing_id}")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{API_BASE_URL}/status/{processing_id}")
            
            if response.status_code == 200:
                result = response.json()
                status = result['status']
                message = result['message']
                parser = result.get('parser', 'unknown')
                
                print(f"   Status: {status} - {message} (Parser: {parser})")
                
                if status == "completed":
                    print("✅ Processing completed!")
                    return result
                elif status == "failed":
                    print("❌ Processing failed!")
                    return result
                else:
                    time.sleep(2)
                    attempt += 1
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return None
    
    print("⏰ Timeout waiting for processing to complete")
    return None

def get_results(processing_id):
    """Get markdown results from Redis"""
    print(f"\n📄 Getting results for: {processing_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/results/{processing_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Results retrieved successfully!")
            print(f"   Parser used: {result['parser_used']}")
            print(f"   Filename: {result['filename']}")
            print(f"   Processing time: {result['processing_time']:.2f}s")
            print(f"\n📝 Summary:")
            print(f"   {result['summary']}")
            print(f"\n📋 Markdown (first 500 chars):")
            print(f"   {result['markdown'][:500]}...")
            return result
        else:
            print(f"❌ Failed to get results: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Results retrieval error: {e}")
        return None

def demo_parser(pdf_path, parser):
    """Demo a specific parser"""
    print(f"\n{'='*60}")
    print(f"🚀 DEMO: {parser.upper()} PARSER")
    print(f"{'='*60}")
    
    # Upload PDF
    processing_id = upload_pdf(pdf_path, parser)
    if not processing_id:
        return False
    
    # Check status until completion
    status_result = check_status(processing_id)
    if not status_result:
        return False
    
    # Get markdown results
    results = get_results(processing_id)
    if not results:
        return False
    
    # Display detailed results
    if status_result.get('result'):
        result = status_result['result']
        extraction = result.get('extraction', {})
        analysis = result.get('analysis', {})
        
        print(f"\n📊 Detailed Results:")
        print(f"   📄 Pages: {extraction.get('page_count', 'N/A')}")
        print(f"   📝 Text length: {len(extraction.get('text', ''))}")
        print(f"   📋 Markdown length: {len(extraction.get('markdown', ''))}")
        print(f"   🎯 Key Points: {', '.join(analysis.get('key_points', [])[:3])}...")
        print(f"   😊 Sentiment: {analysis.get('sentiment', 'N/A')}")
        print(f"   🏷️  Topics: {', '.join(analysis.get('topics', []))}")
        print(f"   🎯 Confidence: {analysis.get('confidence_score', 'N/A')}")
    
    return True

def main():
    """Main demo function"""
    print("🚀 PDF Processor API Demo")
    print("=" * 50)
    
    # Check if PDF path is provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "sample.pdf"
    
    # Check if PDF file exists
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        print("Usage: python demo_api.py [pdf_file_path]")
        return
    
    print(f"📄 Using PDF: {pdf_path}")
    
    # Test API health
    if not test_health():
        print("❌ API is not available. Please start the API first with: ./start.sh")
        return
    
    # Demo different parsers
    parsers = ["pypdf", "gemini_flash", "mistral"]
    
    for parser in parsers:
        success = demo_parser(pdf_path, parser)
        if not success:
            print(f"❌ Demo failed for {parser} parser")
        
        # Wait between demos
        if parser != parsers[-1]:
            print(f"\n⏳ Waiting 3 seconds before next demo...")
            time.sleep(3)
    
    print(f"\n🎉 Demo completed!")
    print(f"\n💡 You can also test manually with curl:")
    print(f"   # Upload with PyPDF:")
    print(f"   curl -X POST '{API_BASE_URL}/upload-pdf' -F 'file=@{pdf_path}' -F 'parser=pypdf'")
    print(f"   ")
    print(f"   # Upload with Gemini Flash:")
    print(f"   curl -X POST '{API_BASE_URL}/upload-pdf' -F 'file=@{pdf_path}' -F 'parser=gemini_flash'")
    print(f"   ")
    print(f"   # Check status:")
    print(f"   curl '{API_BASE_URL}/status/{{processing_id}}'")
    print(f"   ")
    print(f"   # Get markdown results:")
    print(f"   curl '{API_BASE_URL}/results/{{processing_id}}'")

if __name__ == "__main__":
    main()