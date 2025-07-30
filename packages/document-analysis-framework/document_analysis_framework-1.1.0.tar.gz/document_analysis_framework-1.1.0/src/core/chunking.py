"""
Document Chunking Strategies for Document Analysis Framework
"""

import re
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of document content"""
    chunk_id: str
    content: str
    chunk_type: str
    metadata: Dict[str, Any]
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    token_count: Optional[int] = None

class DocumentChunkingStrategy(ABC):
    """Abstract base class for document chunking strategies"""
    
    def __init__(self, max_chunk_size: int = 2000, overlap_size: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
    
    @abstractmethod
    def chunk_document(self, file_path: str, content: str, specialized_analysis: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Chunk the document content into smaller pieces"""
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token on average
        return len(text) // 4
    
    def generate_chunk_id(self, content: str, index: int) -> str:
        """Generate a unique ID for a chunk"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"chunk_{index}_{content_hash}"

class TextChunkingStrategy(DocumentChunkingStrategy):
    """Basic text-based chunking strategy"""
    
    def chunk_document(self, file_path: str, content: str, specialized_analysis: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        chunks = []
        
        # Split into paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # Fall back to line-based splitting
            paragraphs = [line.strip() for line in content.split('\n') if line.strip()]
        
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size
            if len(current_chunk) + len(paragraph) > self.max_chunk_size and current_chunk:
                # Create chunk from current content
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                    content=current_chunk.strip(),
                    chunk_type="text",
                    metadata={"chunk_index": chunk_index, "strategy": "text"},
                    token_count=self.estimate_tokens(current_chunk)
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap if possible
                if self.overlap_size > 0:
                    overlap_text = current_chunk[-self.overlap_size:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                chunk_index += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                content=current_chunk.strip(),
                chunk_type="text",
                metadata={"chunk_index": chunk_index, "strategy": "text"},
                token_count=self.estimate_tokens(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks

class StructuredChunkingStrategy(DocumentChunkingStrategy):
    """Chunking strategy for structured documents (JSON, CSV, etc.)"""
    
    def chunk_document(self, file_path: str, content: str, specialized_analysis: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        chunks = []
        document_type = specialized_analysis.get('document_type', {}).get('type_name', '') if specialized_analysis else ''
        
        if 'JSON' in document_type:
            return self._chunk_json(content)
        elif 'CSV' in document_type:
            return self._chunk_csv(content)
        else:
            # Fall back to text chunking
            return TextChunkingStrategy(self.max_chunk_size, self.overlap_size).chunk_document(file_path, content, specialized_analysis)
    
    def _chunk_json(self, content: str) -> List[DocumentChunk]:
        """Chunk JSON content by logical structure"""
        chunks = []
        
        try:
            import json
            data = json.loads(content)
            
            if isinstance(data, dict):
                # Chunk by top-level keys
                chunk_index = 0
                for key, value in data.items():
                    chunk_content = json.dumps({key: value}, indent=2)
                    if len(chunk_content) <= self.max_chunk_size:
                        chunk = DocumentChunk(
                            chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                            content=chunk_content,
                            chunk_type="json_object",
                            metadata={"key": key, "chunk_index": chunk_index, "strategy": "structured"},
                            token_count=self.estimate_tokens(chunk_content)
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                    else:
                        # If single key-value is too large, chunk its content
                        sub_chunks = self._chunk_large_json_value(key, value, chunk_index)
                        chunks.extend(sub_chunks)
                        chunk_index += len(sub_chunks)
            
            elif isinstance(data, list):
                # Chunk by array elements
                chunk_index = 0
                current_items = []
                current_size = 0
                
                for item in data:
                    item_str = json.dumps(item, indent=2)
                    item_size = len(item_str)
                    
                    if current_size + item_size > self.max_chunk_size and current_items:
                        # Create chunk from current items
                        chunk_content = json.dumps(current_items, indent=2)
                        chunk = DocumentChunk(
                            chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                            content=chunk_content,
                            chunk_type="json_array",
                            metadata={
                                "item_count": len(current_items),
                                "chunk_index": chunk_index,
                                "strategy": "structured"
                            },
                            token_count=self.estimate_tokens(chunk_content)
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                        
                        current_items = [item]
                        current_size = item_size
                    else:
                        current_items.append(item)
                        current_size += item_size
                
                # Add final chunk
                if current_items:
                    chunk_content = json.dumps(current_items, indent=2)
                    chunk = DocumentChunk(
                        chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                        content=chunk_content,
                        chunk_type="json_array",
                        metadata={
                            "item_count": len(current_items),
                            "chunk_index": chunk_index,
                            "strategy": "structured"
                        },
                        token_count=self.estimate_tokens(chunk_content)
                    )
                    chunks.append(chunk)
            
        except json.JSONDecodeError:
            # Fall back to text chunking
            return TextChunkingStrategy(self.max_chunk_size, self.overlap_size).chunk_document("", content)
        
        return chunks
    
    def _chunk_large_json_value(self, key: str, value: Any, start_index: int) -> List[DocumentChunk]:
        """Handle large JSON values that need sub-chunking"""
        import json
        chunks = []
        
        if isinstance(value, dict):
            # Chunk dictionary by key groups
            current_dict = {}
            current_size = 0
            chunk_index = start_index
            
            for sub_key, sub_value in value.items():
                item_str = json.dumps({sub_key: sub_value})
                item_size = len(item_str)
                
                if current_size + item_size > self.max_chunk_size and current_dict:
                    chunk_content = json.dumps({key: current_dict}, indent=2)
                    chunk = DocumentChunk(
                        chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                        content=chunk_content,
                        chunk_type="json_partial",
                        metadata={
                            "parent_key": key,
                            "chunk_index": chunk_index,
                            "strategy": "structured"
                        },
                        token_count=self.estimate_tokens(chunk_content)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_dict = {sub_key: sub_value}
                    current_size = item_size
                else:
                    current_dict[sub_key] = sub_value
                    current_size += item_size
            
            if current_dict:
                chunk_content = json.dumps({key: current_dict}, indent=2)
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                    content=chunk_content,
                    chunk_type="json_partial",
                    metadata={
                        "parent_key": key,
                        "chunk_index": chunk_index,
                        "strategy": "structured"
                    },
                    token_count=self.estimate_tokens(chunk_content)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_csv(self, content: str) -> List[DocumentChunk]:
        """Chunk CSV content by rows"""
        chunks = []
        lines = content.split('\n')
        
        if not lines:
            return chunks
        
        # First line is usually headers
        header = lines[0] if lines else ""
        data_lines = lines[1:] if len(lines) > 1 else []
        
        chunk_index = 0
        current_lines = [header]  # Always include header
        current_size = len(header)
        
        for line in data_lines:
            line_size = len(line)
            
            if current_size + line_size > self.max_chunk_size and len(current_lines) > 1:  # More than just header
                chunk_content = '\n'.join(current_lines)
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                    content=chunk_content,
                    chunk_type="csv",
                    metadata={
                        "row_count": len(current_lines) - 1,  # Exclude header from count
                        "chunk_index": chunk_index,
                        "strategy": "structured"
                    },
                    token_count=self.estimate_tokens(chunk_content)
                )
                chunks.append(chunk)
                chunk_index += 1
                current_lines = [header, line]  # Start new chunk with header
                current_size = len(header) + line_size
            else:
                current_lines.append(line)
                current_size += line_size
        
        # Add final chunk
        if len(current_lines) > 1:  # More than just header
            chunk_content = '\n'.join(current_lines)
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                content=chunk_content,
                chunk_type="csv",
                metadata={
                    "row_count": len(current_lines) - 1,
                    "chunk_index": chunk_index,
                    "strategy": "structured"
                },
                token_count=self.estimate_tokens(chunk_content)
            )
            chunks.append(chunk)
        
        return chunks

class CodeChunkingStrategy(DocumentChunkingStrategy):
    """Chunking strategy for source code files"""
    
    def chunk_document(self, file_path: str, content: str, specialized_analysis: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        document_type = specialized_analysis.get('document_type', {}).get('type_name', '') if specialized_analysis else ''
        
        if 'Python' in document_type:
            return self._chunk_python(content)
        elif 'JavaScript' in document_type:
            return self._chunk_javascript(content)
        elif 'SQL' in document_type:
            return self._chunk_sql(content)
        else:
            # Fall back to text chunking
            return TextChunkingStrategy(self.max_chunk_size, self.overlap_size).chunk_document(file_path, content, specialized_analysis)
    
    def _chunk_python(self, content: str) -> List[DocumentChunk]:
        """Chunk Python code by functions and classes"""
        chunks = []
        lines = content.split('\n')
        
        current_block = []
        current_type = "module"
        current_name = "module_level"
        chunk_index = 0
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detect class or function definitions
            class_match = re.match(r'^(\s*)class\s+(\w+)', line)
            func_match = re.match(r'^(\s*)def\s+(\w+)', line)
            
            if class_match or func_match:
                # Save previous block if it has content
                if current_block and any(l.strip() for l in current_block):
                    chunk_content = '\n'.join(current_block)
                    if len(chunk_content.strip()) > 0:
                        chunk = DocumentChunk(
                            chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                            content=chunk_content,
                            chunk_type=f"python_{current_type}",
                            metadata={
                                "name": current_name,
                                "type": current_type,
                                "chunk_index": chunk_index,
                                "strategy": "code"
                            },
                            token_count=self.estimate_tokens(chunk_content)
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                
                # Start new block
                if class_match:
                    current_type = "class"
                    current_name = class_match.group(2)
                    indent_level = len(class_match.group(1))
                else:
                    current_type = "function"
                    current_name = func_match.group(2)
                    indent_level = len(func_match.group(1))
                
                current_block = [line]
            else:
                current_block.append(line)
                
                # If block gets too large, chunk it
                if len('\n'.join(current_block)) > self.max_chunk_size:
                    chunk_content = '\n'.join(current_block)
                    chunk = DocumentChunk(
                        chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                        content=chunk_content,
                        chunk_type=f"python_{current_type}",
                        metadata={
                            "name": current_name,
                            "type": current_type,
                            "chunk_index": chunk_index,
                            "strategy": "code"
                        },
                        token_count=self.estimate_tokens(chunk_content)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_block = []
                    current_type = "module"
                    current_name = "module_level"
        
        # Add final block
        if current_block and any(l.strip() for l in current_block):
            chunk_content = '\n'.join(current_block)
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id(chunk_content, chunk_index),
                content=chunk_content,
                chunk_type=f"python_{current_type}",
                metadata={
                    "name": current_name,
                    "type": current_type,
                    "chunk_index": chunk_index,
                    "strategy": "code"
                },
                token_count=self.estimate_tokens(chunk_content)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_javascript(self, content: str) -> List[DocumentChunk]:
        """Chunk JavaScript code by functions"""
        chunks = []
        
        # Simple function detection - could be enhanced
        function_pattern = r'(function\s+\w+\s*\([^)]*\)\s*{|const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*{|\w+\s*:\s*function\s*\([^)]*\)\s*{)'
        
        # Split by functions for now - this is a simplified approach
        parts = re.split(function_pattern, content)
        
        chunk_index = 0
        for i, part in enumerate(parts):
            if part.strip():
                if len(part) > self.max_chunk_size:
                    # Split large parts further
                    sub_parts = [part[i:i+self.max_chunk_size] for i in range(0, len(part), self.max_chunk_size)]
                    for sub_part in sub_parts:
                        chunk = DocumentChunk(
                            chunk_id=self.generate_chunk_id(sub_part, chunk_index),
                            content=sub_part,
                            chunk_type="javascript_code",
                            metadata={
                                "chunk_index": chunk_index,
                                "strategy": "code"
                            },
                            token_count=self.estimate_tokens(sub_part)
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                else:
                    chunk = DocumentChunk(
                        chunk_id=self.generate_chunk_id(part, chunk_index),
                        content=part,
                        chunk_type="javascript_code",
                        metadata={
                            "chunk_index": chunk_index,
                            "strategy": "code"
                        },
                        token_count=self.estimate_tokens(part)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
        
        return chunks if chunks else [DocumentChunk(
            chunk_id=self.generate_chunk_id(content, 0),
            content=content,
            chunk_type="javascript_code",
            metadata={"chunk_index": 0, "strategy": "code"},
            token_count=self.estimate_tokens(content)
        )]
    
    def _chunk_sql(self, content: str) -> List[DocumentChunk]:
        """Chunk SQL by statements"""
        chunks = []
        
        # Split by semicolons (rough SQL statement boundary)
        statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
        
        chunk_index = 0
        current_chunk = ""
        
        for statement in statements:
            if len(current_chunk) + len(statement) > self.max_chunk_size and current_chunk:
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                    content=current_chunk.strip(),
                    chunk_type="sql_statements",
                    metadata={
                        "chunk_index": chunk_index,
                        "strategy": "code"
                    },
                    token_count=self.estimate_tokens(current_chunk)
                )
                chunks.append(chunk)
                chunk_index += 1
                current_chunk = statement + ";"
            else:
                if current_chunk:
                    current_chunk += "\n" + statement + ";"
                else:
                    current_chunk = statement + ";"
        
        # Add final chunk
        if current_chunk.strip():
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id(current_chunk, chunk_index),
                content=current_chunk.strip(),
                chunk_type="sql_statements",
                metadata={
                    "chunk_index": chunk_index,
                    "strategy": "code"
                },
                token_count=self.estimate_tokens(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks

class ChunkingOrchestrator:
    """Orchestrates different chunking strategies based on document type"""
    
    def __init__(self, max_file_size_mb: Optional[float] = None, max_chunk_size: int = 2000, overlap_size: int = 200):
        self.max_file_size_mb = max_file_size_mb
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        
        self.strategies = {
            'text': TextChunkingStrategy(max_chunk_size, overlap_size),
            'structured': StructuredChunkingStrategy(max_chunk_size, overlap_size),
            'code': CodeChunkingStrategy(max_chunk_size, overlap_size),
            'auto': None  # Will be determined automatically
        }
    
    def _validate_file_size(self, file_path: str) -> bool:
        """Check if file size is within limits"""
        if self.max_file_size_mb is None:
            return True
        
        try:
            import os
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return file_size_mb <= self.max_file_size_mb
        except OSError:
            return False
    
    def _read_file_content(self, file_path: str) -> str:
        """Read file content as text"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fall back to latin-1
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    def _determine_strategy(self, specialized_analysis: Optional[Dict[str, Any]]) -> str:
        """Determine the best chunking strategy based on document analysis"""
        if not specialized_analysis:
            return 'text'
        
        doc_type = specialized_analysis.get('document_type', {})
        if isinstance(doc_type, dict):
            type_name = doc_type.get('type_name', '')
            category = doc_type.get('category', '')
        else:
            # Handle case where doc_type might be a string or object
            type_name = str(doc_type)
            category = 'unknown'
        
        # Map document types to strategies
        if any(keyword in type_name.lower() for keyword in ['json', 'csv', 'yaml', 'toml']):
            return 'structured'
        elif any(keyword in type_name.lower() for keyword in ['python', 'javascript', 'sql', 'java', 'cpp']):
            return 'code'
        elif category == 'code':
            return 'code'
        elif category in ['data', 'config']:
            return 'structured'
        else:
            return 'text'
    
    def chunk_document(self, file_path: str, specialized_analysis: Optional[Dict[str, Any]] = None, strategy: str = 'auto') -> List[DocumentChunk]:
        """
        Chunk a document using the specified or automatically determined strategy
        """
        try:
            # Validate file size
            if not self._validate_file_size(file_path):
                raise ValueError(f"File too large: {file_path}")
            
            # Read file content
            content = self._read_file_content(file_path)
            
            # Determine strategy
            if strategy == 'auto':
                strategy = self._determine_strategy(specialized_analysis)
            
            # Get chunking strategy
            chunking_strategy = self.strategies.get(strategy)
            if not chunking_strategy:
                logger.warning(f"Unknown strategy '{strategy}', using text strategy")
                chunking_strategy = self.strategies['text']
            
            # Chunk the document
            chunks = chunking_strategy.chunk_document(file_path, content, specialized_analysis)
            
            # Add file-level metadata to all chunks
            for chunk in chunks:
                chunk.metadata.update({
                    'file_path': file_path,
                    'total_chunks': len(chunks),
                    'file_size': len(content)
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking document {file_path}: {e}")
            # Return a single chunk with the error
            return [DocumentChunk(
                chunk_id="error_chunk",
                content=f"Error chunking document: {str(e)}",
                chunk_type="error",
                metadata={"error": str(e), "file_path": file_path}
            )]