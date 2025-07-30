"""
Python package management handlers for Poetry and modern Python packaging

Handles analysis of pyproject.toml files for Poetry, setuptools, and other
modern Python packaging tools.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import toml
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class PyProjectHandler(DocumentHandler):
    """
    Handler for pyproject.toml files (PEP 517/518).
    
    Analyzes modern Python project configuration including Poetry,
    setuptools, and other build systems.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the pyproject.toml file."""
        if file_path.endswith('pyproject.toml'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Check for TOML structure with Python-specific sections
            if '[tool.poetry]' in text or '[project]' in text or '[build-system]' in text:
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Python packaging tool and configuration type."""
        text = content.decode('utf-8', errors='ignore')
        
        # Detect packaging tool
        if '[tool.poetry]' in text:
            type_name = "Poetry Project Configuration"
            tool = "Poetry"
        elif '[tool.setuptools]' in text:
            type_name = "Setuptools Project Configuration"
            tool = "Setuptools"
        elif '[tool.flit]' in text:
            type_name = "Flit Project Configuration"
            tool = "Flit"
        elif '[tool.hatch]' in text:
            type_name = "Hatch Project Configuration"
            tool = "Hatch"
        elif '[project]' in text:
            type_name = "PEP 621 Project Configuration"
            tool = "PEP 621"
        else:
            type_name = "Python Project Configuration"
            tool = "Unknown"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="config",
            format="pyproject",
            language="python"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed pyproject.toml analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="PyProject",
            category="config",
            key_findings=findings,
            ai_use_cases=[
                "Dependency update automation",
                "Security vulnerability scanning",
                "Package compatibility checking",
                "Build configuration optimization",
                "CI/CD pipeline generation",
                "Documentation generation"
            ],
            quality_metrics={
                "dependency_management": self._assess_dependency_management(findings),
                "project_metadata": self._assess_project_metadata(findings),
                "development_setup": self._assess_development_setup(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract pyproject.toml data."""
        text = content.decode('utf-8', errors='ignore')
        
        try:
            data = toml.loads(text)
        except Exception as e:
            return {"error": f"Failed to parse TOML: {str(e)}"}
        
        # Determine the packaging tool
        tool_type = self._determine_tool_type(data)
        
        analysis = {
            "tool_type": tool_type,
            "build_system": self._analyze_build_system(data.get('build-system', {})),
            "tools": list(data.get('tool', {}).keys())
        }
        
        # Analyze based on tool type
        if tool_type == "poetry":
            analysis.update(self._analyze_poetry(data))
        elif tool_type == "pep621":
            analysis.update(self._analyze_pep621(data))
        else:
            # Generic analysis
            analysis.update(self._analyze_generic(data))
        
        # Analyze tool-specific configurations
        analysis["tool_configs"] = self._analyze_tool_configs(data.get('tool', {}))
        
        return analysis
    
    def _determine_tool_type(self, data: Dict[str, Any]) -> str:
        """Determine which packaging tool is being used."""
        tool_section = data.get('tool', {})
        
        if 'poetry' in tool_section:
            return "poetry"
        elif 'project' in data:
            return "pep621"
        elif 'setuptools' in tool_section:
            return "setuptools"
        elif 'flit' in tool_section:
            return "flit"
        elif 'hatch' in tool_section:
            return "hatch"
        else:
            return "unknown"
    
    def _analyze_build_system(self, build_system: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze build-system section."""
        return {
            "requires": build_system.get('requires', []),
            "build_backend": build_system.get('build-backend', 'unknown'),
            "backend_path": build_system.get('backend-path', [])
        }
    
    def _analyze_poetry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Poetry-specific configuration."""
        poetry_config = data.get('tool', {}).get('poetry', {})
        
        analysis = {
            "project": self._extract_poetry_metadata(poetry_config),
            "dependencies": self._analyze_poetry_dependencies(poetry_config),
            "scripts": poetry_config.get('scripts', {}),
            "extras": list(poetry_config.get('extras', {}).keys()),
            "groups": self._analyze_dependency_groups(poetry_config),
            "urls": poetry_config.get('urls', {}),
            "packages": poetry_config.get('packages', []),
            "include": poetry_config.get('include', []),
            "exclude": poetry_config.get('exclude', [])
        }
        
        return analysis
    
    def _extract_poetry_metadata(self, poetry_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Poetry project metadata."""
        return {
            "name": poetry_config.get('name', 'unknown'),
            "version": poetry_config.get('version', '0.0.0'),
            "description": poetry_config.get('description', ''),
            "authors": poetry_config.get('authors', []),
            "maintainers": poetry_config.get('maintainers', []),
            "license": poetry_config.get('license', ''),
            "readme": poetry_config.get('readme', ''),
            "homepage": poetry_config.get('homepage', ''),
            "repository": poetry_config.get('repository', ''),
            "documentation": poetry_config.get('documentation', ''),
            "keywords": poetry_config.get('keywords', []),
            "classifiers": poetry_config.get('classifiers', []),
            "python_versions": poetry_config.get('python', '')
        }
    
    def _analyze_poetry_dependencies(self, poetry_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Poetry dependencies."""
        deps = poetry_config.get('dependencies', {})
        dev_deps = poetry_config.get('dev-dependencies', {})
        
        # Also check for dependency groups (Poetry 1.2+)
        groups = poetry_config.get('group', {})
        group_deps = {}
        for group_name, group_config in groups.items():
            if 'dependencies' in group_config:
                group_deps[group_name] = group_config['dependencies']
        
        return {
            "runtime": self._analyze_dependency_list(deps),
            "dev": self._analyze_dependency_list(dev_deps),
            "groups": {
                name: self._analyze_dependency_list(deps)
                for name, deps in group_deps.items()
            },
            "python_constraint": deps.get('python', ''),
            "total_runtime": len(deps) - 1 if 'python' in deps else len(deps),
            "total_dev": len(dev_deps),
            "total_groups": sum(len(d) for d in group_deps.values())
        }
    
    def _analyze_dependency_list(self, deps: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a dictionary of dependencies."""
        analysis = {
            "packages": [],
            "git_dependencies": 0,
            "path_dependencies": 0,
            "url_dependencies": 0,
            "extras_used": 0,
            "version_pinned": 0,
            "version_ranged": 0
        }
        
        for name, spec in deps.items():
            if name == 'python':
                continue
                
            dep_info = {
                "name": name,
                "spec": spec
            }
            
            if isinstance(spec, dict):
                # Complex dependency specification
                if 'git' in spec:
                    analysis['git_dependencies'] += 1
                    dep_info['type'] = 'git'
                elif 'path' in spec:
                    analysis['path_dependencies'] += 1
                    dep_info['type'] = 'path'
                elif 'url' in spec:
                    analysis['url_dependencies'] += 1
                    dep_info['type'] = 'url'
                else:
                    dep_info['type'] = 'version'
                    
                if 'extras' in spec:
                    analysis['extras_used'] += 1
                    
                version = spec.get('version', '')
            else:
                # Simple version string
                version = str(spec)
                dep_info['type'] = 'version'
            
            # Analyze version specification
            if version:
                if version.startswith('^') or version.startswith('~'):
                    analysis['version_ranged'] += 1
                elif ',' in version or '>' in version or '<' in version:
                    analysis['version_ranged'] += 1
                elif version == '*':
                    pass  # Unpinned
                else:
                    analysis['version_pinned'] += 1
            
            analysis['packages'].append(dep_info)
        
        return analysis
    
    def _analyze_dependency_groups(self, poetry_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Poetry dependency groups."""
        groups = poetry_config.get('group', {})
        
        group_analysis = {}
        for group_name, group_config in groups.items():
            group_analysis[group_name] = {
                "optional": group_config.get('optional', False),
                "dependency_count": len(group_config.get('dependencies', {}))
            }
        
        return group_analysis
    
    def _analyze_pep621(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PEP 621 project configuration."""
        project = data.get('project', {})
        
        analysis = {
            "project": {
                "name": project.get('name', 'unknown'),
                "version": project.get('version', '0.0.0'),
                "description": project.get('description', ''),
                "readme": project.get('readme', ''),
                "requires_python": project.get('requires-python', ''),
                "license": project.get('license', {}),
                "authors": project.get('authors', []),
                "maintainers": project.get('maintainers', []),
                "keywords": project.get('keywords', []),
                "classifiers": project.get('classifiers', []),
                "urls": project.get('urls', {}),
                "dynamic": project.get('dynamic', [])
            },
            "dependencies": self._analyze_pep621_dependencies(project),
            "scripts": project.get('scripts', {}),
            "gui_scripts": project.get('gui-scripts', {}),
            "entry_points": project.get('entry-points', {})
        }
        
        return analysis
    
    def _analyze_pep621_dependencies(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PEP 621 dependencies."""
        runtime_deps = project.get('dependencies', [])
        optional_deps = project.get('optional-dependencies', {})
        
        return {
            "runtime": {
                "packages": [self._parse_requirement(dep) for dep in runtime_deps],
                "total": len(runtime_deps)
            },
            "optional": {
                name: {
                    "packages": [self._parse_requirement(dep) for dep in deps],
                    "total": len(deps)
                }
                for name, deps in optional_deps.items()
            },
            "total_optional_groups": len(optional_deps)
        }
    
    def _parse_requirement(self, requirement: str) -> Dict[str, str]:
        """Parse a PEP 508 requirement string."""
        # Simple parser for requirement strings
        match = re.match(r'^([a-zA-Z0-9._-]+)(.*)$', requirement.strip())
        if match:
            name = match.group(1)
            spec = match.group(2).strip()
            return {"name": name, "spec": spec}
        return {"name": requirement, "spec": ""}
    
    def _analyze_generic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic analysis for unknown tool types."""
        return {
            "sections": list(data.keys()),
            "has_project_section": 'project' in data,
            "has_tool_section": 'tool' in data,
            "tool_count": len(data.get('tool', {}))
        }
    
    def _analyze_tool_configs(self, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tool-specific configurations."""
        tool_analysis = {}
        
        # Common tools to analyze
        common_tools = {
            'black': self._analyze_black_config,
            'isort': self._analyze_isort_config,
            'pytest': self._analyze_pytest_config,
            'mypy': self._analyze_mypy_config,
            'coverage': self._analyze_coverage_config,
            'ruff': self._analyze_ruff_config,
            'pylint': self._analyze_pylint_config
        }
        
        for tool_name, analyzer in common_tools.items():
            if tool_name in tools:
                tool_analysis[tool_name] = analyzer(tools[tool_name])
        
        # List other tools not specifically analyzed
        other_tools = [name for name in tools if name not in common_tools and name != 'poetry']
        if other_tools:
            tool_analysis['other_tools'] = other_tools
        
        return tool_analysis
    
    def _analyze_black_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Black formatter configuration."""
        return {
            "line_length": config.get('line-length', 88),
            "target_version": config.get('target-version', []),
            "skip_string_normalization": config.get('skip-string-normalization', False),
            "include": config.get('include'),
            "exclude": config.get('exclude')
        }
    
    def _analyze_isort_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze isort configuration."""
        return {
            "profile": config.get('profile', 'default'),
            "line_length": config.get('line_length'),
            "known_first_party": config.get('known_first_party', []),
            "sections": config.get('sections', [])
        }
    
    def _analyze_pytest_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pytest configuration."""
        return {
            "minversion": config.get('minversion'),
            "testpaths": config.get('testpaths', []),
            "python_files": config.get('python_files', []),
            "addopts": config.get('addopts', ''),
            "markers": list(config.get('markers', {}).keys()) if isinstance(config.get('markers'), dict) else []
        }
    
    def _analyze_mypy_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mypy configuration."""
        return {
            "python_version": config.get('python_version'),
            "warn_return_any": config.get('warn_return_any', False),
            "warn_unused_configs": config.get('warn_unused_configs', False),
            "disallow_untyped_defs": config.get('disallow_untyped_defs', False),
            "strict": config.get('strict', False),
            "files": config.get('files', []),
            "exclude": config.get('exclude', [])
        }
    
    def _analyze_coverage_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze coverage configuration."""
        return {
            "source": config.get('source', []),
            "omit": config.get('omit', []),
            "branch": config.get('branch', False),
            "report": config.get('report', {})
        }
    
    def _analyze_ruff_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Ruff linter configuration."""
        return {
            "line_length": config.get('line-length'),
            "select": config.get('select', []),
            "ignore": config.get('ignore', []),
            "target_version": config.get('target-version'),
            "exclude": config.get('exclude', [])
        }
    
    def _analyze_pylint_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Pylint configuration."""
        return {
            "disable": config.get('disable', []),
            "enable": config.get('enable', []),
            "max_line_length": config.get('max-line-length'),
            "ignore": config.get('ignore', [])
        }
    
    def _assess_dependency_management(self, findings: Dict[str, Any]) -> float:
        """Assess dependency management practices."""
        score = 0.5
        
        deps = findings.get('dependencies', {})
        
        # Has dependencies specified
        if deps:
            runtime = deps.get('runtime', {})
            
            # Version constraints used
            if runtime:
                if 'version_ranged' in runtime and runtime['version_ranged'] > 0:
                    score += 0.15
                elif 'version_pinned' in runtime and runtime['version_pinned'] > 0:
                    score += 0.1
            
            # Development dependencies separated
            if 'dev' in deps and deps['dev']:
                score += 0.1
            
            # Dependency groups used (Poetry)
            if 'groups' in deps and deps['groups']:
                score += 0.1
            
            # Optional dependencies (PEP 621)
            if 'optional' in deps and deps['optional']:
                score += 0.1
        
        # Python version specified
        project = findings.get('project', {})
        if project:
            if project.get('python_versions') or project.get('requires_python'):
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_project_metadata(self, findings: Dict[str, Any]) -> float:
        """Assess project metadata completeness."""
        score = 0.5
        
        project = findings.get('project', {})
        if not project:
            return score
        
        # Essential metadata
        if project.get('name') and project['name'] != 'unknown':
            score += 0.05
        if project.get('version') and project['version'] != '0.0.0':
            score += 0.05
        if project.get('description'):
            score += 0.1
        
        # Documentation
        if project.get('readme'):
            score += 0.1
        if project.get('homepage') or project.get('repository'):
            score += 0.05
        if project.get('documentation'):
            score += 0.05
        
        # Authors/maintainers
        if project.get('authors'):
            score += 0.05
        
        # License
        if project.get('license'):
            score += 0.1
        
        # Keywords and classifiers
        if project.get('keywords'):
            score += 0.025
        if project.get('classifiers'):
            score += 0.025
        
        return min(score, 1.0)
    
    def _assess_development_setup(self, findings: Dict[str, Any]) -> float:
        """Assess development tooling setup."""
        score = 0.5
        
        tool_configs = findings.get('tool_configs', {})
        
        # Code formatting
        if 'black' in tool_configs or 'autopep8' in tool_configs:
            score += 0.1
        
        # Import sorting
        if 'isort' in tool_configs:
            score += 0.05
        
        # Linting
        if any(tool in tool_configs for tool in ['ruff', 'pylint', 'flake8']):
            score += 0.1
        
        # Type checking
        if 'mypy' in tool_configs:
            score += 0.1
            # Strict mode is better
            mypy_config = tool_configs.get('mypy', {})
            if mypy_config.get('strict'):
                score += 0.05
        
        # Testing
        if 'pytest' in tool_configs:
            score += 0.1
        
        # Coverage
        if 'coverage' in tool_configs:
            score += 0.05
        
        # Scripts defined
        if findings.get('scripts'):
            score += 0.05
        
        return min(score, 1.0) 