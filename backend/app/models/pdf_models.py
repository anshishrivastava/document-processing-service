from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ParserType(str, Enum):
    PYPDF = "pypdf"
    GEMINI_FLASH = "gemini_flash"
    MISTRAL = "mistral"

class PDFProcessingRequest(BaseModel):
    filename: str
    content: str  # Base64 encoded PDF content
    parser: ParserType = ParserType.PYPDF

class PDFProcessingResponse(BaseModel):
    processing_id: str
    status: ProcessingStatus
    message: str
    parser: Optional[ParserType] = None
    result: Optional[Dict[str, Any]] = None

class PDFTextExtraction(BaseModel):
    text: str
    markdown: str
    page_count: int
    metadata: Dict[str, Any]
    parser_used: ParserType

class GeminiAnalysis(BaseModel):
    summary: str
    key_points: List[str]
    sentiment: Optional[str] = None
    topics: List[str]
    confidence_score: Optional[float] = None

class ProcessingResult(BaseModel):
    extraction: PDFTextExtraction
    analysis: GeminiAnalysis
    processing_time: float
    filename: str
    parser_used: ParserType
