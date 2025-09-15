#!/usr/bin/env python3
"""
Create a sample PDF for testing the API
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_sample_pdf():
    """Create a sample PDF with some text content"""
    filename = "sample.pdf"
    
    # Create a new PDF
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Sample PDF Document")
    
    # Add content
    c.setFont("Helvetica", 12)
    content = [
        "This is a sample PDF document created for testing the PDF Processor API.",
        "",
        "Key Features:",
        "• FastAPI backend with async processing",
        "• Redis Streams for message queuing",
        "• PyPDF for text extraction",
        "• Google Gemini for AI analysis",
        "• Docker containerization",
        "",
        "The application can extract text from PDFs and analyze it using",
        "artificial intelligence to provide insights, summaries, and key points.",
        "",
        "This technology stack enables scalable, asynchronous processing",
        "of PDF documents with real-time status updates and comprehensive",
        "analysis capabilities.",
        "",
        "Thank you for testing the PDF Processor API!"
    ]
    
    y_position = height - 150
    for line in content:
        c.drawString(100, y_position, line)
        y_position -= 20
    
    # Save the PDF
    c.save()
    print(f"✅ Sample PDF created: {filename}")
    print(f"   File size: {os.path.getsize(filename)} bytes")

if __name__ == "__main__":
    try:
        create_sample_pdf()
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        create_sample_pdf()
