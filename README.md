# PDF Processor App

A FastAPI application with Redis Streams for async PDF processing using multiple parsers and Google Gemini 2.0 Flash AI.

## Features

- **Multiple Parsers**: Support for PyPDF, Google Gemini Flash, and Mistral (placeholder)
- **Async Processing**: Redis Streams for scalable, asynchronous PDF processing
- **Markdown Output**: Converts extracted text to markdown format
- **AI Summarization**: Uses Google Gemini 2.0 Flash for comprehensive document analysis
- **Redis Storage**: Stores results with expiration for efficient retrieval
- **Real-time Status**: Track processing status in real-time
- **RESTful API**: Clean REST API with automatic documentation

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  Redis Streams  │───▶│  PDF Consumer   │
│                 │    │                 │    │                 │
│ - Upload PDF    │    │ - Message Queue │    │ - Process PDF   │
│ - Check Status  │    │ - Stream Data   │    │ - Extract Text  │
│ - Get Results   │    │                 │    │ - AI Analysis   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Google Gemini API Key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd pdf-processor-app
   ```

2. **Configure environment**:
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env and add your GEMINI_API_KEY
   ```

3. **Start the application**:
   ```bash
   ./start.sh
   ```

### Option 2: Local Development

1. **Setup Redis**:
   ```bash
   ./setup_redis.sh
   ```

2. **Configure environment**:
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env and add your GEMINI_API_KEY
   ```

3. **Start the application**:
   ```bash
   ./run_local.sh
   ```

### Access the API
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

### Upload PDF
```http
POST /upload-pdf
Content-Type: multipart/form-data

file: <PDF file>
parser: pypdf|gemini_flash|mistral
```

**Response**:
```json
{
  "processing_id": "uuid",
  "status": "pending",
  "parser": "pypdf",
  "message": "PDF uploaded and queued for processing with pypdf parser"
}
```

### Check Processing Status
```http
GET /status/{processing_id}
```

**Response**:
```json
{
  "processing_id": "uuid",
  "status": "completed",
  "parser": "pypdf",
  "message": "PDF processing completed successfully",
  "result": {
    "extraction": {
      "text": "Extracted text...",
      "markdown": "# Document Title\n\nContent...",
      "page_count": 5,
      "metadata": {...},
      "parser_used": "pypdf"
    },
    "analysis": {
      "summary": "Document summary...",
      "key_points": ["point1", "point2"],
      "sentiment": "positive",
      "topics": ["topic1", "topic2"],
      "confidence_score": 0.85
    },
    "processing_time": 2.5,
    "filename": "document.pdf",
    "parser_used": "pypdf"
  }
}
```

### Get Markdown Results
```http
GET /results/{processing_id}
```

**Response**:
```json
{
  "processing_id": "uuid",
  "markdown": "# Document Title\n\nContent in markdown format...",
  "summary": "Document summary...",
  "parser_used": "pypdf",
  "filename": "document.pdf",
  "processing_time": 2.5
}
```

### Health Check
```http
GET /health
```

## Processing Status

- `pending`: PDF uploaded and queued
- `processing`: Currently being processed
- `completed`: Processing finished successfully
- `failed`: Processing failed with error

## Parser Options

- **pypdf**: Traditional PDF text extraction using PyPDF library
- **gemini_flash**: AI-powered PDF parsing using Google Gemini Flash (supports complex layouts)
- **mistral**: Placeholder for Mistral OCR (currently falls back to PyPDF)

## Configuration

Environment variables in `backend/.env`:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Google Gemini API (Required for AI features)
GEMINI_API_KEY=your_api_key_here

# API Configuration
API_BASE_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

## Development

### Local Development (without Docker)

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start Redis**:
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Testing

```bash
# Test with different parsers
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@sample.pdf" -F "parser=pypdf"

curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@sample.pdf" -F "parser=gemini_flash"

# Check status
curl "http://localhost:8000/status/{processing_id}"

# Get markdown results
curl "http://localhost:8000/results/{processing_id}"

# Health check
curl "http://localhost:8000/health"

# Run demo script
python demo_api.py sample.pdf
```

## Project Structure

```
pdf-processor-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/
│   │   │   └── pdf_models.py    # Pydantic models
│   │   ├── services/
│   │   │   ├── redis_service.py # Redis Streams service
│   │   │   └── pdf_processor.py # PDF processing & AI analysis
│   │   └── consumers/
│   │       └── pdf_consumer.py  # Async message consumer
│   ├── requirements.txt
│   ├── Dockerfile
│   └── env.example
├── docker/
│   └── docker-compose.yml
├── start.sh
└── README.md
```

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Redis Streams**: Message queue for async processing
- **PyPDF**: Traditional PDF text extraction
- **Google Gemini 2.0 Flash**: AI-powered PDF parsing and summarization
- **Mistral**: OCR capabilities (placeholder implementation)
- **Pydantic**: Data validation and serialization
- **Docker**: Containerization support

## Error Handling

The application includes comprehensive error handling:

- PDF parsing errors
- Redis connection issues
- Gemini API failures
- Network timeouts
- Invalid file formats

## Monitoring

- Health check endpoint for service monitoring
- Detailed logging for debugging
- Processing status tracking
- Error reporting and recovery

## Demo

Use the included demo script to test all parsers:

```bash
python demo_api.py sample.pdf
```

This will demonstrate:
- PyPDF text extraction with markdown conversion
- Gemini Flash AI-powered parsing
- Mistral OCR (fallback to PyPDF)
- Gemini 2.0 Flash summarization
- Redis storage and retrieval

## License

MIT License
