"""
File validation and security utilities for Document Analysis Framework
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FileSizeLimits:
    """Predefined file size limits for different use cases"""
    REAL_TIME = 5.0      # 5MB - for real-time processing
    INTERACTIVE = 10.0   # 10MB - for interactive analysis
    BATCH_SMALL = 25.0   # 25MB - for small batch processing
    BATCH_MEDIUM = 50.0  # 50MB - for medium batch processing
    BATCH_LARGE = 100.0  # 100MB - for large batch processing
    UNLIMITED = None     # No limit

def validate_file_path(file_path: str) -> bool:
    """
    Validate that a file path is safe and accessible
    """
    try:
        path = Path(file_path).resolve()
        
        # Check if file exists
        if not path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        # Check if it's actually a file
        if not path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            return False
        
        # Check if file is readable
        if not os.access(path, os.R_OK):
            logger.error(f"File is not readable: {file_path}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating file path {file_path}: {e}")
        return False

def check_file_size(file_path: str, max_size_mb: Optional[float] = None) -> bool:
    """
    Check if file size is within specified limits
    """
    if max_size_mb is None:
        return True
        
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            logger.warning(f"File {file_path} ({file_size_mb:.2f}MB) exceeds limit of {max_size_mb}MB")
            return False
        return True
        
    except OSError as e:
        logger.error(f"Error checking file size for {file_path}: {e}")
        return False

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive file information
    """
    try:
        path = Path(file_path)
        stat = path.stat()
        
        return {
            "file_path": str(path.resolve()),
            "file_name": path.name,
            "file_extension": path.suffix,
            "file_size_bytes": stat.st_size,
            "file_size_mb": stat.st_size / (1024 * 1024),
            "is_readable": os.access(path, os.R_OK),
            "is_writable": os.access(path, os.W_OK),
            "modified_time": stat.st_mtime,
        }
        
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {"error": str(e)}

def safe_analyze_document(file_path: str, max_size_mb: Optional[float] = None) -> Dict[str, Any]:
    """
    Safely analyze a document with comprehensive validation
    """
    # Import here to avoid circular imports
    from core.analyzer import DocumentAnalyzer
    
    # Validate file path
    if not validate_file_path(file_path):
        return {"error": "Invalid file path", "file_path": file_path}
    
    # Check file size
    if not check_file_size(file_path, max_size_mb):
        file_info = get_file_info(file_path)
        return {
            "error": f"File too large: {file_info.get('file_size_mb', 0):.2f}MB exceeds limit of {max_size_mb}MB",
            "file_path": file_path,
            "file_size_mb": file_info.get('file_size_mb', 0)
        }
    
    try:
        # Create analyzer with size limit
        analyzer = DocumentAnalyzer(max_file_size_mb=max_size_mb)
        
        # Perform analysis
        result = analyzer.analyze_document(file_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Error during safe document analysis: {e}")
        return {"error": str(e), "file_path": file_path}

def create_analyzer_with_limits(max_size_mb: float):
    """
    Create a DocumentAnalyzer with predefined size limits
    """
    from core.analyzer import DocumentAnalyzer
    return DocumentAnalyzer(max_file_size_mb=max_size_mb)

def create_chunking_orchestrator_with_limits(max_size_mb: float, max_chunk_size: int = 2000):
    """
    Create a ChunkingOrchestrator with predefined size limits
    """
    from core.chunking import ChunkingOrchestrator
    return ChunkingOrchestrator(max_file_size_mb=max_size_mb, max_chunk_size=max_chunk_size)

# Convenience functions for common use cases
def create_real_time_analyzer():
    """Create analyzer optimized for real-time processing (5MB limit)"""
    return create_analyzer_with_limits(FileSizeLimits.REAL_TIME)

def create_interactive_analyzer():
    """Create analyzer optimized for interactive use (10MB limit)"""
    return create_analyzer_with_limits(FileSizeLimits.INTERACTIVE)

def create_batch_analyzer(size: str = "medium"):
    """
    Create analyzer optimized for batch processing
    Args:
        size: "small" (25MB), "medium" (50MB), or "large" (100MB)
    """
    size_limits = {
        "small": FileSizeLimits.BATCH_SMALL,
        "medium": FileSizeLimits.BATCH_MEDIUM,
        "large": FileSizeLimits.BATCH_LARGE
    }
    limit = size_limits.get(size, FileSizeLimits.BATCH_MEDIUM)
    return create_analyzer_with_limits(limit)