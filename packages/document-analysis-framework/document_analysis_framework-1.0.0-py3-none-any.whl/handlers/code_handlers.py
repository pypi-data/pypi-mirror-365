"""
Code File Handlers for Document Analysis Framework
"""

import re
import ast
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis

logger = logging.getLogger(__name__)

class PythonHandler(DocumentHandler):
    """Handler for Python source code files"""
    
    handler_type = "code"
    supported_types = ["Python", "Python Script"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith('.py'):
            return True, 0.95
        if mime_type == 'text/x-python':
            return True, 0.95
        
        # Check for Python shebang or common patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:500]
            if text.startswith('#!/usr/bin/env python') or text.startswith('#!/usr/bin/python'):
                return True, 0.9
            # Look for Python-specific patterns
            python_patterns = [
                r'import \w+',
                r'from \w+ import',
                r'def \w+\(',
                r'class \w+\(',
                r'if __name__ == ["\']__main__["\']'
            ]
            matches = sum(1 for pattern in python_patterns if re.search(pattern, text))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        # Try to detect Python version hints
        try:
            text = content.decode('utf-8', errors='ignore')
            if 'python_requires' in text:
                version_match = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', text)
                version = version_match.group(1) if version_match else "unknown"
            else:
                version = "unknown"
        except:
            version = "unknown"
        
        return DocumentTypeInfo(
            type_name="Python Script",
            confidence=0.95,
            category="code",
            version=version,
            subtype="source_code",
            language="python"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Python Script",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Code analysis and quality assessment",
                "Automated code review",
                "Dependency analysis",
                "Security vulnerability scanning",
                "Code documentation generation",
                "Refactoring suggestions",
                "Test coverage analysis",
                "Performance optimization recommendations",
                "Code similarity detection",
                "API usage pattern analysis"
            ],
            quality_metrics={
                "code_complexity": findings.get("complexity_score", 0.5),
                "documentation_score": findings.get("documentation_score", 0.3),
                "structure_quality": findings.get("structure_quality", 0.7),
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
            "format": "Python",
            "line_count": text.count('\n') + 1
        }
        
        try:
            # Try to parse the AST for detailed analysis
            tree = ast.parse(text)
            
            # Count different node types
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            data["class_count"] = len(classes)
            data["function_count"] = len(functions)
            data["import_count"] = len(imports)
            
            # Extract names
            if classes:
                data["class_names"] = [cls.name for cls in classes[:10]]
            if functions:
                data["function_names"] = [func.name for func in functions[:20]]
            
            # Extract imports
            import_modules = []
            for imp in imports:
                if isinstance(imp, ast.Import):
                    import_modules.extend([alias.name for alias in imp.names])
                elif isinstance(imp, ast.ImportFrom):
                    if imp.module:
                        import_modules.append(imp.module)
            data["imported_modules"] = list(set(import_modules))[:20]
            
            # Calculate complexity (simple metric based on nesting)
            max_depth = 0
            for node in ast.walk(tree):
                depth = 0
                parent = node
                while hasattr(parent, 'parent'):
                    parent = parent.parent
                    depth += 1
                max_depth = max(max_depth, depth)
            
            data["complexity_score"] = min(max_depth / 20, 1.0)
            
        except SyntaxError as e:
            data["syntax_error"] = str(e)
            data["parseable"] = False
        except Exception as e:
            logger.warning(f"Python AST parsing error: {e}")
            data["parsing_error"] = str(e)
        
        # Analyze documentation
        docstring_matches = re.findall(r'""".*?"""', text, re.DOTALL)
        docstring_matches.extend(re.findall(r"'''.*?'''", text, re.DOTALL))
        comment_lines = len(re.findall(r'^\s*#', text, re.MULTILINE))
        
        data["docstring_count"] = len(docstring_matches)
        data["comment_line_count"] = comment_lines
        
        # Documentation score
        total_lines = data["line_count"]
        doc_lines = sum(len(doc.split('\n')) for doc in docstring_matches) + comment_lines
        data["documentation_score"] = min(doc_lines / total_lines, 1.0) if total_lines > 0 else 0
        
        # Structure quality score
        structure_score = 0.5
        if data.get("function_count", 0) > 0:
            structure_score += 0.2
        if data.get("class_count", 0) > 0:
            structure_score += 0.2
        if data.get("documentation_score", 0) > 0.1:
            structure_score += 0.1
        data["structure_quality"] = min(structure_score, 1.0)
        
        return data

class JavaScriptHandler(DocumentHandler):
    """Handler for JavaScript source code files"""
    
    handler_type = "code"
    supported_types = ["JavaScript", "ECMAScript", "Node.js"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith(('.js', '.mjs', '.jsx')):
            return True, 0.95
        if mime_type in ['application/javascript', 'text/javascript']:
            return True, 0.95
        
        # Check for JavaScript patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:1000]
            js_patterns = [
                r'function\s+\w+\s*\(',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'require\s*\(',
                r'import\s+.*from',
                r'export\s+(default\s+)?'
            ]
            matches = sum(1 for pattern in js_patterns if re.search(pattern, text))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        # Try to detect if it's Node.js, React, etc.
        try:
            text = content.decode('utf-8', errors='ignore')
            if 'require(' in text or 'module.exports' in text:
                subtype = "nodejs"
            elif 'import React' in text or 'from \'react\'' in text:
                subtype = "react"
            elif file_path.lower().endswith('.jsx'):
                subtype = "jsx"
            else:
                subtype = "vanilla"
        except:
            subtype = "unknown"
        
        return DocumentTypeInfo(
            type_name="JavaScript",
            confidence=0.95,
            category="code",
            subtype=subtype,
            language="javascript"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="JavaScript",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Code quality analysis",
                "Security vulnerability detection",
                "Performance optimization",
                "Dependency analysis",
                "Framework detection and migration",
                "API usage pattern analysis",
                "Code documentation generation",
                "Testing strategy recommendations",
                "Bundle size optimization",
                "Modern syntax migration"
            ],
            quality_metrics={
                "complexity_score": findings.get("complexity_score", 0.5),
                "modern_syntax_usage": findings.get("modern_syntax_score", 0.5),
                "structure_quality": findings.get("structure_quality", 0.7),
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
            "format": "JavaScript",
            "line_count": text.count('\n') + 1
        }
        
        # Count functions
        function_patterns = [
            r'function\s+(\w+)\s*\(',  # function declarations
            r'(\w+)\s*:\s*function\s*\(',  # method definitions
            r'(\w+)\s*=>\s*{',  # arrow functions
            r'const\s+(\w+)\s*=\s*\(',  # const function assignments
        ]
        
        functions = []
        for pattern in function_patterns[:2]:  # Only named functions for counting
            functions.extend(re.findall(pattern, text))
        
        data["function_count"] = len(functions)
        if functions:
            data["function_names"] = functions[:20]
        
        # Count classes (ES6)
        classes = re.findall(r'class\s+(\w+)', text)
        data["class_count"] = len(classes)
        if classes:
            data["class_names"] = classes[:10]
        
        # Check for imports/requires
        imports = []
        imports.extend(re.findall(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', text))
        imports.extend(re.findall(r'require\s*\(\s*["\']([^"\']+)["\']', text))
        data["import_count"] = len(imports)
        data["imported_modules"] = list(set(imports))[:20]
        
        # Modern JavaScript features
        modern_features = {
            "arrow_functions": len(re.findall(r'=>', text)),
            "template_literals": len(re.findall(r'`[^`]*`', text)),
            "const_declarations": len(re.findall(r'\bconst\s+', text)),
            "let_declarations": len(re.findall(r'\blet\s+', text)),
            "destructuring": len(re.findall(r'{\s*\w+[^}]*}\s*=', text)),
            "spread_operator": len(re.findall(r'\.\.\.', text))
        }
        
        data["modern_features"] = modern_features
        modern_feature_count = sum(1 for count in modern_features.values() if count > 0)
        data["modern_syntax_score"] = min(modern_feature_count / 6, 1.0)
        
        # Calculate complexity
        complexity_indicators = [
            text.count('if '),
            text.count('for '),
            text.count('while '),
            text.count('switch '),
            text.count('try '),
            text.count('catch '),
        ]
        complexity = sum(complexity_indicators)
        data["complexity_score"] = min(complexity / (data["line_count"] * 0.1), 1.0)
        
        # Comments and documentation
        single_comments = len(re.findall(r'//.*', text))
        multi_comments = len(re.findall(r'/\*.*?\*/', text, re.DOTALL))
        data["comment_count"] = single_comments + multi_comments
        
        # Structure quality
        structure_score = 0.5
        if data.get("function_count", 0) > 0:
            structure_score += 0.2
        if data.get("class_count", 0) > 0:
            structure_score += 0.2
        if data.get("modern_syntax_score", 0) > 0.3:
            structure_score += 0.1
        data["structure_quality"] = min(structure_score, 1.0)
        
        return data

class SQLHandler(DocumentHandler):
    """Handler for SQL script files"""
    
    handler_type = "code"
    supported_types = ["SQL", "Structured Query Language"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith('.sql'):
            return True, 0.95
        if mime_type == 'application/sql':
            return True, 0.95
        
        # Check for SQL keywords
        try:
            text = content.decode('utf-8', errors='ignore').upper()[:1000]
            sql_keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
            keyword_matches = sum(1 for keyword in sql_keywords if keyword in text)
            if keyword_matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        # Try to detect SQL variant
        try:
            text = content.decode('utf-8', errors='ignore').upper()
            if 'MYSQL' in text or 'ENGINE=' in text:
                variant = "MySQL"
            elif 'POSTGRESQL' in text or 'SERIAL' in text:
                variant = "PostgreSQL"
            elif 'SQLSERVER' in text or 'IDENTITY(' in text:
                variant = "SQL Server"
            elif 'ORACLE' in text or 'ROWNUM' in text:
                variant = "Oracle"
            else:
                variant = "Generic SQL"
        except:
            variant = "Generic SQL"
        
        return DocumentTypeInfo(
            type_name="SQL Script",
            confidence=0.95,
            category="code",
            version=variant,
            subtype="database",
            language="sql"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="SQL Script",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Database schema analysis",
                "Query optimization recommendations",
                "Performance tuning",
                "Security vulnerability scanning",
                "Data migration planning",
                "Database documentation generation",
                "Query pattern analysis",
                "Index recommendation",
                "Data quality assessment",
                "ETL process optimization"
            ],
            quality_metrics={
                "query_complexity": findings.get("complexity_score", 0.5),
                "schema_quality": findings.get("schema_quality", 0.7),
                "documentation_score": findings.get("documentation_score", 0.3),
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
            "format": "SQL",
            "line_count": text.count('\n') + 1
        }
        
        # Count different types of SQL statements
        text_upper = text.upper()
        
        statement_counts = {
            "SELECT": len(re.findall(r'\bSELECT\b', text_upper)),
            "INSERT": len(re.findall(r'\bINSERT\s+INTO\b', text_upper)),
            "UPDATE": len(re.findall(r'\bUPDATE\b', text_upper)),
            "DELETE": len(re.findall(r'\bDELETE\s+FROM\b', text_upper)),
            "CREATE": len(re.findall(r'\bCREATE\s+(TABLE|VIEW|INDEX|PROCEDURE|FUNCTION)\b', text_upper)),
            "ALTER": len(re.findall(r'\bALTER\s+TABLE\b', text_upper)),
            "DROP": len(re.findall(r'\bDROP\s+(TABLE|VIEW|INDEX|PROCEDURE|FUNCTION)\b', text_upper))
        }
        
        data["statement_counts"] = statement_counts
        data["total_statements"] = sum(statement_counts.values())
        
        # Extract table names
        table_patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'CREATE\s+TABLE\s+(\w+)',
            r'ALTER\s+TABLE\s+(\w+)',
            r'DROP\s+TABLE\s+(\w+)'
        ]
        
        tables = set()
        for pattern in table_patterns:
            tables.update(re.findall(pattern, text_upper))
        
        data["table_count"] = len(tables)
        data["table_names"] = list(tables)[:20]
        
        # Count functions and procedures
        functions = re.findall(r'CREATE\s+(FUNCTION|PROCEDURE)\s+(\w+)', text_upper)
        data["function_procedure_count"] = len(functions)
        if functions:
            data["function_procedure_names"] = [f[1] for f in functions[:10]]
        
        # Calculate complexity based on joins, subqueries, etc.
        complexity_factors = {
            "joins": len(re.findall(r'\bJOIN\b', text_upper)),
            "subqueries": text.count('(') - text.count(')'),  # Rough estimate
            "unions": len(re.findall(r'\bUNION\b', text_upper)),
            "case_statements": len(re.findall(r'\bCASE\b', text_upper)),
            "window_functions": len(re.findall(r'\bOVER\s*\(', text_upper))
        }
        
        data["complexity_factors"] = complexity_factors
        complexity_score = min(sum(complexity_factors.values()) / (data["line_count"] * 0.1), 1.0)
        data["complexity_score"] = complexity_score
        
        # Documentation analysis
        comment_lines = len(re.findall(r'^\s*--', text, re.MULTILINE))
        block_comments = len(re.findall(r'/\*.*?\*/', text, re.DOTALL))
        data["comment_line_count"] = comment_lines
        data["block_comment_count"] = block_comments
        
        doc_score = (comment_lines + block_comments * 3) / data["line_count"] if data["line_count"] > 0 else 0
        data["documentation_score"] = min(doc_score, 1.0)
        
        # Schema quality assessment
        schema_indicators = statement_counts.get("CREATE", 0) + statement_counts.get("ALTER", 0)
        data["schema_quality"] = min(schema_indicators / max(data["table_count"], 1), 1.0) if data["table_count"] > 0 else 0.5
        
        return data

class JavaHandler(DocumentHandler):
    """Handler for Java source code files"""
    
    handler_type = "code"
    supported_types = ["Java", "Java Source"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith('.java'):
            return True, 0.95
        if mime_type == 'text/x-java':
            return True, 0.95
        
        # Check for Java-specific patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:1000]
            java_patterns = [
                r'public\s+class\s+\w+',
                r'import\s+[\w\.]+;',
                r'package\s+[\w\.]+;',
                r'public\s+static\s+void\s+main',
                r'@\w+',  # Annotations
            ]
            matches = sum(1 for pattern in java_patterns if re.search(pattern, text))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="Java Source",
            confidence=0.95,
            category="code",
            subtype="source_code",
            language="java"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Java Source",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Code analysis and quality assessment",
                "Automated code review",
                "Dependency analysis",
                "Security vulnerability scanning",
                "Code documentation generation",
                "Refactoring suggestions",
                "Design pattern detection",
                "Performance optimization recommendations",
                "Enterprise architecture analysis",
                "Spring framework analysis"
            ],
            quality_metrics={
                "code_complexity": findings.get("complexity_score", 0.5),
                "documentation_score": findings.get("documentation_score", 0.3),
                "structure_quality": findings.get("structure_quality", 0.7),
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
            "format": "Java",
            "line_count": text.count('\n') + 1
        }
        
        # Extract package
        package_match = re.search(r'package\s+([\w\.]+);', text)
        if package_match:
            data["package"] = package_match.group(1)
        
        # Extract imports
        imports = re.findall(r'import\s+([\w\.]+);', text)
        data["import_count"] = len(imports)
        data["imported_packages"] = list(set(imports))[:20]
        
        # Extract classes
        classes = re.findall(r'(?:public\s+|private\s+|protected\s+)?class\s+(\w+)', text)
        data["class_count"] = len(classes)
        data["class_names"] = classes[:10]
        
        # Extract methods
        methods = re.findall(r'(?:public\s+|private\s+|protected\s+|static\s+)*\w+\s+(\w+)\s*\([^)]*\)\s*\{', text)
        data["method_count"] = len(methods)
        data["method_names"] = methods[:20]
        
        # Extract annotations
        annotations = re.findall(r'@(\w+)', text)
        data["annotation_count"] = len(annotations)
        data["annotations"] = list(set(annotations))[:10]
        
        # Analyze comments
        single_comments = len(re.findall(r'//.*', text))
        multi_comments = len(re.findall(r'/\*.*?\*/', text, re.DOTALL))
        data["comment_count"] = single_comments + multi_comments
        
        # Calculate complexity
        complexity_indicators = [
            text.count('if '),
            text.count('for '),
            text.count('while '),
            text.count('switch '),
            text.count('try '),
            text.count('catch '),
        ]
        complexity = sum(complexity_indicators)
        data["complexity_score"] = min(complexity / (data["line_count"] * 0.1), 1.0)
        
        # Documentation score
        javadoc_comments = len(re.findall(r'/\*\*.*?\*/', text, re.DOTALL))
        doc_score = (javadoc_comments * 5 + data["comment_count"]) / data["line_count"] if data["line_count"] > 0 else 0
        data["documentation_score"] = min(doc_score, 1.0)
        
        # Structure quality
        structure_score = 0.5
        if data.get("class_count", 0) > 0:
            structure_score += 0.2
        if data.get("method_count", 0) > 0:
            structure_score += 0.2
        if data.get("documentation_score", 0) > 0.1:
            structure_score += 0.1
        data["structure_quality"] = min(structure_score, 1.0)
        
        return data

class CppHandler(DocumentHandler):
    """Handler for C++ source code files"""
    
    handler_type = "code"
    supported_types = ["C++", "C++ Source", "C Header"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.lower().endswith(('.cpp', '.cxx', '.cc', '.hpp', '.h')):
            return True, 0.95
        if mime_type in ['text/x-c++src', 'text/x-c++hdr', 'text/x-chdr']:
            return True, 0.95
        
        # Check for C++ patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:1000]
            cpp_patterns = [
                r'#include\s*[<"][\w\/\.]+[>"]',
                r'namespace\s+\w+',
                r'class\s+\w+',
                r'std::\w+',
                r'using\s+namespace',
                r'template\s*<.*>',
            ]
            matches = sum(1 for pattern in cpp_patterns if re.search(pattern, text))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.hpp', '.h']:
            subtype = "header"
        else:
            subtype = "source"
        
        return DocumentTypeInfo(
            type_name="C++ Source",
            confidence=0.95,
            category="code",
            subtype=subtype,
            language="cpp"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="C++ Source",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Code analysis and optimization",
                "Memory leak detection",
                "Performance optimization",
                "Security vulnerability scanning",
                "Code modernization (C++11/14/17/20)",
                "Template metaprogramming analysis",
                "System-level programming assistance",
                "Cross-platform compatibility analysis",
                "Build system optimization",
                "Legacy code migration"
            ],
            quality_metrics={
                "code_complexity": findings.get("complexity_score", 0.5),
                "modern_cpp_usage": findings.get("modern_cpp_score", 0.3),
                "structure_quality": findings.get("structure_quality", 0.7),
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
            "format": "C++",
            "line_count": text.count('\n') + 1,
            "is_header": Path(file_path).suffix.lower() in ['.hpp', '.h']
        }
        
        # Extract includes
        includes = re.findall(r'#include\s*[<"]([\w\/\.]+)[>"]', text)
        data["include_count"] = len(includes)
        data["includes"] = includes[:20]
        
        # Count system vs local includes
        system_includes = [inc for inc in includes if not inc.startswith('.')]
        data["system_includes"] = len(system_includes)
        data["local_includes"] = len(includes) - len(system_includes)
        
        # Extract namespaces
        namespaces = re.findall(r'namespace\s+(\w+)', text)
        data["namespace_count"] = len(set(namespaces))
        data["namespaces"] = list(set(namespaces))[:10]
        
        # Extract classes
        classes = re.findall(r'class\s+(\w+)', text)
        data["class_count"] = len(classes)
        data["class_names"] = classes[:10]
        
        # Extract functions
        functions = re.findall(r'(?:inline\s+|virtual\s+|static\s+)*\w+\s+(\w+)\s*\([^)]*\)\s*(?:\{|;)', text)
        data["function_count"] = len(functions)
        data["function_names"] = functions[:20]
        
        # Modern C++ features
        modern_features = {
            "auto_keyword": text.count('auto '),
            "range_based_for": len(re.findall(r'for\s*\(\s*[\w&]+\s*:\s*', text)),
            "lambda_expressions": text.count('[]'),
            "smart_pointers": len(re.findall(r'std::(unique_ptr|shared_ptr|weak_ptr)', text)),
            "templates": len(re.findall(r'template\s*<.*>', text)),
        }
        
        data["modern_features"] = modern_features
        modern_feature_count = sum(1 for count in modern_features.values() if count > 0)
        data["modern_cpp_score"] = min(modern_feature_count / 5, 1.0)
        
        # Comments
        single_comments = len(re.findall(r'//.*', text))
        multi_comments = len(re.findall(r'/\*.*?\*/', text, re.DOTALL))
        data["comment_count"] = single_comments + multi_comments
        
        # Calculate complexity
        complexity_indicators = [
            text.count('if '),
            text.count('for '),
            text.count('while '),
            text.count('switch '),
            text.count('try '),
            text.count('catch '),
        ]
        complexity = sum(complexity_indicators)
        data["complexity_score"] = min(complexity / (data["line_count"] * 0.1), 1.0)
        
        # Structure quality
        structure_score = 0.5
        if data.get("class_count", 0) > 0:
            structure_score += 0.2
        if data.get("function_count", 0) > 0:
            structure_score += 0.2
        if data.get("modern_cpp_score", 0) > 0.3:
            structure_score += 0.1
        data["structure_quality"] = min(structure_score, 1.0)
        
        return data