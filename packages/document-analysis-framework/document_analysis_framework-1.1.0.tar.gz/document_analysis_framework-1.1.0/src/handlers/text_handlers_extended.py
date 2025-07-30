"""
Extended text and data handlers for additional file types
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import csv
import io
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class LaTeXHandler(DocumentHandler):
    """Handler for LaTeX documents"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.tex'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # LaTeX patterns
            if any(pattern in text for pattern in [
                '\\documentclass', '\\begin{document}', '\\section{',
                '\\usepackage{', '\\title{', '\\author{'
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if '\\documentclass{article}' in text:
            type_name = "LaTeX Article"
        elif '\\documentclass{book}' in text:
            type_name = "LaTeX Book"
        elif '\\documentclass{report}' in text:
            type_name = "LaTeX Report"
        elif 'beamer' in text:
            type_name = "LaTeX Beamer Presentation"
        else:
            type_name = "LaTeX Document"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="document",
            format="latex"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="LaTeX",
            category="document",
            key_findings=findings,
            ai_use_cases=[
                "Document structure analysis",
                "Bibliography management",
                "Mathematical formula extraction",
                "Cross-reference checking",
                "Compilation error debugging"
            ],
            quality_metrics={
                "structure_quality": self._assess_structure(findings),
                "completeness": self._assess_completeness(findings),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "document_class": self._extract_document_class(text),
            "packages": self._extract_packages(text),
            "sections": self._extract_sections(text),
            "figures": self._count_figures(text),
            "tables": self._count_tables(text),
            "equations": self._count_equations(text),
            "citations": self._extract_citations(text),
            "labels": self._extract_labels(text),
            "references": self._extract_references(text),
            "commands": self._extract_custom_commands(text)
        }
    
    def _extract_document_class(self, text: str) -> str:
        match = re.search(r'\\documentclass(?:\[.*?\])?\{(\w+)\}', text)
        return match.group(1) if match else "unknown"
    
    def _extract_packages(self, text: str) -> List[str]:
        return re.findall(r'\\usepackage(?:\[.*?\])?\{([^}]+)\}', text)
    
    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        sections = []
        section_types = ['part', 'chapter', 'section', 'subsection', 'subsubsection']
        
        for section_type in section_types:
            for match in re.finditer(rf'\\{section_type}\{{([^}}]+)\}}', text):
                sections.append({
                    'type': section_type,
                    'title': match.group(1)
                })
        
        return sections
    
    def _count_figures(self, text: str) -> int:
        return len(re.findall(r'\\begin\{figure\}', text))
    
    def _count_tables(self, text: str) -> int:
        return len(re.findall(r'\\begin\{table\}', text))
    
    def _count_equations(self, text: str) -> int:
        # Count various equation environments
        equation_envs = ['equation', 'align', 'gather', 'multline']
        count = 0
        for env in equation_envs:
            count += len(re.findall(rf'\\begin\{{{env}\*?\}}', text))
        # Also count inline math
        count += len(re.findall(r'\$[^$]+\$', text))
        return count
    
    def _extract_citations(self, text: str) -> List[str]:
        citations = []
        # \cite{key} and \cite{key1,key2}
        for match in re.finditer(r'\\cite(?:\[.*?\])?\{([^}]+)\}', text):
            citations.extend([c.strip() for c in match.group(1).split(',')])
        return list(set(citations))
    
    def _extract_labels(self, text: str) -> List[str]:
        return re.findall(r'\\label\{([^}]+)\}', text)
    
    def _extract_references(self, text: str) -> List[str]:
        return re.findall(r'\\ref\{([^}]+)\}', text)
    
    def _extract_custom_commands(self, text: str) -> List[str]:
        commands = []
        # \newcommand{\cmd}{definition}
        commands.extend(re.findall(r'\\newcommand\{\\(\w+)\}', text))
        # \def\cmd{definition}
        commands.extend(re.findall(r'\\def\\(\w+)', text))
        return commands
    
    def _assess_structure(self, findings: Dict[str, Any]) -> float:
        sections = findings.get('sections', [])
        if not sections:
            return 0.5
        
        # Check for logical hierarchy
        section_types = [s['type'] for s in sections]
        hierarchy_score = 0.5
        
        # Good structure has varied section levels
        unique_types = len(set(section_types))
        if unique_types > 1:
            hierarchy_score = min(unique_types / 4, 1.0)
        
        return hierarchy_score
    
    def _assess_completeness(self, findings: Dict[str, Any]) -> float:
        # Check if references match labels
        labels = set(findings.get('labels', []))
        references = set(findings.get('references', []))
        
        if not references:
            return 1.0  # No references to check
        
        matched = len(references.intersection(labels))
        return matched / len(references) if references else 0.0


class AsciiDocHandler(DocumentHandler):
    """Handler for AsciiDoc documents"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith(('.adoc', '.asciidoc', '.asc')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # AsciiDoc patterns
            if any(pattern in text for pattern in [
                '= ', '== ', '=== ', ':toc:', ':author:', '[source,',
                '----', '....', '____', '****'
            ]):
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="AsciiDoc Document",
            confidence=0.95,
            category="document",
            format="asciidoc"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="AsciiDoc",
            category="document",
            key_findings=findings,
            ai_use_cases=[
                "Documentation generation",
                "Technical writing assistance",
                "Format conversion",
                "Structure validation",
                "Cross-reference management"
            ],
            quality_metrics={
                "structure_quality": self._assess_structure(findings),
                "formatting_consistency": self._assess_formatting(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "title": self._extract_title(text),
            "attributes": self._extract_attributes(text),
            "sections": self._extract_sections(text),
            "code_blocks": self._extract_code_blocks(text),
            "links": self._extract_links(text),
            "images": self._extract_images(text),
            "tables": self._count_tables(text),
            "lists": self._count_lists(text),
            "admonitions": self._extract_admonitions(text)
        }
    
    def _extract_title(self, text: str) -> str:
        match = re.search(r'^=\s+(.+)$', text, re.MULTILINE)
        return match.group(1) if match else ""
    
    def _extract_attributes(self, text: str) -> Dict[str, str]:
        attributes = {}
        for match in re.finditer(r'^:(\w+):\s*(.*)$', text, re.MULTILINE):
            attributes[match.group(1)] = match.group(2)
        return attributes
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        sections = []
        # Match section headers (=, ==, ===, etc.)
        for match in re.finditer(r'^(=+)\s+(.+)$', text, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2)
            sections.append({
                'level': level,
                'title': title
            })
        return sections
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        code_blocks = []
        # [source,language]
        for match in re.finditer(r'\[source,(\w+)\]\n----\n(.*?)\n----', text, re.DOTALL):
            code_blocks.append({
                'language': match.group(1),
                'lines': len(match.group(2).split('\n'))
            })
        return code_blocks
    
    def _extract_links(self, text: str) -> List[str]:
        links = []
        # External links: https://example.com[text]
        links.extend(re.findall(r'(https?://[^\s\[]+)', text))
        # Cross references: <<anchor,text>>
        links.extend(re.findall(r'<<([^,>]+)(?:,[^>]+)?>', text))
        return links
    
    def _extract_images(self, text: str) -> List[str]:
        return re.findall(r'image::([^\[]+)', text)
    
    def _count_tables(self, text: str) -> int:
        # Count table blocks (|===)
        return len(re.findall(r'\|===', text))
    
    def _count_lists(self, text: str) -> Dict[str, int]:
        return {
            'unordered': len(re.findall(r'^\*\s+', text, re.MULTILINE)),
            'ordered': len(re.findall(r'^\.\s+', text, re.MULTILINE)),
            'description': len(re.findall(r'^.+::\s*$', text, re.MULTILINE))
        }
    
    def _extract_admonitions(self, text: str) -> List[str]:
        admonition_types = ['NOTE', 'TIP', 'IMPORTANT', 'WARNING', 'CAUTION']
        found = []
        for adm in admonition_types:
            if re.search(rf'^{adm}:', text, re.MULTILINE):
                found.append(adm)
        return found
    
    def _assess_structure(self, findings: Dict[str, Any]) -> float:
        sections = findings.get('sections', [])
        if not sections:
            return 0.3
        
        # Check for proper hierarchy
        levels = [s['level'] for s in sections]
        unique_levels = len(set(levels))
        
        # Good structure has multiple levels
        return min(unique_levels / 4, 1.0)
    
    def _assess_formatting(self, findings: Dict[str, Any]) -> float:
        score = 0.5
        
        # Has attributes defined
        if findings.get('attributes'):
            score += 0.1
        
        # Uses code blocks
        if findings.get('code_blocks'):
            score += 0.1
        
        # Has images
        if findings.get('images'):
            score += 0.1
        
        # Uses admonitions
        if findings.get('admonitions'):
            score += 0.1
        
        # Has tables
        if findings.get('tables', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)


class ReStructuredTextHandler(DocumentHandler):
    """Handler for reStructuredText documents"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.rst'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # RST patterns
            if any(pattern in text for pattern in [
                '.. ', '::', '===', '---', '^^^', '"""',
                '.. code-block::', '.. image::', '.. note::'
            ]):
                # Check for section underlines
                if re.search(r'^.+\n[=\-~`#"^+*]+$', text, re.MULTILINE):
                    return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if 'sphinx' in text.lower() or 'conf.py' in file_path:
            type_name = "Sphinx Documentation"
        else:
            type_name = "reStructuredText Document"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="document",
            format="rst"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="reStructuredText",
            category="document",
            key_findings=findings,
            ai_use_cases=[
                "Documentation maintenance",
                "Sphinx documentation",
                "API documentation",
                "Format validation",
                "Cross-reference checking"
            ],
            quality_metrics={
                "structure_quality": self._assess_structure(findings),
                "directive_usage": self._assess_directives(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "title": self._extract_title(text),
            "sections": self._extract_sections(text),
            "directives": self._extract_directives(text),
            "code_blocks": self._extract_code_blocks(text),
            "links": self._extract_links(text),
            "images": self._extract_images(text),
            "footnotes": self._extract_footnotes(text),
            "citations": self._extract_citations(text),
            "toctree": self._extract_toctree(text)
        }
    
    def _extract_title(self, text: str) -> str:
        # RST titles are text with underline of same length
        match = re.search(r'^(.+)\n(={3,}|#{3,})$', text, re.MULTILINE)
        return match.group(1) if match else ""
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        sections = []
        # Section markers in order of hierarchy
        section_chars = ['=', '-', '~', '^', '"', '#', '*', '+']
        
        for match in re.finditer(r'^(.+)\n([=\-~^"#*+])\2+$', text, re.MULTILINE):
            title = match.group(1)
            char = match.group(2)
            level = section_chars.index(char) + 1 if char in section_chars else 9
            
            sections.append({
                'title': title,
                'level': level,
                'marker': char
            })
        
        return sections
    
    def _extract_directives(self, text: str) -> List[Dict[str, str]]:
        directives = []
        # .. directive:: arguments
        for match in re.finditer(r'^\.\.\s+(\w+)::\s*(.*?)$', text, re.MULTILINE):
            directives.append({
                'name': match.group(1),
                'args': match.group(2)
            })
        return directives
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        code_blocks = []
        # .. code-block:: language
        for match in re.finditer(r'\.\.\s+code-block::\s*(\w+).*?\n\n((?:\s{3,}.*\n)+)', text):
            code_blocks.append({
                'language': match.group(1),
                'lines': len(match.group(2).strip().split('\n'))
            })
        return code_blocks
    
    def _extract_links(self, text: str) -> List[Dict[str, str]]:
        links = []
        # External links `text <url>`_
        for match in re.finditer(r'`([^<]+)\s+<([^>]+)>`_', text):
            links.append({
                'text': match.group(1),
                'url': match.group(2),
                'type': 'external'
            })
        # Internal references :ref:`label`
        for match in re.finditer(r':ref:`([^`]+)`', text):
            links.append({
                'text': match.group(1),
                'url': '',
                'type': 'internal'
            })
        return links
    
    def _extract_images(self, text: str) -> List[str]:
        images = []
        # .. image:: path
        images.extend(re.findall(r'\.\.\s+image::\s+(.+)$', text, re.MULTILINE))
        # .. figure:: path
        images.extend(re.findall(r'\.\.\s+figure::\s+(.+)$', text, re.MULTILINE))
        return images
    
    def _extract_footnotes(self, text: str) -> int:
        # [#]_ or [#name]_
        return len(re.findall(r'\[\#\w*\]_', text))
    
    def _extract_citations(self, text: str) -> List[str]:
        # [citation]_
        return re.findall(r'\[([^\]]+)\]_', text)
    
    def _extract_toctree(self, text: str) -> List[str]:
        toctree_docs = []
        # Find toctree directive and its contents
        toctree_match = re.search(r'\.\.\s+toctree::.*?\n\n((?:\s{3,}.*\n)+)', text, re.DOTALL)
        if toctree_match:
            content = toctree_match.group(1)
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith(':'):
                    toctree_docs.append(line)
        return toctree_docs
    
    def _assess_structure(self, findings: Dict[str, Any]) -> float:
        sections = findings.get('sections', [])
        if not sections:
            return 0.3
        
        # Check section hierarchy
        levels = [s['level'] for s in sections]
        unique_levels = len(set(levels))
        
        return min(unique_levels / 4, 1.0)
    
    def _assess_directives(self, findings: Dict[str, Any]) -> float:
        directives = findings.get('directives', [])
        directive_names = [d['name'] for d in directives]
        
        # Common useful directives
        useful_directives = ['note', 'warning', 'code-block', 'image', 'figure', 
                           'toctree', 'automodule', 'autoclass', 'autofunction']
        
        used_useful = sum(1 for d in useful_directives if d in directive_names)
        
        return min(used_useful / 5, 1.0)


class TSVHandler(DocumentHandler):
    """Handler for Tab-Separated Values files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.tsv'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            lines = text.strip().split('\n')[:10]  # Check first 10 lines
            
            if len(lines) > 1:
                # Check if consistent tab counts
                tab_counts = [line.count('\t') for line in lines if line]
                if tab_counts and all(count == tab_counts[0] for count in tab_counts):
                    return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="Tab-Separated Values",
            confidence=0.95,
            category="data",
            format="tsv"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="TSV Data",
            category="data",
            key_findings=findings,
            ai_use_cases=[
                "Data analysis and visualization",
                "Statistical processing",
                "Data quality assessment",
                "Format conversion",
                "Data integration"
            ],
            quality_metrics={
                "data_quality": self._assess_data_quality(findings),
                "completeness": self._assess_completeness(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        # Parse TSV
        reader = csv.reader(io.StringIO(text), delimiter='\t')
        rows = list(reader)
        
        if not rows:
            return {"error": "Empty TSV file"}
        
        # Assume first row is header
        headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        # Analyze data types
        column_types = self._infer_column_types(data_rows, len(headers))
        
        return {
            "headers": headers,
            "row_count": len(data_rows),
            "column_count": len(headers),
            "column_types": column_types,
            "sample_data": data_rows[:5],  # First 5 rows
            "empty_cells": self._count_empty_cells(data_rows),
            "unique_values": self._count_unique_values(data_rows, headers)
        }
    
    def _infer_column_types(self, rows: List[List[str]], num_columns: int) -> List[str]:
        if not rows:
            return ["unknown"] * num_columns
        
        column_types = []
        
        for col_idx in range(num_columns):
            values = [row[col_idx] for row in rows if col_idx < len(row) and row[col_idx]]
            
            if not values:
                column_types.append("empty")
                continue
            
            # Try to infer type
            is_numeric = True
            is_integer = True
            
            for value in values[:100]:  # Sample first 100
                try:
                    float(value)
                    if '.' in value:
                        is_integer = False
                except ValueError:
                    is_numeric = False
                    is_integer = False
                    break
            
            if is_integer:
                column_types.append("integer")
            elif is_numeric:
                column_types.append("float")
            else:
                column_types.append("string")
        
        return column_types
    
    def _count_empty_cells(self, rows: List[List[str]]) -> int:
        count = 0
        for row in rows:
            for cell in row:
                if not cell or cell.isspace():
                    count += 1
        return count
    
    def _count_unique_values(self, rows: List[List[str]], headers: List[str]) -> Dict[str, int]:
        unique_counts = {}
        
        for col_idx, header in enumerate(headers):
            values = set()
            for row in rows:
                if col_idx < len(row) and row[col_idx]:
                    values.add(row[col_idx])
            unique_counts[header] = len(values)
        
        return unique_counts
    
    def _assess_data_quality(self, findings: Dict[str, Any]) -> float:
        if "error" in findings:
            return 0.0
        
        row_count = findings.get('row_count', 0)
        col_count = findings.get('column_count', 0)
        empty_cells = findings.get('empty_cells', 0)
        
        if row_count == 0 or col_count == 0:
            return 0.0
        
        total_cells = row_count * col_count
        completeness = 1.0 - (empty_cells / total_cells) if total_cells > 0 else 0.0
        
        return completeness
    
    def _assess_completeness(self, findings: Dict[str, Any]) -> float:
        # Similar to data quality for TSV
        return self._assess_data_quality(findings)


class LogFileHandler(DocumentHandler):
    """Handler for log files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.log'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Common log patterns
            log_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # Date
                r'\d{2}:\d{2}:\d{2}',  # Time
                r'\[(ERROR|WARN|INFO|DEBUG)\]',  # Log levels
                r'(ERROR|WARN|INFO|DEBUG):',
                r'^\d+\s+\w+\s+\d+\s+\d+:\d+:\d+',  # Syslog format
            ]
            
            matches = sum(1 for pattern in log_patterns if re.search(pattern, text))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if 'apache' in file_path.lower() or re.search(r'\d+\.\d+\.\d+\.\d+.*"(GET|POST|PUT)', text):
            type_name = "Apache Access Log"
        elif 'error' in file_path.lower():
            type_name = "Error Log"
        elif 'nginx' in file_path.lower():
            type_name = "Nginx Log"
        elif re.search(r'(ERROR|WARN|INFO|DEBUG)', text):
            type_name = "Application Log"
        else:
            type_name = "Log File"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.9,
            category="logs",
            format="log"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Log File",
            category="logs",
            key_findings=findings,
            ai_use_cases=[
                "Error pattern detection",
                "Performance analysis",
                "Security incident detection",
                "Trend analysis",
                "Anomaly detection"
            ],
            quality_metrics={
                "parsability": self._assess_parsability(findings),
                "information_density": self._assess_information_density(findings),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        lines = text.split('\n')
        
        return {
            "total_lines": len(lines),
            "log_levels": self._extract_log_levels(text),
            "timestamps": self._analyze_timestamps(text),
            "error_messages": self._extract_errors(text),
            "ip_addresses": self._extract_ips(text),
            "status_codes": self._extract_status_codes(text),
            "patterns": self._identify_patterns(text),
            "time_range": self._get_time_range(text)
        }
    
    def _extract_log_levels(self, text: str) -> Dict[str, int]:
        levels = {
            'ERROR': len(re.findall(r'\b(ERROR|ERR)\b', text, re.IGNORECASE)),
            'WARN': len(re.findall(r'\b(WARN|WARNING)\b', text, re.IGNORECASE)),
            'INFO': len(re.findall(r'\bINFO\b', text, re.IGNORECASE)),
            'DEBUG': len(re.findall(r'\bDEBUG\b', text, re.IGNORECASE))
        }
        return {k: v for k, v in levels.items() if v > 0}
    
    def _analyze_timestamps(self, text: str) -> Dict[str, Any]:
        # Common timestamp formats
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # ISO format
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',  # Apache format
            r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',  # Syslog format
        ]
        
        for pattern in timestamp_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return {
                    "format": pattern,
                    "count": len(matches),
                    "sample": matches[0] if matches else None
                }
        
        return {"format": "unknown", "count": 0}
    
    def _extract_errors(self, text: str) -> List[str]:
        errors = []
        error_lines = re.findall(r'^.*\b(?:ERROR|ERR|Exception|Failed)\b.*$', text, re.MULTILINE | re.IGNORECASE)
        
        # Get unique error messages (limit to first 10)
        seen = set()
        for line in error_lines:
            # Try to extract just the error message part
            clean_line = re.sub(r'^\d{4}-\d{2}-\d{2}.*?\]\s*', '', line)
            clean_line = re.sub(r'^\[.*?\]\s*', '', clean_line)
            
            if clean_line not in seen:
                errors.append(clean_line)
                seen.add(clean_line)
                
            if len(errors) >= 10:
                break
        
        return errors
    
    def _extract_ips(self, text: str) -> List[str]:
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, text)
        return list(set(ips))[:20]  # Unique IPs, limit to 20
    
    def _extract_status_codes(self, text: str) -> Dict[str, int]:
        # HTTP status codes
        status_codes = {}
        for match in re.finditer(r'\b([1-5]\d{2})\b', text):
            code = match.group(1)
            if code in ['200', '201', '204', '301', '302', '304', '400', '401', 
                       '403', '404', '500', '502', '503', '504']:
                status_codes[code] = status_codes.get(code, 0) + 1
        
        return status_codes
    
    def _identify_patterns(self, text: str) -> List[str]:
        patterns = []
        
        # Check for common log formats
        if re.search(r'\d+\.\d+\.\d+\.\d+.*"(GET|POST|PUT)', text):
            patterns.append("HTTP Access Log")
        
        if re.search(r'java\.\w+\..*Exception', text):
            patterns.append("Java Stack Traces")
        
        if re.search(r'at\s+\w+\.\w+\(.*\.java:\d+\)', text):
            patterns.append("Java Stack Trace Format")
        
        if re.search(r'\[pid\s+\d+\]', text):
            patterns.append("Process IDs")
        
        return patterns
    
    def _get_time_range(self, text: str) -> Dict[str, str]:
        # Try to find first and last timestamp
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}'
        timestamps = re.findall(timestamp_pattern, text)
        
        if timestamps:
            return {
                "start": timestamps[0],
                "end": timestamps[-1]
            }
        
        return {"start": "unknown", "end": "unknown"}
    
    def _assess_parsability(self, findings: Dict[str, Any]) -> float:
        # Check if we can identify timestamp format and structure
        score = 0.5
        
        if findings.get('timestamps', {}).get('format') != 'unknown':
            score += 0.3
        
        if findings.get('patterns'):
            score += 0.2
        
        return score
    
    def _assess_information_density(self, findings: Dict[str, Any]) -> float:
        # Assess how much useful information is in the logs
        total_lines = findings.get('total_lines', 0)
        if total_lines == 0:
            return 0.0
        
        # Count informative elements
        error_count = sum(findings.get('log_levels', {}).values())
        ip_count = len(findings.get('ip_addresses', []))
        
        info_score = min((error_count + ip_count) / total_lines * 10, 1.0)
        
        return info_score


