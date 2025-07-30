"""
Extended code handlers for additional programming languages
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class TypeScriptHandler(DocumentHandler):
    """Handler for TypeScript files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith(('.ts', '.tsx')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # TypeScript-specific patterns
            if any(pattern in text for pattern in [
                'interface ', 'type ', ': string', ': number', ': boolean',
                'export default', 'import {', 'const:', 'let:', 'var:',
                'React.FC', 'JSX.Element', '<>', '</>'
            ]):
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        is_tsx = file_path.endswith('.tsx')
        
        return DocumentTypeInfo(
            type_name="TypeScript React Component" if is_tsx else "TypeScript Module",
            confidence=0.95,
            category="code",
            language="typescript",
            framework="React" if is_tsx else None
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        text = content.decode('utf-8', errors='ignore')
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="TypeScript",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Type system analysis and improvement",
                "React component optimization",
                "Code refactoring with type safety",
                "API interface generation",
                "Documentation from types"
            ],
            quality_metrics={
                "type_coverage": self._estimate_type_coverage(text),
                "complexity": self._calculate_complexity(text),
                "ai_readiness": 0.95
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "interfaces": self._extract_interfaces(text),
            "types": self._extract_types(text),
            "imports": self._extract_imports(text),
            "exports": self._extract_exports(text),
            "react_components": self._extract_react_components(text),
            "decorators": self._extract_decorators(text),
            "async_functions": len(re.findall(r'async\s+\w+', text)),
            "generics": len(re.findall(r'<[A-Z]\w*>', text))
        }
    
    def _extract_interfaces(self, text: str) -> List[str]:
        return re.findall(r'interface\s+(\w+)', text)
    
    def _extract_types(self, text: str) -> List[str]:
        return re.findall(r'type\s+(\w+)\s*=', text)
    
    def _extract_imports(self, text: str) -> List[str]:
        imports = []
        for match in re.finditer(r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]', text):
            imports.append(match.group(1))
        return imports
    
    def _extract_exports(self, text: str) -> List[str]:
        return re.findall(r'export\s+(?:default\s+)?(?:class|function|const|interface|type)\s+(\w+)', text)
    
    def _extract_react_components(self, text: str) -> List[str]:
        components = []
        # Function components
        components.extend(re.findall(r'(?:export\s+)?(?:const|function)\s+(\w+):\s*React\.FC', text))
        # Class components
        components.extend(re.findall(r'class\s+(\w+)\s+extends\s+React\.Component', text))
        return components
    
    def _extract_decorators(self, text: str) -> List[str]:
        return re.findall(r'@(\w+)', text)
    
    def _estimate_type_coverage(self, text: str) -> float:
        # Simple heuristic: ratio of typed vs untyped declarations
        typed = len(re.findall(r':\s*\w+', text))
        untyped = len(re.findall(r'(?:const|let|var)\s+\w+\s*=', text))
        if typed + untyped == 0:
            return 0.0
        return typed / (typed + untyped)
    
    def _calculate_complexity(self, text: str) -> float:
        lines = text.split('\n')
        if not lines:
            return 0.0
        
        complexity_indicators = [
            r'if\s*\(', r'else\s*{', r'for\s*\(', r'while\s*\(',
            r'switch\s*\(', r'catch\s*\(', r'\?\s*.*\s*:'
        ]
        
        complexity_count = sum(
            len(re.findall(pattern, text))
            for pattern in complexity_indicators
        )
        
        return min(complexity_count / len(lines) * 10, 10.0)


class GoHandler(DocumentHandler):
    """Handler for Go files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.go'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            if text.startswith('package ') or 'func main()' in text:
                return True, 0.9
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if 'func main()' in text:
            type_name = "Go Main Package"
        elif 'func Test' in text:
            type_name = "Go Test File"
        else:
            type_name = "Go Package"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="code",
            language="go"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Go",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Goroutine optimization",
                "Error handling improvement",
                "Interface design",
                "Performance profiling suggestions",
                "Concurrent programming patterns"
            ],
            quality_metrics={
                "error_handling": self._assess_error_handling(content),
                "concurrency_usage": self._assess_concurrency(content),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "package": self._extract_package(text),
            "imports": self._extract_imports(text),
            "functions": self._extract_functions(text),
            "structs": self._extract_structs(text),
            "interfaces": self._extract_interfaces(text),
            "goroutines": len(re.findall(r'go\s+\w+', text)),
            "channels": len(re.findall(r'chan\s+', text)),
            "defer_statements": len(re.findall(r'defer\s+', text))
        }
    
    def _extract_package(self, text: str) -> str:
        match = re.search(r'package\s+(\w+)', text)
        return match.group(1) if match else "unknown"
    
    def _extract_imports(self, text: str) -> List[str]:
        imports = []
        import_block = re.search(r'import\s*\((.*?)\)', text, re.DOTALL)
        if import_block:
            for line in import_block.group(1).split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    imports.append(line.strip('"'))
        else:
            # Single imports
            imports.extend(re.findall(r'import\s+"([^"]+)"', text))
        return imports
    
    def _extract_functions(self, text: str) -> List[str]:
        return re.findall(r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)', text)
    
    def _extract_structs(self, text: str) -> List[str]:
        return re.findall(r'type\s+(\w+)\s+struct', text)
    
    def _extract_interfaces(self, text: str) -> List[str]:
        return re.findall(r'type\s+(\w+)\s+interface', text)
    
    def _assess_error_handling(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        error_checks = len(re.findall(r'if\s+err\s*!=\s*nil', text))
        function_calls = len(re.findall(r'\w+\(.*?\)', text))
        if function_calls == 0:
            return 0.0
        return min(error_checks / function_calls * 2, 1.0)
    
    def _assess_concurrency(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        goroutines = len(re.findall(r'go\s+', text))
        channels = len(re.findall(r'chan\s+', text))
        mutexes = len(re.findall(r'sync\.Mutex', text))
        
        if goroutines + channels + mutexes == 0:
            return 0.0
        return min((goroutines + channels + mutexes) / 10, 1.0)


class RustHandler(DocumentHandler):
    """Handler for Rust files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.rs'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            if any(pattern in text for pattern in ['fn main()', 'use std::', 'impl ', 'trait ']):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if 'fn main()' in text:
            type_name = "Rust Binary"
        elif '#[cfg(test)]' in text:
            type_name = "Rust Test Module"
        elif 'lib.rs' in file_path:
            type_name = "Rust Library"
        else:
            type_name = "Rust Module"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="code",
            language="rust"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Rust",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Memory safety analysis",
                "Lifetime annotation suggestions",
                "Error handling with Result type",
                "Performance optimization",
                "Unsafe code review"
            ],
            quality_metrics={
                "safety_score": self._assess_safety(content),
                "error_handling": self._assess_error_handling(content),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "modules": self._extract_modules(text),
            "functions": self._extract_functions(text),
            "structs": self._extract_structs(text),
            "enums": self._extract_enums(text),
            "traits": self._extract_traits(text),
            "impls": self._extract_impls(text),
            "macros": self._extract_macros(text),
            "unsafe_blocks": len(re.findall(r'unsafe\s*{', text)),
            "lifetimes": len(re.findall(r"'[a-z]\w*", text))
        }
    
    def _extract_modules(self, text: str) -> List[str]:
        return re.findall(r'mod\s+(\w+)', text)
    
    def _extract_functions(self, text: str) -> List[str]:
        return re.findall(r'fn\s+(\w+)', text)
    
    def _extract_structs(self, text: str) -> List[str]:
        return re.findall(r'struct\s+(\w+)', text)
    
    def _extract_enums(self, text: str) -> List[str]:
        return re.findall(r'enum\s+(\w+)', text)
    
    def _extract_traits(self, text: str) -> List[str]:
        return re.findall(r'trait\s+(\w+)', text)
    
    def _extract_impls(self, text: str) -> List[str]:
        return re.findall(r'impl\s+(?:<.*?>)?\s*(\w+)', text)
    
    def _extract_macros(self, text: str) -> List[str]:
        return re.findall(r'(\w+)!', text)
    
    def _assess_safety(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        unsafe_count = len(re.findall(r'unsafe\s*{', text))
        total_functions = len(re.findall(r'fn\s+', text))
        if total_functions == 0:
            return 1.0
        return max(0, 1.0 - (unsafe_count / total_functions))
    
    def _assess_error_handling(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        result_usage = len(re.findall(r'Result<', text))
        option_usage = len(re.findall(r'Option<', text))
        unwrap_usage = len(re.findall(r'\.unwrap\(\)', text))
        
        if result_usage + option_usage == 0:
            return 0.5
        
        # Penalize unwrap usage
        return max(0, 1.0 - (unwrap_usage / (result_usage + option_usage)))


class RubyHandler(DocumentHandler):
    """Handler for Ruby files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.rb'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            if text.startswith('#!/usr/bin/env ruby') or 'class ' in text or 'def ' in text:
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if 'Rails.application' in text or 'ActiveRecord' in text:
            type_name = "Ruby on Rails"
        elif '_spec.rb' in file_path or 'RSpec' in text:
            type_name = "Ruby RSpec Test"
        elif 'Gemfile' in file_path:
            type_name = "Ruby Gemfile"
        else:
            type_name = "Ruby Script"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="code",
            language="ruby",
            framework="Rails" if "Rails" in type_name else None
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Ruby",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Rails best practices",
                "Ruby idiom suggestions",
                "Performance optimization",
                "Test coverage improvement",
                "Metaprogramming analysis"
            ],
            quality_metrics={
                "ruby_style": self._assess_style(content),
                "test_presence": self._check_test_presence(content),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "classes": self._extract_classes(text),
            "modules": self._extract_modules(text),
            "methods": self._extract_methods(text),
            "gems": self._extract_gems(text),
            "attributes": self._extract_attributes(text),
            "blocks": len(re.findall(r'do\s*\|', text)),
            "symbols": len(re.findall(r':\w+', text))
        }
    
    def _extract_classes(self, text: str) -> List[str]:
        return re.findall(r'class\s+(\w+)', text)
    
    def _extract_modules(self, text: str) -> List[str]:
        return re.findall(r'module\s+(\w+)', text)
    
    def _extract_methods(self, text: str) -> List[str]:
        return re.findall(r'def\s+(\w+)', text)
    
    def _extract_gems(self, text: str) -> List[str]:
        gems = []
        gems.extend(re.findall(r"gem\s+['\"](\w+)['\"]", text))
        gems.extend(re.findall(r"require\s+['\"](\w+)['\"]", text))
        return list(set(gems))
    
    def _extract_attributes(self, text: str) -> List[str]:
        attrs = []
        attrs.extend(re.findall(r'attr_reader\s+:(\w+)', text))
        attrs.extend(re.findall(r'attr_writer\s+:(\w+)', text))
        attrs.extend(re.findall(r'attr_accessor\s+:(\w+)', text))
        return attrs
    
    def _assess_style(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        # Simple Ruby style indicators
        good_practices = [
            len(re.findall(r'\.each\s*do', text)),  # Iterators
            len(re.findall(r'&:\w+', text)),  # Symbol to proc
            len(re.findall(r'\|\|=', text)),  # Memoization
        ]
        
        bad_practices = [
            len(re.findall(r'for\s+\w+\s+in', text)),  # For loops
            len(re.findall(r'eval\s*\(', text)),  # Eval usage
        ]
        
        score = sum(good_practices) - sum(bad_practices) * 2
        return min(max(score / 10, 0), 1.0)
    
    def _check_test_presence(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        test_indicators = ['describe ', 'it ', 'expect(', 'assert_', 'test ']
        return 1.0 if any(indicator in text for indicator in test_indicators) else 0.0


class PHPHandler(DocumentHandler):
    """Handler for PHP files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.php'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            if '<?php' in text or '<?' in text:
                return True, 0.9
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if 'namespace ' in text and 'class ' in text:
            type_name = "PHP Class"
        elif 'Laravel' in text or 'Illuminate' in text:
            type_name = "Laravel PHP"
        elif 'WordPress' in text or 'wp_' in text:
            type_name = "WordPress PHP"
        else:
            type_name = "PHP Script"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="code",
            language="php",
            framework=self._detect_framework(text)
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="PHP",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Security vulnerability detection",
                "Modern PHP migration",
                "Framework best practices",
                "SQL injection prevention",
                "Performance optimization"
            ],
            quality_metrics={
                "security_score": self._assess_security(content),
                "modern_php": self._assess_modern_php(content),
                "ai_readiness": 0.8
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "namespaces": self._extract_namespaces(text),
            "classes": self._extract_classes(text),
            "functions": self._extract_functions(text),
            "traits": self._extract_traits(text),
            "interfaces": self._extract_interfaces(text),
            "uses": self._extract_uses(text),
            "global_vars": len(re.findall(r'\$GLOBALS', text)),
            "sql_queries": self._detect_sql_queries(text)
        }
    
    def _detect_framework(self, text: str) -> Optional[str]:
        frameworks = {
            'Laravel': ['Illuminate\\', 'Laravel\\'],
            'Symfony': ['Symfony\\', 'use Symfony'],
            'WordPress': ['wp_', 'add_action', 'add_filter'],
            'Drupal': ['drupal_', 'hook_'],
            'CodeIgniter': ['CI_Controller', '$this->load->']
        }
        
        for framework, patterns in frameworks.items():
            if any(pattern in text for pattern in patterns):
                return framework
        return None
    
    def _extract_namespaces(self, text: str) -> List[str]:
        return re.findall(r'namespace\s+([\w\\]+);', text)
    
    def _extract_classes(self, text: str) -> List[str]:
        return re.findall(r'class\s+(\w+)', text)
    
    def _extract_functions(self, text: str) -> List[str]:
        return re.findall(r'function\s+(\w+)', text)
    
    def _extract_traits(self, text: str) -> List[str]:
        return re.findall(r'trait\s+(\w+)', text)
    
    def _extract_interfaces(self, text: str) -> List[str]:
        return re.findall(r'interface\s+(\w+)', text)
    
    def _extract_uses(self, text: str) -> List[str]:
        return re.findall(r'use\s+([\w\\]+);', text)
    
    def _detect_sql_queries(self, text: str) -> int:
        sql_patterns = [
            r'SELECT\s+.*\s+FROM',
            r'INSERT\s+INTO',
            r'UPDATE\s+.*\s+SET',
            r'DELETE\s+FROM'
        ]
        return sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in sql_patterns)
    
    def _assess_security(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        
        vulnerabilities = [
            len(re.findall(r'\$_GET\[', text)),
            len(re.findall(r'\$_POST\[', text)),
            len(re.findall(r'eval\s*\(', text)),
            len(re.findall(r'exec\s*\(', text)),
            len(re.findall(r'system\s*\(', text))
        ]
        
        protections = [
            len(re.findall(r'htmlspecialchars', text)),
            len(re.findall(r'prepared\s+statement', text, re.IGNORECASE)),
            len(re.findall(r'bindParam', text))
        ]
        
        vuln_score = sum(vulnerabilities)
        prot_score = sum(protections)
        
        if vuln_score == 0:
            return 1.0
        return min(prot_score / vuln_score, 1.0)
    
    def _assess_modern_php(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        
        modern_features = [
            'declare(strict_types=1)' in text,
            'namespace ' in text,
            len(re.findall(r':\s*\??\w+\s*(?:\{|$)', text)) > 0,  # Type hints
            len(re.findall(r'->', text)) > len(re.findall(r'::', text)),  # OOP
            'use ' in text
        ]
        
        return sum(modern_features) / len(modern_features)


class ShellScriptHandler(DocumentHandler):
    """Handler for Shell scripts (bash, sh, zsh)"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith(('.sh', '.bash', '.zsh')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            if text.startswith('#!/bin/bash') or text.startswith('#!/bin/sh') or text.startswith('#!/usr/bin/env bash'):
                return True, 0.9
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        if '#!/bin/bash' in text or '.bash' in file_path:
            shell_type = "Bash"
        elif '#!/bin/zsh' in text or '.zsh' in file_path:
            shell_type = "Zsh"
        else:
            shell_type = "Shell"
        
        return DocumentTypeInfo(
            type_name=f"{shell_type} Script",
            confidence=0.95,
            category="code",
            language="shell"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Shell Script",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Script optimization",
                "Error handling improvement",
                "Security hardening",
                "POSIX compliance",
                "Cross-platform compatibility"
            ],
            quality_metrics={
                "error_handling": self._assess_error_handling(content),
                "security": self._assess_security(content),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "functions": self._extract_functions(text),
            "variables": self._extract_variables(text),
            "commands": self._extract_commands(text),
            "conditionals": len(re.findall(r'\bif\b.*\bthen\b', text)),
            "loops": self._count_loops(text),
            "pipelines": len(re.findall(r'\|', text)),
            "subshells": len(re.findall(r'\$\(', text)) + len(re.findall(r'`', text))
        }
    
    def _extract_functions(self, text: str) -> List[str]:
        # Bash function syntax
        functions = re.findall(r'function\s+(\w+)', text)
        functions.extend(re.findall(r'^(\w+)\s*\(\s*\)', text, re.MULTILINE))
        return list(set(functions))
    
    def _extract_variables(self, text: str) -> List[str]:
        return re.findall(r'^(\w+)=', text, re.MULTILINE)
    
    def _extract_commands(self, text: str) -> List[str]:
        # Common shell commands
        common_commands = ['echo', 'cd', 'ls', 'grep', 'sed', 'awk', 'find', 'curl', 'wget']
        found_commands = []
        for cmd in common_commands:
            if re.search(rf'\b{cmd}\b', text):
                found_commands.append(cmd)
        return found_commands
    
    def _count_loops(self, text: str) -> int:
        for_loops = len(re.findall(r'\bfor\b.*\bdo\b', text))
        while_loops = len(re.findall(r'\bwhile\b.*\bdo\b', text))
        until_loops = len(re.findall(r'\buntil\b.*\bdo\b', text))
        return for_loops + while_loops + until_loops
    
    def _assess_error_handling(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        
        error_handling = [
            len(re.findall(r'set\s+-e', text)),
            len(re.findall(r'\|\|\s*exit', text)),
            len(re.findall(r'trap\s+', text)),
            len(re.findall(r'\$\?', text))
        ]
        
        return min(sum(error_handling) / 10, 1.0)
    
    def _assess_security(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        
        vulnerabilities = [
            len(re.findall(r'eval\s+', text)),
            len(re.findall(r'\$\(.*\$', text)),  # Unquoted variables in command substitution
            text.count('rm -rf')
        ]
        
        good_practices = [
            'set -u' in text,  # Undefined variable check
            len(re.findall(r'"\$\{?\w+\}?"', text)),  # Quoted variables
            'set -o pipefail' in text
        ]
        
        vuln_score = sum(vulnerabilities)
        good_score = sum(1 for practice in good_practices if practice)
        
        if vuln_score == 0:
            return min(good_score / 3, 1.0)
        return max(0, (good_score - vuln_score) / 3)


class PowerShellHandler(DocumentHandler):
    """Handler for PowerShell scripts"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.ps1'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            if any(pattern in text for pattern in ['$PSVersionTable', 'Get-', 'Set-', 'New-']):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="PowerShell Script",
            confidence=0.95,
            category="code",
            language="powershell"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="PowerShell",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Cmdlet optimization",
                "Error handling with try-catch",
                "Pipeline efficiency",
                "Security best practices",
                "Cross-platform compatibility"
            ],
            quality_metrics={
                "cmdlet_usage": self._assess_cmdlet_usage(content),
                "error_handling": self._assess_error_handling(content),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "functions": self._extract_functions(text),
            "cmdlets": self._extract_cmdlets(text),
            "variables": self._extract_variables(text),
            "parameters": self._extract_parameters(text),
            "modules": self._extract_modules(text),
            "pipelines": text.count('|'),
            "error_handling": len(re.findall(r'try\s*{', text))
        }
    
    def _extract_functions(self, text: str) -> List[str]:
        return re.findall(r'function\s+(\w+-\w+)', text)
    
    def _extract_cmdlets(self, text: str) -> List[str]:
        return re.findall(r'(Get|Set|New|Remove|Add|Start|Stop|Restart)-\w+', text)
    
    def _extract_variables(self, text: str) -> List[str]:
        return re.findall(r'\$(\w+)\s*=', text)
    
    def _extract_parameters(self, text: str) -> List[str]:
        return re.findall(r'\[Parameter.*?\]\s*\$(\w+)', text)
    
    def _extract_modules(self, text: str) -> List[str]:
        modules = []
        modules.extend(re.findall(r'Import-Module\s+(\w+)', text))
        modules.extend(re.findall(r'using\s+module\s+(\w+)', text))
        return list(set(modules))
    
    def _assess_cmdlet_usage(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        cmdlet_count = len(self._extract_cmdlets(text))
        line_count = len(text.split('\n'))
        if line_count == 0:
            return 0.0
        return min(cmdlet_count / line_count * 5, 1.0)
    
    def _assess_error_handling(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        try_blocks = len(re.findall(r'try\s*{', text))
        catch_blocks = len(re.findall(r'catch\s*{', text))
        error_action = len(re.findall(r'-ErrorAction', text))
        
        score = (try_blocks + catch_blocks + error_action) / 10
        return min(score, 1.0) 