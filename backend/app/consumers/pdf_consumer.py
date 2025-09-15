import asyncio
import json
import logging
from typing import Dict, Any
import aiohttp
import os

from ..services.redis_service import RedisService
from ..services.pdf_processor import PDFProcessor
from ..models.pdf_models import ProcessingStatus, ParserType

logger = logging.getLogger(__name__)

class PDFConsumer:
    def __init__(self, redis_service: RedisService, pdf_processor: PDFProcessor):
        self.redis_service = redis_service
        self.pdf_processor = pdf_processor
        self.running = False
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    async def consume_messages(self):
        """Main consumer loop for processing PDF messages"""
        self.running = True
        logger.info("PDF Consumer started")
        
        while self.running:
            try:
                messages = await self.redis_service.read_messages(count=1)
                
                if not messages:
                    await asyncio.sleep(1)
                    continue
                
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        await self._process_message(message_id, fields)
                        
            except Exception as e:
                logger.error(f"Consumer error: {e}")
                await asyncio.sleep(5)
    
    async def _process_message(self, message_id: str, fields: Dict[str, Any]):
        """Process a single PDF message"""
        processing_id = None
        try:
            processing_id = fields.get("processing_id")
            data_json = fields.get("data")
            
            if not processing_id or not data_json:
                await self.redis_service.acknowledge_message(message_id)
                return
            
            data = json.loads(data_json)
            filename = data.get("filename")
            content_hex = data.get("content")
            parser_str = data.get("parser", "pypdf")
            
            try:
                parser = ParserType(parser_str)
            except ValueError:
                parser = ParserType.PYPDF
            
            if not filename or not content_hex:
                await self.redis_service.acknowledge_message(message_id)
                return
            
            pdf_content = bytes.fromhex(content_hex)
            
            # Update status to processing
            await self._update_status(processing_id, {
                "status": ProcessingStatus.PROCESSING,
                "message": "Processing PDF..."
            })
            
            # Process PDF
            result = await self.pdf_processor.process_pdf(pdf_content, filename, parser)
            
            # Clean text for JSON serialization
            clean_text = result.extraction.text.encode('utf-8', errors='replace').decode('utf-8')
            clean_markdown = result.extraction.markdown.encode('utf-8', errors='replace').decode('utf-8')
            clean_summary = result.analysis.summary.encode('utf-8', errors='replace').decode('utf-8')
            clean_key_points = [point.encode('utf-8', errors='replace').decode('utf-8') for point in result.analysis.key_points]
            clean_topics = [topic.encode('utf-8', errors='replace').decode('utf-8') for topic in result.analysis.topics]
            
            # Store results in Redis
            await self._store_results_in_redis(processing_id, {
                "markdown": clean_markdown,
                "summary": clean_summary,
                "parser_used": result.parser_used,
                "filename": result.filename,
                "processing_time": result.processing_time
            })
            
            # Update status to completed
            await self._update_status(processing_id, {
                "status": ProcessingStatus.COMPLETED,
                "message": "PDF processing completed successfully",
                "parser": result.parser_used,
                "result": {
                    "extraction": {
                        "text": clean_text,
                        "markdown": clean_markdown,
                        "page_count": result.extraction.page_count,
                        "metadata": result.extraction.metadata,
                        "parser_used": result.extraction.parser_used
                    },
                    "analysis": {
                        "summary": clean_summary,
                        "key_points": clean_key_points,
                        "sentiment": result.analysis.sentiment,
                        "topics": clean_topics,
                        "confidence_score": result.analysis.confidence_score
                    },
                    "processing_time": result.processing_time,
                    "filename": result.filename,
                    "parser_used": result.parser_used
                }
            })
            
            await self.redis_service.acknowledge_message(message_id)
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            
            if processing_id:
                await self._update_status(processing_id, {
                    "status": ProcessingStatus.FAILED,
                    "message": f"Processing failed: {str(e)}"
                })
            
            await self.redis_service.acknowledge_message(message_id)
    
    async def _update_status(self, processing_id: str, status_data: Dict[str, Any]):
        """Update processing status via API call"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/update-status/{processing_id}"
                async with session.post(url, json=status_data) as response:
                    if response.status != 200:
                        logger.error(f"Status update failed: {response.status}")
        except Exception as e:
            logger.error(f"Status update error: {e}")
    
    async def _store_results_in_redis(self, processing_id: str, data: Dict[str, Any]):
        """Store processing results in Redis"""
        try:
            await self.redis_service.store_result(processing_id, data, expire_seconds=86400)
        except Exception as e:
            logger.error(f"Redis storage failed: {e}")
    
    def stop(self):
        """Stop the consumer"""
        self.running = False
        logger.info("PDF Consumer stopped")