class ExcelHandler(DocumentHandler):
    """Handler for Excel files (basic text extraction)"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith(('.xls', '.xlsx')):
            return True, 0.95
        
        # Check for Excel file signatures
        if content.startswith(b'PK'):  # XLSX (ZIP format)
            return True, 0.8
        elif content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):  # XLS
            return True, 0.8
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        if file_path.endswith('.xlsx'):
            format_type = "xlsx"
            type_name = "Excel Workbook (XLSX)"
        else:
            format_type = "xls"
            type_name = "Excel Workbook (XLS)"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.9,
            category="spreadsheet",
            format=format_type
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Excel Spreadsheet",
            category="spreadsheet",
            key_findings=findings,
            ai_use_cases=[
                "Data extraction and analysis",
                "Formula validation",
                "Data quality assessment",
                "Format conversion",
                "Statistical analysis"
            ],
            quality_metrics={
                "extraction_success": 0.7,  # Limited without external libraries
                "ai_readiness": 0.6
            },
            structured_data=findings,
            metadata={
                "note": "Limited analysis without openpyxl/xlrd. Consider using docling-analysis-framework for full Excel support."
            }
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        # Note: This is a basic extraction without external libraries
        # For full Excel support, use docling-analysis-framework
        
        findings = {
            "file_size": len(content),
            "format": "xlsx" if file_path.endswith('.xlsx') else "xls",
            "extraction_limited": True,
            "recommendation": "Use docling-analysis-framework for full Excel analysis"
        }
        
        # Try to extract some basic info from XLSX (ZIP format)
        if content.startswith(b'PK'):
            findings["type"] = "XLSX (ZIP-based)"
            # Could extract worksheet names from ZIP structure if needed
        elif content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            findings["type"] = "XLS (Binary format)"
        
        # Extract any readable text (very basic)
        try:
            text = content.decode('utf-8', errors='ignore')
            # Look for common Excel patterns
            if 'xl/worksheets' in text:
                findings["sheets_detected"] = True
            if 'xl/sharedStrings.xml' in text:
                findings["shared_strings"] = True
        except:
            pass
        
        return findings 