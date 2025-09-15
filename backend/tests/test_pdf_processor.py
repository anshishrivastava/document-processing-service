"""
Unit tests for PDF Processor
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.pdf_processor import PDFProcessor
from app.models.pdf_models import PDFTextExtraction, GeminiAnalysis, ParserType

class TestPDFProcessor:
    """Test cases for PDFProcessor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = PDFProcessor()
        self.sample_pdf_path = backend_dir.parent / "sample.pdf"
    
    def test_initialization(self):
        """Test PDFProcessor initialization"""
        assert self.processor is not None
        # Note: gemini_model might be None if API key is not available
        assert hasattr(self.processor, 'gemini_model')
    
    def test_extract_text_with_pypdf(self):
        """Test text extraction from PDF using PyPDF"""
        if not self.sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        with open(self.sample_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        extraction = self.processor.extract_text_with_pypdf(pdf_content)
        
        assert isinstance(extraction, PDFTextExtraction)
        assert extraction.page_count > 0
        assert len(extraction.text) > 0
        assert len(extraction.markdown) > 0
        assert isinstance(extraction.metadata, dict)
        assert extraction.parser_used == ParserType.PYPDF
        assert "Sample PDF Document" in extraction.text
    
    @pytest.mark.asyncio
    async def test_summarize_with_gemini_success(self):
        """Test successful Gemini summarization"""
        # Mock the gemini_model
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''
        {
            "summary": "Test summary",
            "key_points": ["point1", "point2"],
            "sentiment": "positive",
            "topics": ["topic1", "topic2"],
            "confidence_score": 0.9
        }
        '''
        mock_model.generate_content.return_value = mock_response
        self.processor.gemini_model = mock_model
        
        result = await self.processor.summarize_with_gemini("Test text", "# Test markdown")
        
        assert result is not None
        assert result.summary == "Test summary"
        assert result.key_points == ["point1", "point2"]
        assert result.sentiment == "positive"
        assert result.topics == ["topic1", "topic2"]
        assert result.confidence_score == 0.9
    
    @pytest.mark.asyncio
    async def test_summarize_with_gemini_no_model(self):
        """Test Gemini summarization when model is not available"""
        self.processor.gemini_model = None
        
        result = await self.processor.summarize_with_gemini("Test text", "# Test markdown")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_summarize_with_gemini_error(self):
        """Test Gemini summarization error handling"""
        # Mock the gemini_model to raise an exception
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        self.processor.gemini_model = mock_model
        
        result = await self.processor.summarize_with_gemini("Test text", "# Test markdown")
        
        assert result is not None
        assert "Summarization failed" in result.summary
        assert result.confidence_score == 0.3
    
    @pytest.mark.asyncio
    async def test_process_pdf(self):
        """Test complete PDF processing"""
        if not self.sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        with open(self.sample_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Mock the summarize_with_gemini method
        with patch.object(self.processor, 'summarize_with_gemini') as mock_summarize:
            mock_analysis = GeminiAnalysis(
                summary="Test summary",
                key_points=["point1", "point2"],
                sentiment="positive",
                topics=["topic1"],
                confidence_score=0.8
            )
            mock_summarize.return_value = mock_analysis
            
            result = await self.processor.process_pdf(pdf_content, "test.pdf", ParserType.PYPDF)
            
            assert result is not None
            assert result.filename == "test.pdf"
            assert result.parser_used == ParserType.PYPDF
            assert result.processing_time > 0
            assert result.extraction is not None
            assert result.analysis is not None
            assert result.extraction.parser_used == ParserType.PYPDF
