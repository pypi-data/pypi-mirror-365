"""
Text and Data Format Handlers for Document Analysis Framework
"""

import json
import csv
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis

logger = logging.getLogger(__name__)

class MarkdownHandler(DocumentHandler):
    """Handler for Markdown documents"""
    
    handler_type = "text"
    supported_types = ["Markdown", "CommonMark"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith(('.md', '.markdown', '.mdown', '.mkd')):
            return True, 0.95
        if mime_type in ['text/markdown', 'text/x-markdown']:
            return True, 0.95
        
        # Check content for markdown patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:2000]
            markdown_patterns = [
                r'^#{1,6}\s',  # Headers
                r'^\*\s|\-\s|\+\s',  # Lists
                r'\[.*\]\(.*\)',  # Links
                r'```',  # Code blocks
                r'\*\*.*\*\*|\*.*\*',  # Bold/italic
            ]
            matches = sum(1 for pattern in markdown_patterns if re.search(pattern, text, re.MULTILINE))
            if matches >= 2:
                return True, 0.7
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="Markdown Document",
            confidence=0.95,
            category="text",
            subtype="markup",
            encoding="utf-8"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Markdown Document",
            category="text",
            key_findings=findings,
            ai_use_cases=[
                "Documentation analysis and generation",
                "README file processing",
                "Technical writing assistance",
                "Knowledge base construction",
                "Blog content analysis",
                "API documentation processing",
                "Static site generation",
                "Content management systems"
            ],
            quality_metrics={
                "structure_score": findings.get("structure_score", 0.8),
                "readability_score": 0.9,
                "markdown_compliance": 0.85,
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        try:
            text = content.decode('utf-8', errors='replace')
        except:
            text = content.decode('latin-1', errors='replace')
        
        data = {
            "file_size": len(content),
            "format": "Markdown",
            "line_count": text.count('\n') + 1,
            "word_count": len(text.split())
        }
        
        # Analyze markdown structure
        headers = re.findall(r'^(#{1,6})\s+(.+)$', text, re.MULTILINE)
        data["header_count"] = len(headers)
        if headers:
            data["header_levels"] = list(set(len(h[0]) for h in headers))
            data["headers"] = [(len(h[0]), h[1][:50]) for h in headers[:10]]  # First 10 headers
        
        # Count markdown elements
        data["link_count"] = len(re.findall(r'\[.*?\]\(.*?\)', text))
        data["image_count"] = len(re.findall(r'!\[.*?\]\(.*?\)', text))
        data["code_block_count"] = text.count('```')
        data["inline_code_count"] = text.count('`') - (data["code_block_count"] * 6)  # Rough estimate
        
        # Check for tables
        table_rows = re.findall(r'^\|.*\|$', text, re.MULTILINE)
        data["table_row_count"] = len(table_rows)
        
        # Structure score based on organization
        structure_score = 0.5
        if data["header_count"] > 0:
            structure_score += 0.2
        if data["link_count"] > 0:
            structure_score += 0.1
        if data["code_block_count"] > 0:
            structure_score += 0.1
        if data["table_row_count"] > 0:
            structure_score += 0.1
        data["structure_score"] = min(structure_score, 1.0)
        
        return data

class TextHandler(DocumentHandler):
    """Handler for plain text documents"""
    
    handler_type = "text"
    supported_types = ["Plain Text", "Text File"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if mime_type and mime_type.startswith('text/'):
            return True, 0.8
        if file_path.lower().endswith('.txt'):
            return True, 0.9
        
        # Check if content is primarily text
        try:
            text = content.decode('utf-8', errors='strict')
            # Simple heuristic: if we can decode and it's not too binary-looking
            printable_ratio = sum(1 for c in text if c.isprintable() or c.isspace()) / len(text)
            if printable_ratio > 0.8:
                return True, 0.6
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        # Try to detect encoding
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        detected_encoding = 'unknown'
        
        for encoding in encodings:
            try:
                content.decode(encoding)
                detected_encoding = encoding
                break
            except:
                continue
        
        return DocumentTypeInfo(
            type_name="Plain Text Document",
            confidence=0.8,
            category="text",
            subtype="plain",
            encoding=detected_encoding
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Plain Text Document",
            category="text",
            key_findings=findings,
            ai_use_cases=[
                "Text mining and analysis",
                "Natural language processing",
                "Log file analysis",
                "Data preprocessing",
                "Content classification",
                "Sentiment analysis",
                "Document clustering",
                "Information extraction"
            ],
            quality_metrics={
                "text_quality": findings.get("text_quality", 0.7),
                "structure_score": findings.get("structure_score", 0.3),
                "ai_readiness": 0.8
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        text = None
        encoding_used = 'unknown'
        
        for encoding in encodings:
            try:
                text = content.decode(encoding)
                encoding_used = encoding
                break
            except:
                continue
        
        if text is None:
            text = content.decode('utf-8', errors='replace')
            encoding_used = 'utf-8-with-errors'
        
        data = {
            "file_size": len(content),
            "format": "Plain Text",
            "encoding": encoding_used,
            "line_count": text.count('\n') + 1,
            "word_count": len(text.split()),
            "character_count": len(text)
        }
        
        # Text quality metrics
        if text:
            printable_chars = sum(1 for c in text if c.isprintable() or c.isspace())
            data["printable_ratio"] = printable_chars / len(text) if text else 0
            
            # Check for structure indicators
            data["paragraph_count"] = len([p for p in text.split('\n\n') if p.strip()])
            data["empty_line_count"] = text.count('\n\n')
            
            # Basic language detection indicators
            if re.search(r'[a-zA-Z]', text):
                data["contains_latin_text"] = True
            if re.search(r'[0-9]', text):
                data["contains_numbers"] = True
        
        # Quality scores
        text_quality = data.get("printable_ratio", 0) * 0.7 + (0.3 if data.get("paragraph_count", 0) > 1 else 0)
        structure_score = min(data.get("paragraph_count", 0) / 10, 1.0) * 0.5
        
        data["text_quality"] = text_quality
        data["structure_score"] = structure_score
        
        return data

class CSVHandler(DocumentHandler):
    """Handler for CSV (Comma-Separated Values) files"""
    
    handler_type = "data"
    supported_types = ["CSV", "Comma-Separated Values"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith('.csv'):
            return True, 0.95
        if mime_type == 'text/csv':
            return True, 0.95
        
        # Try to detect CSV content
        try:
            text = content.decode('utf-8', errors='ignore')[:2000]
            lines = text.split('\n')[:10]
            if len(lines) >= 2:
                # Check if lines have consistent comma count
                comma_counts = [line.count(',') for line in lines if line.strip()]
                if len(set(comma_counts)) <= 2 and max(comma_counts) > 0:  # Allow some variation
                    return True, 0.7
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="CSV Document",
            confidence=0.95,
            category="data",
            subtype="tabular",
            encoding="utf-8"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="CSV Document",
            category="data",
            key_findings=findings,
            ai_use_cases=[
                "Data analysis and preprocessing",
                "Machine learning dataset preparation",
                "Statistical analysis",
                "Data visualization preparation",
                "Business intelligence",
                "Data migration and ETL",
                "Automated reporting",
                "Predictive modeling"
            ],
            quality_metrics={
                "data_quality": findings.get("data_quality", 0.8),
                "structure_consistency": findings.get("structure_consistency", 0.9),
                "completeness": findings.get("completeness", 0.8),
                "ai_readiness": 0.95
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        try:
            text = content.decode('utf-8', errors='replace')
        except:
            text = content.decode('latin-1', errors='replace')
        
        data = {
            "file_size": len(content),
            "format": "CSV"
        }
        
        try:
            # Parse CSV structure
            lines = text.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            data["row_count"] = len(non_empty_lines)
            
            if non_empty_lines:
                # Analyze first row as headers
                first_row = non_empty_lines[0]
                column_count = first_row.count(',') + 1
                data["column_count"] = column_count
                
                # Extract potential headers
                headers = [h.strip().strip('"\'') for h in first_row.split(',')]
                data["headers"] = headers[:10]  # First 10 headers
                
                # Check consistency
                row_lengths = [line.count(',') + 1 for line in non_empty_lines[:100]]  # Check first 100 rows
                consistency = len(set(row_lengths)) == 1
                data["structure_consistency"] = 1.0 if consistency else 0.7
                
                # Estimate data types
                if len(non_empty_lines) > 1:
                    sample_row = non_empty_lines[1].split(',')
                    data_types = []
                    for value in sample_row[:column_count]:
                        value = value.strip().strip('"\'')
                        if value.isdigit():
                            data_types.append("integer")
                        elif re.match(r'^-?\d*\.\d+$', value):
                            data_types.append("float")
                        else:
                            data_types.append("string")
                    data["estimated_data_types"] = data_types
                
                # Quality metrics
                data["data_quality"] = 0.9 if consistency else 0.7
                data["completeness"] = 0.8  # Would need more analysis for accurate measurement
                
        except Exception as e:
            logger.warning(f"CSV parsing error: {e}")
            data["parsing_error"] = str(e)
        
        return data

class JSONHandler(DocumentHandler):
    """Handler for JSON documents"""
    
    handler_type = "data"
    supported_types = ["JSON", "JavaScript Object Notation"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith('.json'):
            return True, 0.95
        if mime_type == 'application/json':
            return True, 0.95
        
        # Try to parse as JSON
        try:
            text = content.decode('utf-8', errors='ignore')
            json.loads(text)
            return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="JSON Document",
            confidence=0.95,
            category="data",
            subtype="structured",
            encoding="utf-8"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="JSON Document",
            category="data",
            key_findings=findings,
            ai_use_cases=[
                "API response processing",
                "Configuration analysis",
                "Data transformation and ETL",
                "NoSQL database operations",
                "Web scraping result processing",
                "Microservices communication",
                "Log analysis and monitoring",
                "Machine learning feature engineering"
            ],
            quality_metrics={
                "structure_validity": findings.get("structure_validity", 0.0),
                "complexity_score": findings.get("complexity_score", 0.5),
                "data_richness": findings.get("data_richness", 0.7),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        try:
            text = content.decode('utf-8', errors='replace')
        except:
            text = content.decode('latin-1', errors='replace')
        
        data = {
            "file_size": len(content),
            "format": "JSON"
        }
        
        try:
            # Parse JSON
            json_data = json.loads(text)
            data["structure_validity"] = 1.0
            
            # Analyze structure
            if isinstance(json_data, dict):
                data["root_type"] = "object"
                data["top_level_keys"] = list(json_data.keys())[:20]  # First 20 keys
                data["key_count"] = len(json_data.keys())
            elif isinstance(json_data, list):
                data["root_type"] = "array"
                data["array_length"] = len(json_data)
                if json_data:
                    data["first_element_type"] = type(json_data[0]).__name__
            else:
                data["root_type"] = type(json_data).__name__
            
            # Calculate complexity
            def calculate_depth(obj, current_depth=0):
                if isinstance(obj, dict):
                    return max(calculate_depth(v, current_depth + 1) for v in obj.values()) if obj else current_depth
                elif isinstance(obj, list):
                    return max(calculate_depth(item, current_depth + 1) for item in obj) if obj else current_depth
                else:
                    return current_depth
            
            data["max_depth"] = calculate_depth(json_data)
            data["complexity_score"] = min(data["max_depth"] / 10, 1.0)
            data["data_richness"] = 0.8 if data.get("key_count", 0) > 5 or data.get("array_length", 0) > 10 else 0.5
            
        except json.JSONDecodeError as e:
            data["structure_validity"] = 0.0
            data["json_error"] = str(e)
            data["complexity_score"] = 0.0
            data["data_richness"] = 0.0
        except Exception as e:
            logger.warning(f"JSON analysis error: {e}")
            data["analysis_error"] = str(e)
        
        return data

class YAMLHandler(DocumentHandler):
    """Handler for YAML configuration files"""
    
    handler_type = "data"
    supported_types = ["YAML", "YAML Configuration"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith(('.yml', '.yaml')):
            return True, 0.95
        if mime_type in ['application/x-yaml', 'text/yaml']:
            return True, 0.95
        
        # Check content for YAML patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:1000]
            yaml_patterns = [
                r'^\w+:\s*$',  # Key: (with no value)
                r'^\w+:\s+\w+',  # Key: value
                r'^\s*-\s+\w+',  # List items
                r'^---\s*$',  # Document separator
            ]
            matches = sum(1 for pattern in yaml_patterns if re.search(pattern, text, re.MULTILINE))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="YAML Configuration",
            confidence=0.95,
            category="config",
            subtype="structured",
            encoding="utf-8"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="YAML Configuration",
            category="config",
            key_findings=findings,
            ai_use_cases=[
                "Configuration analysis and validation",
                "Infrastructure as Code processing",
                "CI/CD pipeline configuration",
                "Kubernetes manifest analysis",
                "Application configuration management",
                "Environment setup automation",
                "Docker Compose analysis",
                "Ansible playbook processing"
            ],
            quality_metrics={
                "structure_validity": findings.get("structure_validity", 0.0),
                "complexity_score": findings.get("complexity_score", 0.5),
                "configuration_completeness": findings.get("config_completeness", 0.7),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        try:
            text = content.decode('utf-8', errors='replace')
        except:
            text = content.decode('latin-1', errors='replace')
        
        data = {
            "file_size": len(content),
            "format": "YAML",
            "line_count": text.count('\n') + 1
        }
        
        # Simple YAML parsing (without external dependencies)
        lines = [line.rstrip() for line in text.split('\n')]
        
        # Count structure elements
        top_level_keys = []
        list_items = 0
        comments = 0
        documents = 0
        
        for line in lines:
            if line.strip().startswith('#'):
                comments += 1
            elif line.strip() == '---':
                documents += 1
            elif re.match(r'^\w+:\s*', line):  # Top-level key
                key = line.split(':')[0].strip()
                top_level_keys.append(key)
            elif re.match(r'^\s*-\s+', line):  # List item
                list_items += 1
        
        data["top_level_keys"] = top_level_keys[:20]  # First 20 keys
        data["key_count"] = len(top_level_keys)
        data["list_items"] = list_items
        data["comment_lines"] = comments
        data["document_count"] = max(documents, 1)
        
        # Try to detect common YAML types
        yaml_types = []
        key_names = [key.lower() for key in top_level_keys]
        
        if any(k in key_names for k in ['apiversion', 'kind', 'metadata']):
            yaml_types.append("Kubernetes")
        if any(k in key_names for k in ['version', 'services', 'volumes']):
            yaml_types.append("Docker Compose")
        if any(k in key_names for k in ['name', 'on', 'jobs', 'steps']):
            yaml_types.append("GitHub Actions")
        if any(k in key_names for k in ['hosts', 'tasks', 'vars']):
            yaml_types.append("Ansible")
        
        data["detected_types"] = yaml_types
        
        # Quality metrics
        structure_validity = 0.8 if len(top_level_keys) > 0 else 0.3
        complexity_score = min(len(top_level_keys) / 20, 1.0)
        config_completeness = 0.7 + (0.2 if comments > 0 else 0) + (0.1 if yaml_types else 0)
        
        data["structure_validity"] = structure_validity
        data["complexity_score"] = complexity_score
        data["config_completeness"] = min(config_completeness, 1.0)
        
        return data

class TOMLHandler(DocumentHandler):
    """Handler for TOML configuration files"""
    
    handler_type = "config"
    supported_types = ["TOML", "TOML Configuration"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith('.toml'):
            return True, 0.95
        if mime_type == 'application/toml':
            return True, 0.95
        
        # Check content for TOML patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:1000]
            toml_patterns = [
                r'^\[[\w\.\-]+\]',  # [section]
                r'^\w+\s*=\s*["\']',  # key = "value"
                r'^\w+\s*=\s*\d+',  # key = number
                r'^\w+\s*=\s*true|false',  # key = boolean
            ]
            matches = sum(1 for pattern in toml_patterns if re.search(pattern, text, re.MULTILINE))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        # Try to detect TOML subtype
        try:
            text = content.decode('utf-8', errors='ignore')
            if 'pyproject.toml' in file_path.lower():
                subtype = "Python Project"
            elif 'cargo.toml' in file_path.lower():
                subtype = "Rust Cargo"
            elif '[tool.' in text:
                subtype = "Tool Configuration"
            else:
                subtype = "General Configuration"
        except:
            subtype = "General Configuration"
        
        return DocumentTypeInfo(
            type_name="TOML Configuration",
            confidence=0.95,
            category="config",
            subtype=subtype,
            encoding="utf-8"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="TOML Configuration",
            category="config",
            key_findings=findings,
            ai_use_cases=[
                "Project configuration analysis",
                "Dependency management",
                "Build system configuration",
                "Tool settings optimization",
                "Package metadata extraction",
                "Configuration migration assistance",
                "Project structure analysis",
                "Development environment setup"
            ],
            quality_metrics={
                "structure_validity": findings.get("structure_validity", 0.8),
                "completeness_score": findings.get("completeness_score", 0.7),
                "organization_quality": findings.get("organization_quality", 0.6),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        try:
            text = content.decode('utf-8', errors='replace')
        except:
            text = content.decode('latin-1', errors='replace')
        
        data = {
            "file_size": len(content),
            "format": "TOML",
            "line_count": text.count('\n') + 1
        }
        
        # Parse TOML structure (basic parsing without external deps)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        sections = []
        current_section = None
        key_value_pairs = 0
        comments = 0
        
        for line in lines:
            if line.startswith('#'):
                comments += 1
            elif line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                sections.append(current_section)
            elif '=' in line and not line.startswith('#'):
                key_value_pairs += 1
        
        data["sections"] = sections[:20]  # First 20 sections
        data["section_count"] = len(sections)
        data["key_value_pairs"] = key_value_pairs
        data["comment_lines"] = comments
        
        # Try to detect project type
        project_types = []
        text_lower = text.lower()
        
        if 'pyproject.toml' in file_path.lower() or '[build-system]' in text:
            project_types.append("Python Project")
        if 'cargo.toml' in file_path.lower() or '[package]' in text:
            project_types.append("Rust Project")
        if '[tool.' in text:
            project_types.append("Development Tools")
        
        data["detected_project_types"] = project_types
        
        # Quality metrics
        structure_validity = 0.9 if len(sections) > 0 else 0.7
        completeness_score = min((key_value_pairs + len(sections)) / 20, 1.0)
        organization_quality = 0.5 + (0.3 if len(sections) > 2 else 0) + (0.2 if comments > 5 else 0)
        
        data["structure_validity"] = structure_validity
        data["completeness_score"] = completeness_score
        data["organization_quality"] = min(organization_quality, 1.0)
        
        return data