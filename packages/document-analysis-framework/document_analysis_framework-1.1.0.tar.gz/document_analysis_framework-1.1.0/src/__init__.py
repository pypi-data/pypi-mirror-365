"""
Document Analysis Framework

General-purpose document analysis framework for text, configuration, and code files.
Provides AI-ready analysis and chunking capabilities for documents not handled by
specialized frameworks.
"""

__version__ = "1.0.0"
__author__ = "AI Building Blocks"

# Core imports
from .core.analyzer import DocumentAnalyzer, DocumentTypeInfo, SpecializedAnalysis
from .core.chunking import ChunkingOrchestrator, DocumentChunk

# Convenience functions
def analyze(file_path: str, **kwargs):
    """
    Analyze a document and return comprehensive results.
    
    Args:
        file_path: Path to the document file
        **kwargs: Additional analysis options
        
    Returns:
        dict: Analysis results including document type, AI opportunities, and metadata
        
    Example:
        result = analyze("config.yaml")
        print(f"Type: {result['document_type'].type_name}")
        print(f"AI opportunities: {result['analysis'].ai_use_cases}")
    """
    analyzer = DocumentAnalyzer()
    return analyzer.analyze_document(file_path, **kwargs)

def get_supported_types():
    """
    Get list of supported document types.
    
    Returns:
        list: Supported file types and categories
    """
    analyzer = DocumentAnalyzer()
    return analyzer.get_supported_types()

# Export main classes and functions
__all__ = [
    # Simple API
    "analyze",
    "get_supported_types",
    
    # Core classes
    "DocumentAnalyzer",
    "ChunkingOrchestrator",
    
    # Data structures
    "DocumentTypeInfo",
    "SpecializedAnalysis",
    "DocumentChunk",
    
    # Version info
    "__version__",
    "__author__",
]

# Add unified interface support
from .unified_interface import UnifiedAnalysisResult

def analyze_unified(file_path: str, **kwargs):
    """Analyze file and return unified result format.
    
    This provides a consistent interface across all analysis frameworks.
    
    Args:
        file_path: Path to the file to analyze
        **kwargs: Framework-specific parameters
        
    Returns:
        UnifiedAnalysisResult with consistent interface
        
    Example:
        result = analyze_unified("config.yaml")
        doc_type = result['document_type']  # Dict access
        doc_type = result.document_type     # Attribute access
        as_dict = result.to_dict()          # Full conversion
    """
    analyzer = DocumentAnalyzer()
    return analyzer.analyze_unified(file_path, **kwargs)

# Update __all__ to include unified interface
__all__.extend([
    'UnifiedAnalysisResult',
    'analyze_unified'
])