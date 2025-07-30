#!/usr/bin/env python3
"""
Document Analysis Framework - Core Analyzer
Follows the same pattern as xml-analysis-framework
"""

import os
import mimetypes
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DocumentTypeInfo:
    """Information about detected document type"""
    type_name: str
    confidence: float
    category: str
    version: Optional[str] = None
    subtype: Optional[str] = None
    encoding: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    format: Optional[str] = None

@dataclass 
class SpecializedAnalysis:
    """Specialized analysis results for AI/ML processing"""
    document_type: str
    category: str
    key_findings: Dict[str, Any]
    ai_use_cases: List[str]
    quality_metrics: Optional[Dict[str, float]] = None
    structured_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentHandler(ABC):
    """Abstract base class for document handlers"""
    
    @abstractmethod
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """
        Determine if this handler can process the document
        Returns: (can_handle, confidence_score)
        """
        pass
    
    @abstractmethod
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect specific document type information"""
        pass
    
    @abstractmethod
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform specialized analysis of the document"""
        pass
    
    @abstractmethod
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract key structured data from document"""
        pass

class GenericDocumentHandler(DocumentHandler):
    """Fallback handler for unknown document types"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        return True, 0.1  # Always can handle as fallback
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        file_ext = Path(file_path).suffix.lower()
        return DocumentTypeInfo(
            type_name=f"Generic Document ({file_ext})",
            confidence=0.1,
            category="generic",
            subtype=mime_type
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        file_size = len(content)
        file_ext = Path(file_path).suffix.lower()
        
        return SpecializedAnalysis(
            document_type=f"Generic Document ({file_ext})",
            category="generic",
            key_findings={
                "file_size": file_size,
                "file_extension": file_ext,
                "basic_info": "Generic document analysis"
            },
            ai_use_cases=[
                "Content classification",
                "Basic text extraction",
                "File type detection"
            ],
            quality_metrics={"basic_readiness": 0.5},
            structured_data={"file_info": {"size": file_size, "type": file_ext}}
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        return {
            "file_size": len(content),
            "file_extension": Path(file_path).suffix.lower(),
            "mime_type": mimetypes.guess_type(file_path)[0]
        }

class DocumentAnalyzer:
    """Main document analysis engine"""
    
    def __init__(self, max_file_size_mb: Optional[float] = None):
        self.max_file_size_mb = max_file_size_mb
        self.handlers = []
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """Initialize all available handlers"""
        # Import handlers from handlers module
        try:
            from handlers import ALL_HANDLERS
            self.handlers = [handler_class() for handler_class in ALL_HANDLERS]
        except ImportError:
            logger.warning("No specialized handlers found, using generic handler only")
            self.handlers = []
        
        # Always add generic handler as fallback
        self.handlers.append(GenericDocumentHandler())
    
    def _validate_file_size(self, file_path: str) -> bool:
        """Check if file size is within limits"""
        if self.max_file_size_mb is None:
            return True
        
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return file_size_mb <= self.max_file_size_mb
        except OSError:
            return False
    
    def _read_file_content(self, file_path: str) -> bytes:
        """Safely read file content"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    def _detect_mime_type(self, file_path: str, content: bytes) -> str:
        """Detect MIME type of document"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        
        # Try to detect from content
        if content.startswith(b'%PDF'):
            return 'application/pdf'
        elif content.startswith(b'PK'):
            return 'application/zip'  # Could be DOCX, XLSX, etc.
        elif content.startswith(b'\x7fELF'):
            return 'application/x-executable'
        else:
            return 'application/octet-stream'
    
    def _find_best_handler(self, file_path: str, mime_type: str, content: bytes) -> DocumentHandler:
        """Find the handler with highest confidence"""
        best_handler = None
        best_confidence = 0.0
        
        for handler in self.handlers:
            try:
                can_handle, confidence = handler.can_handle(file_path, mime_type, content)
                if can_handle and confidence > best_confidence:
                    best_handler = handler
                    best_confidence = confidence
            except Exception as e:
                logger.warning(f"Handler {handler.__class__.__name__} failed: {e}")
        
        return best_handler or self.handlers[-1]  # Fallback to generic
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a document and return comprehensive results
        """
        try:
            # Validate file exists and size
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not self._validate_file_size(file_path):
                raise ValueError(f"File too large: {file_path}")
            
            # Read file content
            content = self._read_file_content(file_path)
            mime_type = self._detect_mime_type(file_path, content)
            
            # Find best handler
            handler = self._find_best_handler(file_path, mime_type, content)
            
            # Perform analysis
            document_type = handler.detect_type(file_path, mime_type, content)
            analysis = handler.analyze(file_path, content)
            
            return {
                "file_path": file_path,
                "document_type": document_type,
                "handler_used": handler.__class__.__name__,
                "confidence": document_type.confidence,
                "analysis": analysis,
                "mime_type": mime_type,
                "file_size": len(content),
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document {file_path}: {e}")
            return {
                "file_path": file_path,
                "error": str(e),
                "processing_time": datetime.now().isoformat()
            }
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported document types"""
        types = []
        for handler in self.handlers:
            if hasattr(handler, 'supported_types'):
                types.extend(handler.supported_types)
        return sorted(set(types))
    
    def get_handler_info(self) -> Dict[str, Any]:
        """Get information about loaded handlers"""
        return {
            "total_handlers": len(self.handlers),
            "handlers": [
                {
                    "name": handler.__class__.__name__,
                    "type": getattr(handler, 'handler_type', 'unknown')
                }
                for handler in self.handlers
            ]
        }