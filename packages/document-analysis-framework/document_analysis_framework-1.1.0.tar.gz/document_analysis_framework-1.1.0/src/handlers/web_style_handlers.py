"""
Web stylesheet handlers for CSS and SCSS files

Handles analysis of web stylesheets including CSS and SCSS/Sass files.
Focuses on structure, selectors, properties, and best practices.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class CSSHandler(DocumentHandler):
    """
    Handler for CSS (Cascading Style Sheets) files.
    
    Analyzes CSS structure, selectors, properties, and identifies
    patterns useful for AI-assisted web development and optimization.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the CSS file."""
        if file_path.endswith('.css'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # CSS patterns
            if any(pattern in text for pattern in [
                '{', '}', ':', ';',  # Basic CSS syntax
                'color:', 'font-', 'margin:', 'padding:',  # Common properties
                '.', '#', '@media', '@import'  # Selectors and at-rules
            ]):
                css_score = len(re.findall(r'[.#]\w+\s*{', text)) / 10
                return True, min(0.8 + css_score, 0.9)
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect specific CSS type and framework."""
        text = content.decode('utf-8', errors='ignore')
        
        # Detect CSS framework/library
        framework = None
        if 'bootstrap' in text.lower() or '.btn-' in text or '.col-' in text:
            framework = "Bootstrap"
        elif 'tailwind' in text.lower() or any(cls in text for cls in ['.flex', '.grid', '.p-', '.m-']):
            framework = "Tailwind"
        elif 'bulma' in text.lower() or '.column.is-' in text:
            framework = "Bulma"
        elif 'foundation' in text.lower():
            framework = "Foundation"
        
        return DocumentTypeInfo(
            type_name="CSS Stylesheet",
            confidence=0.95,
            category="web",
            format="css",
            framework=framework
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed CSS analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="CSS",
            category="web",
            key_findings=findings,
            ai_use_cases=[
                "CSS optimization and minification",
                "Selector refactoring",
                "Responsive design analysis",
                "Performance optimization",
                "Design system extraction",
                "Accessibility improvements"
            ],
            quality_metrics={
                "specificity_score": self._calculate_specificity_score(findings),
                "organization": self._assess_organization(findings),
                "performance": self._assess_performance(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract key CSS data and patterns."""
        text = content.decode('utf-8', errors='ignore')
        
        # Remove comments for analysis
        text_no_comments = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        return {
            "selectors": self._extract_selectors(text_no_comments),
            "properties": self._extract_properties(text_no_comments),
            "at_rules": self._extract_at_rules(text_no_comments),
            "media_queries": self._extract_media_queries(text),
            "variables": self._extract_css_variables(text_no_comments),
            "colors": self._extract_colors(text_no_comments),
            "fonts": self._extract_fonts(text_no_comments),
            "animations": self._extract_animations(text_no_comments),
            "imports": self._extract_imports(text),
            "rule_count": len(re.findall(r'{[^}]+}', text_no_comments)),
            "file_size_bytes": len(content),
            "comments": len(re.findall(r'/\*.*?\*/', text, re.DOTALL))
        }
    
    def _extract_selectors(self, text: str) -> Dict[str, int]:
        """Extract and categorize CSS selectors."""
        selectors = {
            "class_selectors": len(re.findall(r'\.\w+(?:-\w+)*', text)),
            "id_selectors": len(re.findall(r'#\w+(?:-\w+)*', text)),
            "element_selectors": len(re.findall(r'(?:^|\s)(?:div|span|p|a|img|h[1-6]|ul|li|table|form|input|button)\s*[{,]', text)),
            "attribute_selectors": len(re.findall(r'\[[^\]]+\]', text)),
            "pseudo_classes": len(re.findall(r':\w+(?:-\w+)*(?:\([^)]*\))?', text)),
            "pseudo_elements": len(re.findall(r'::\w+(?:-\w+)*', text)),
            "combinators": len(re.findall(r'[>+~]', text))
        }
        return selectors
    
    def _extract_properties(self, text: str) -> Dict[str, int]:
        """Extract CSS properties by category."""
        properties = {}
        
        # Common property categories
        categories = {
            "layout": ['display', 'position', 'float', 'flex', 'grid', 'width', 'height'],
            "spacing": ['margin', 'padding', 'gap'],
            "typography": ['font', 'text-', 'line-height', 'letter-spacing'],
            "colors": ['color', 'background', 'border-color'],
            "effects": ['transform', 'transition', 'animation', 'opacity', 'filter'],
            "borders": ['border', 'border-radius', 'outline']
        }
        
        for category, props in categories.items():
            count = 0
            for prop in props:
                count += len(re.findall(rf'{prop}[^:]*:', text))
            properties[category] = count
        
        return properties
    
    def _extract_at_rules(self, text: str) -> List[str]:
        """Extract CSS at-rules."""
        at_rules = re.findall(r'@(\w+)', text)
        return list(set(at_rules))
    
    def _extract_media_queries(self, text: str) -> List[Dict[str, str]]:
        """Extract media queries with their conditions."""
        queries = []
        for match in re.finditer(r'@media\s*([^{]+)\s*{', text):
            condition = match.group(1).strip()
            queries.append({
                "condition": condition,
                "type": self._classify_media_query(condition)
            })
        return queries
    
    def _classify_media_query(self, condition: str) -> str:
        """Classify media query type."""
        if 'min-width' in condition or 'max-width' in condition:
            return "responsive"
        elif 'print' in condition:
            return "print"
        elif 'prefers-' in condition:
            return "preference"
        else:
            return "other"
    
    def _extract_css_variables(self, text: str) -> List[str]:
        """Extract CSS custom properties (variables)."""
        variables = re.findall(r'--[\w-]+', text)
        return list(set(variables))
    
    def _extract_colors(self, text: str) -> Dict[str, List[str]]:
        """Extract color values by type."""
        colors = {
            "hex": re.findall(r'#[0-9a-fA-F]{3,8}', text),
            "rgb": re.findall(r'rgba?\([^)]+\)', text),
            "hsl": re.findall(r'hsla?\([^)]+\)', text),
            "named": re.findall(r':\s*(red|blue|green|yellow|black|white|gray|grey)\s*[;}]', text)
        }
        
        # Deduplicate
        for key in colors:
            colors[key] = list(set(colors[key]))[:20]  # Limit to 20 unique values
        
        return colors
    
    def _extract_fonts(self, text: str) -> List[str]:
        """Extract font families."""
        fonts = []
        for match in re.finditer(r'font-family:\s*([^;]+);', text):
            font_list = match.group(1)
            # Split by comma and clean
            for font in font_list.split(','):
                font = font.strip().strip('"\'')
                if font and font not in ['inherit', 'initial', 'unset']:
                    fonts.append(font)
        
        return list(set(fonts))
    
    def _extract_animations(self, text: str) -> Dict[str, int]:
        """Extract animation-related properties."""
        return {
            "keyframes": len(re.findall(r'@keyframes\s+\w+', text)),
            "animations": len(re.findall(r'animation:\s*[^;]+;', text)),
            "transitions": len(re.findall(r'transition:\s*[^;]+;', text)),
            "transforms": len(re.findall(r'transform:\s*[^;]+;', text))
        }
    
    def _extract_imports(self, text: str) -> List[str]:
        """Extract @import statements."""
        imports = []
        for match in re.finditer(r'@import\s+(?:url\()?["\']([^"\']+)["\']', text):
            imports.append(match.group(1))
        return imports
    
    def _calculate_specificity_score(self, findings: Dict[str, Any]) -> float:
        """Calculate CSS specificity score (lower is better)."""
        selectors = findings.get('selectors', {})
        
        # ID selectors have highest specificity (bad for maintainability)
        id_weight = selectors.get('id_selectors', 0) * 3
        # Complex selectors
        combinator_weight = selectors.get('combinators', 0) * 2
        # Class selectors (good balance)
        class_weight = selectors.get('class_selectors', 0) * 1
        
        total_selectors = sum(selectors.values())
        if total_selectors == 0:
            return 0.5
        
        # Lower score is better (less specific)
        specificity = (id_weight + combinator_weight) / total_selectors
        return max(0, 1 - specificity)
    
    def _assess_organization(self, findings: Dict[str, Any]) -> float:
        """Assess CSS organization and structure."""
        score = 0.5
        
        # Using CSS variables is good
        if findings.get('variables'):
            score += 0.2
        
        # Media queries indicate responsive design
        if findings.get('media_queries'):
            score += 0.1
        
        # Reasonable number of rules
        rule_count = findings.get('rule_count', 0)
        if 50 <= rule_count <= 500:
            score += 0.1
        
        # Using imports for modularization
        if findings.get('imports'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_performance(self, findings: Dict[str, Any]) -> float:
        """Assess CSS performance considerations."""
        score = 0.5
        
        # File size check
        size_bytes = findings.get('file_size_bytes', 0)
        if size_bytes < 50000:  # Under 50KB
            score += 0.2
        elif size_bytes < 100000:  # Under 100KB
            score += 0.1
        
        # Too many animations can impact performance
        animations = findings.get('animations', {})
        total_animations = sum(animations.values())
        if total_animations < 10:
            score += 0.1
        
        # Complex selectors impact performance
        selectors = findings.get('selectors', {})
        if selectors.get('attribute_selectors', 0) < 20:
            score += 0.1
        
        # Too many rules
        if findings.get('rule_count', 0) < 1000:
            score += 0.1
        
        return min(score, 1.0)


class SCSSHandler(DocumentHandler):
    """
    Handler for SCSS (Sassy CSS) files.
    
    Analyzes SCSS-specific features like variables, mixins, nesting,
    and inheritance in addition to standard CSS analysis.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the SCSS file."""
        if file_path.endswith(('.scss', '.sass')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # SCSS-specific patterns
            if any(pattern in text for pattern in [
                '$', '@mixin', '@include', '@extend', '@import',
                '&:', '#{', '@if', '@for', '@each'
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect SCSS variant and features."""
        is_sass = file_path.endswith('.sass')
        
        return DocumentTypeInfo(
            type_name="Sass Stylesheet" if is_sass else "SCSS Stylesheet",
            confidence=0.95,
            category="web",
            format="sass" if is_sass else "scss"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed SCSS analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="SCSS",
            category="web",
            key_findings=findings,
            ai_use_cases=[
                "SCSS to CSS compilation optimization",
                "Mixin and function refactoring",
                "Variable organization",
                "Nesting optimization",
                "Design token extraction",
                "Component style generation"
            ],
            quality_metrics={
                "modularity": self._assess_modularity(findings),
                "nesting_depth": self._assess_nesting(findings),
                "reusability": self._assess_reusability(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract SCSS-specific features and patterns."""
        text = content.decode('utf-8', errors='ignore')
        
        # Also extract standard CSS data
        css_handler = CSSHandler()
        css_data = css_handler.extract_key_data(file_path, content)
        
        # SCSS-specific extractions
        scss_data = {
            "variables": self._extract_variables(text),
            "mixins": self._extract_mixins(text),
            "functions": self._extract_functions(text),
            "extends": self._extract_extends(text),
            "imports": self._extract_imports(text),
            "uses": self._extract_uses(text),
            "nesting_levels": self._analyze_nesting(text),
            "control_directives": self._extract_control_directives(text),
            "interpolations": len(re.findall(r'#\{[^}]+\}', text)),
            "placeholder_selectors": len(re.findall(r'%\w+', text))
        }
        
        # Merge CSS and SCSS data
        return {**css_data, **scss_data}
    
    def _extract_variables(self, text: str) -> Dict[str, Any]:
        """Extract SCSS variables and categorize them."""
        variables = []
        variable_types = {
            "colors": 0,
            "dimensions": 0,
            "fonts": 0,
            "other": 0
        }
        
        for match in re.finditer(r'\$([a-zA-Z_-][\w-]*)\s*:\s*([^;]+);', text):
            var_name = match.group(1)
            var_value = match.group(2).strip()
            
            variables.append({
                "name": var_name,
                "value": var_value[:50]  # Truncate long values
            })
            
            # Categorize
            if any(color in var_name.lower() for color in ['color', 'bg', 'background', 'border']):
                variable_types["colors"] += 1
            elif any(dim in var_name.lower() for dim in ['width', 'height', 'size', 'margin', 'padding']):
                variable_types["dimensions"] += 1
            elif 'font' in var_name.lower():
                variable_types["fonts"] += 1
            else:
                variable_types["other"] += 1
        
        return {
            "list": variables[:20],  # Limit to first 20
            "total": len(variables),
            "types": variable_types
        }
    
    def _extract_mixins(self, text: str) -> List[Dict[str, Any]]:
        """Extract mixin definitions."""
        mixins = []
        
        for match in re.finditer(r'@mixin\s+([a-zA-Z_-][\w-]*)(?:\(([^)]*)\))?', text):
            mixin_name = match.group(1)
            params = match.group(2) or ""
            
            mixins.append({
                "name": mixin_name,
                "params": [p.strip() for p in params.split(',') if p.strip()],
                "has_params": bool(params.strip())
            })
        
        return mixins
    
    def _extract_functions(self, text: str) -> List[Dict[str, str]]:
        """Extract SCSS function definitions."""
        functions = []
        
        for match in re.finditer(r'@function\s+([a-zA-Z_-][\w-]*)(?:\(([^)]*)\))?', text):
            functions.append({
                "name": match.group(1),
                "params": match.group(2) or ""
            })
        
        return functions
    
    def _extract_extends(self, text: str) -> List[str]:
        """Extract @extend usage."""
        extends = re.findall(r'@extend\s+([^;]+);', text)
        return list(set(extends))
    
    def _extract_imports(self, text: str) -> List[str]:
        """Extract @import statements."""
        imports = []
        for match in re.finditer(r'@import\s+["\']([^"\']+)["\']', text):
            imports.append(match.group(1))
        return imports
    
    def _extract_uses(self, text: str) -> List[str]:
        """Extract @use statements (Sass modules)."""
        uses = []
        for match in re.finditer(r'@use\s+["\']([^"\']+)["\']', text):
            uses.append(match.group(1))
        return uses
    
    def _analyze_nesting(self, text: str) -> Dict[str, int]:
        """Analyze nesting depth in SCSS."""
        # Simple approximation of nesting depth
        max_depth = 0
        current_depth = 0
        depths = []
        
        for char in text:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                depths.append(current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        avg_depth = sum(depths) / len(depths) if depths else 0
        
        return {
            "max_depth": max_depth,
            "average_depth": round(avg_depth, 2),
            "deeply_nested": sum(1 for d in depths if d > 3)
        }
    
    def _extract_control_directives(self, text: str) -> Dict[str, int]:
        """Extract SCSS control directives."""
        return {
            "@if": len(re.findall(r'@if\s+', text)),
            "@else": len(re.findall(r'@else', text)),
            "@for": len(re.findall(r'@for\s+', text)),
            "@each": len(re.findall(r'@each\s+', text)),
            "@while": len(re.findall(r'@while\s+', text))
        }
    
    def _assess_modularity(self, findings: Dict[str, Any]) -> float:
        """Assess SCSS modularity and organization."""
        score = 0.5
        
        # Using variables
        if findings.get('variables', {}).get('total', 0) > 10:
            score += 0.15
        
        # Using mixins
        if findings.get('mixins'):
            score += 0.15
        
        # Using imports/uses for modularization
        if findings.get('imports') or findings.get('uses'):
            score += 0.1
        
        # Using functions
        if findings.get('functions'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_nesting(self, findings: Dict[str, Any]) -> float:
        """Assess nesting quality (too deep is bad)."""
        nesting = findings.get('nesting_levels', {})
        max_depth = nesting.get('max_depth', 0)
        
        if max_depth <= 3:
            return 1.0
        elif max_depth <= 5:
            return 0.7
        else:
            return max(0.3, 1.0 - (max_depth - 5) * 0.1)
    
    def _assess_reusability(self, findings: Dict[str, Any]) -> float:
        """Assess code reusability through SCSS features."""
        score = 0.5
        
        # Mixins with parameters are highly reusable
        mixins = findings.get('mixins', [])
        param_mixins = sum(1 for m in mixins if m.get('has_params'))
        if param_mixins > 0:
            score += min(0.2, param_mixins * 0.05)
        
        # Placeholder selectors for extending
        if findings.get('placeholder_selectors', 0) > 0:
            score += 0.1
        
        # Functions for calculations
        if findings.get('functions'):
            score += 0.1
        
        # Good variable usage
        variables = findings.get('variables', {})
        if variables.get('total', 0) > 20:
            score += 0.1
        
        return min(score, 1.0) 