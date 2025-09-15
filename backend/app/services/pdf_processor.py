import io
import time
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv
import base64

from ..models.pdf_models import PDFTextExtraction, GeminiAnalysis, ProcessingResult, ProcessingStatus, ParserType

load_dotenv()

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.gemini_model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Google Gemini API"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found")
                return
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini 2.0 Flash initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.gemini_model = None
    
    def extract_text_with_pypdf(self, pdf_content: bytes) -> PDFTextExtraction:
        """Extract text from PDF using PyPDF"""
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_content))
            
            # Extract text from all pages
            text_content = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                page_text = page_text.encode('utf-8', errors='replace').decode('utf-8')
                text_content += page_text + "\n"
            
            # Extract basic metadata
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "pages": len(pdf_reader.pages)
                }
            
            markdown_content = self._text_to_markdown(text_content.strip())
            
            return PDFTextExtraction(
                text=text_content.strip(),
                markdown=markdown_content,
                page_count=len(pdf_reader.pages),
                metadata=metadata,
                parser_used=ParserType.PYPDF
            )
            
        except Exception as e:
            logger.error(f"PyPDF extraction failed: {e}")
            raise e
    
    async def extract_text_with_gemini(self, pdf_content: bytes) -> PDFTextExtraction:
        """Extract text from PDF using Google Gemini Flash"""
        if not self.gemini_model:
            raise Exception("Gemini model not available")
        
        try:
            prompt = "Extract all text from this PDF and format as clean markdown. Return only the markdown content."
            
            # Upload PDF to Gemini
            pdf_file = genai.upload_file(io.BytesIO(pdf_content), mime_type="application/pdf")
            response = self.gemini_model.generate_content([prompt, pdf_file])
            genai.delete_file(pdf_file.name)
            
            markdown_content = response.text.strip()
            plain_text = self._markdown_to_text(markdown_content)
            
            return PDFTextExtraction(
                text=plain_text,
                markdown=markdown_content,
                page_count=1,
                metadata={"extraction_method": "gemini_flash"},
                parser_used=ParserType.GEMINI_FLASH
            )
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            raise e
    
    async def extract_text_with_mistral(self, pdf_content: bytes) -> PDFTextExtraction:
        """Extract text from PDF using Mistral (placeholder - falls back to PyPDF)"""
        logger.warning("Mistral OCR not implemented, using PyPDF fallback")
        
        try:
            result = self.extract_text_with_pypdf(pdf_content)
            result.parser_used = ParserType.MISTRAL
            result.metadata["note"] = "Mistral fallback to PyPDF"
            return result
        except Exception as e:
            logger.error(f"Mistral extraction failed: {e}")
            raise e
    
    def _text_to_markdown(self, text: str) -> str:
        """Convert plain text to basic markdown format"""
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append('')
                continue
            
            # Simple heuristics for markdown conversion
            if len(line) < 100 and line.isupper():
                # Likely a header
                markdown_lines.append(f"## {line.title()}")
            elif line.endswith(':') and len(line) < 80:
                # Likely a subheader
                markdown_lines.append(f"### {line}")
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Already a list item
                markdown_lines.append(line)
            else:
                # Regular paragraph
                markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)
    
    def _markdown_to_text(self, markdown: str) -> str:
        """Convert markdown to plain text"""
        import re
        
        # Remove markdown formatting
        text = re.sub(r'^#{1,6}\s+', '', markdown, flags=re.MULTILINE)  # Headers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)  # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)  # Code
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
        
        return text.strip()
    
    async def summarize_with_gemini(self, text: str, markdown: str) -> Optional[GeminiAnalysis]:
        """Summarize text using Gemini 2.0 Flash"""
        if not self.gemini_model:
            return None
        
        try:
            prompt = f"""
Analyze this document and respond in JSON format:
{{
    "summary": "2-3 sentence summary",
    "key_points": ["point1", "point2", "point3"],
    "sentiment": "positive/negative/neutral",
    "topics": ["topic1", "topic2"],
    "confidence_score": 0.85
}}

Document: {markdown[:8000] if markdown else text[:8000]}
"""
            
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = '{"summary": "Analysis completed", "key_points": ["Text processed"], "sentiment": "neutral", "topics": ["document"], "confidence_score": 0.7}'
            
            import json
            data = json.loads(json_text)
            
            return GeminiAnalysis(
                summary=data.get("summary", "Analysis completed"),
                key_points=data.get("key_points", []),
                sentiment=data.get("sentiment"),
                topics=data.get("topics", []),
                confidence_score=data.get("confidence_score", 0.5)
            )
            
        except Exception as e:
            logger.error(f"Gemini summarization failed: {e}")
            return GeminiAnalysis(
                summary="Summarization failed, text extracted successfully",
                key_points=["Text extraction completed"],
                sentiment="neutral",
                topics=["document processing"],
                confidence_score=0.3
            )
    
    async def process_pdf(self, pdf_content: bytes, filename: str, parser: ParserType = ParserType.PYPDF) -> ProcessingResult:
        """Process PDF with specified parser and summarize with Gemini"""
        try:
            start_time = time.time()
            
            # Extract text using specified parser
            if parser == ParserType.PYPDF:
                extraction = self.extract_text_with_pypdf(pdf_content)
            elif parser == ParserType.GEMINI_FLASH:
                extraction = await self.extract_text_with_gemini(pdf_content)
            elif parser == ParserType.MISTRAL:
                extraction = await self.extract_text_with_mistral(pdf_content)
            else:
                raise ValueError(f"Unsupported parser: {parser}")
            
            # Summarize with Gemini
            analysis = await self.summarize_with_gemini(extraction.text, extraction.markdown)
            
            return ProcessingResult(
                extraction=extraction,
                analysis=analysis,
                processing_time=time.time() - start_time,
                filename=filename,
                parser_used=parser
            )
            
        except Exception as e:
            logger.error(f"PDF processing failed for {filename}: {e}")
            raise e
