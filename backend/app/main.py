from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis
import asyncio
import json
import uuid
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from .services.pdf_processor import PDFProcessor
from .services.redis_service import RedisService
from .models.pdf_models import PDFProcessingRequest, PDFProcessingResponse, ProcessingStatus, ParserType
from .consumers.pdf_consumer import PDFConsumer

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PDF Processor API",
    description="Async PDF processing with multiple parsers and Gemini 2.0 Flash summarization",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
redis_service = RedisService()
pdf_processor = PDFProcessor()
pdf_consumer = PDFConsumer(redis_service, pdf_processor)

# Global variable to store processing status
processing_status: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize services"""
    await redis_service.initialize()
    asyncio.create_task(pdf_consumer.consume_messages())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup"""
    await redis_service.close()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "PDF Processor API v2.0"}

@app.post("/upload-pdf", response_model=PDFProcessingResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    parser: ParserType = Form(ParserType.PYPDF)
):
    """Upload a PDF file for processing with specified parser"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Generate unique processing ID
    processing_id = str(uuid.uuid4())
    
    # Read file content
    content = await file.read()
    
    # Store processing status
    processing_status[processing_id] = {
        "status": ProcessingStatus.PENDING,
        "filename": file.filename,
        "parser": parser,
        "message": f"PDF uploaded and queued for processing with {parser} parser"
    }
    
    # Add to Redis Stream for processing
    await redis_service.add_to_stream(processing_id, {
        "filename": file.filename,
        "content": content.hex(),  # Convert bytes to hex string for JSON serialization
        "processing_id": processing_id,
        "parser": parser
    })
    
    return PDFProcessingResponse(
        processing_id=processing_id,
        status=ProcessingStatus.PENDING,
        message=f"PDF uploaded and queued for processing with {parser} parser",
        parser=parser
    )

@app.get("/status/{processing_id}", response_model=PDFProcessingResponse)
async def get_processing_status(processing_id: str):
    """Get the processing status of a PDF"""
    if processing_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    status_data = processing_status[processing_id]
    return PDFProcessingResponse(
        processing_id=processing_id,
        status=status_data["status"],
        message=status_data.get("message", ""),
        parser=status_data.get("parser"),
        result=status_data.get("result")
    )

@app.get("/health")
async def health_check():
    """Health check for Redis connection"""
    try:
        await redis_service.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "disconnected", "error": str(e)}

# Update processing status endpoint (used by consumer)
@app.get("/results/{processing_id}")
async def get_processing_results(processing_id: str):
    """Get processing results including markdown from Redis"""
    try:
        # Get results from Redis
        results = await redis_service.get_result(processing_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Results not found or expired")
        
        return {
            "processing_id": processing_id,
            "markdown": results.get("markdown", ""),
            "summary": results.get("summary", ""),
            "parser_used": results.get("parser_used", "unknown"),
            "filename": results.get("filename", ""),
            "processing_time": results.get("processing_time", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

@app.post("/update-status/{processing_id}")
async def update_processing_status(
    processing_id: str,
    status_data: Dict[str, Any]
):
    """Update processing status (internal endpoint)"""
    if processing_id in processing_status:
        processing_status[processing_id].update(status_data)
        return {"message": "Status updated"}
    else:
        raise HTTPException(status_code=404, detail="Processing ID not found")
