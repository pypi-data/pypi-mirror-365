"""
Configuration File Handlers for Document Analysis Framework
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis

logger = logging.getLogger(__name__)

class DockerfileHandler(DocumentHandler):
    """Handler for Dockerfile configuration files"""
    
    handler_type = "config"
    supported_types = ["Dockerfile", "Docker Configuration"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        filename = Path(file_path).name.lower()
        if filename in ['dockerfile', 'dockerfile.prod', 'dockerfile.dev'] or filename.startswith('dockerfile.'):
            return True, 0.95
        
        # Check content for Dockerfile instructions
        try:
            text = content.decode('utf-8', errors='ignore')[:1000].upper()
            dockerfile_instructions = ['FROM', 'RUN', 'COPY', 'ADD', 'WORKDIR', 'EXPOSE', 'CMD', 'ENTRYPOINT']
            instruction_matches = sum(1 for instr in dockerfile_instructions if f'{instr} ' in text or text.startswith(instr))
            if instruction_matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        # Try to detect base image
        try:
            text = content.decode('utf-8', errors='ignore')
            from_match = re.search(r'FROM\s+([^\s\n]+)', text, re.IGNORECASE)
            base_image = from_match.group(1) if from_match else "unknown"
        except:
            base_image = "unknown"
        
        return DocumentTypeInfo(
            type_name="Dockerfile",
            confidence=0.95,
            category="config",
            version=base_image,
            subtype="container"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Dockerfile",
            category="config",
            key_findings=findings,
            ai_use_cases=[
                "Container security analysis",
                "Dockerfile optimization recommendations",
                "Base image vulnerability scanning",
                "Multi-stage build optimization",
                "Container size reduction",
                "Security best practices enforcement",
                "CI/CD pipeline integration",
                "Image layer analysis",
                "Performance optimization",
                "Compliance checking"
            ],
            quality_metrics={
                "security_score": findings.get("security_score", 0.5),
                "optimization_score": findings.get("optimization_score", 0.6),
                "best_practices_score": findings.get("best_practices_score", 0.7),
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
            "format": "Dockerfile",
            "line_count": text.count('\n') + 1
        }
        
        # Parse Dockerfile instructions
        instructions = {}
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(None, 1)
                if parts:
                    instruction = parts[0].upper()
                    instructions[instruction] = instructions.get(instruction, 0) + 1
        
        data["instructions"] = instructions
        data["total_instructions"] = sum(instructions.values())
        
        # Extract key information
        # Base image
        from_match = re.search(r'FROM\s+([^\s\n]+)', text, re.IGNORECASE)
        if from_match:
            data["base_image"] = from_match.group(1)
        
        # Exposed ports
        expose_matches = re.findall(r'EXPOSE\s+(\d+)', text, re.IGNORECASE)
        if expose_matches:
            data["exposed_ports"] = [int(port) for port in expose_matches]
        
        # Working directory
        workdir_matches = re.findall(r'WORKDIR\s+([^\s\n]+)', text, re.IGNORECASE)
        if workdir_matches:
            data["working_directories"] = workdir_matches
        
        # Environment variables
        env_matches = re.findall(r'ENV\s+(\w+)', text, re.IGNORECASE)
        data["environment_variables"] = env_matches
        
        # Security analysis
        security_issues = []
        if 'USER root' in text.upper() or 'USER 0' in text:
            security_issues.append("Running as root user")
        if re.search(r'RUN.*sudo', text, re.IGNORECASE):
            security_issues.append("Using sudo in RUN instruction")
        if 'ADD http' in text.upper():
            security_issues.append("Using ADD with URL (prefer COPY)")
        
        data["security_issues"] = security_issues
        data["security_score"] = max(0.9 - len(security_issues) * 0.2, 0.1)
        
        # Optimization analysis
        optimization_issues = []
        run_count = instructions.get('RUN', 0)
        if run_count > 5:
            optimization_issues.append(f"Too many RUN instructions ({run_count})")
        if 'apt-get update' in text and 'apt-get clean' not in text:
            optimization_issues.append("Missing apt-get clean after update")
        
        data["optimization_issues"] = optimization_issues
        data["optimization_score"] = max(0.9 - len(optimization_issues) * 0.1, 0.3)
        
        # Best practices check
        best_practices_issues = []
        if 'MAINTAINER' in instructions:
            best_practices_issues.append("Using deprecated MAINTAINER (use LABEL)")
        if instructions.get('FROM', 0) > 1:
            data["multi_stage_build"] = True
        else:
            data["multi_stage_build"] = False
        
        data["best_practices_issues"] = best_practices_issues
        data["best_practices_score"] = max(0.9 - len(best_practices_issues) * 0.1, 0.5)
        
        return data

class PackageJSONHandler(DocumentHandler):
    """Handler for package.json files (Node.js/npm)"""
    
    handler_type = "config"
    supported_types = ["package.json", "Node.js Package Configuration"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if Path(file_path).name.lower() == 'package.json':
            return True, 0.95
        
        # Try to parse as JSON and check for npm-specific fields
        try:
            text = content.decode('utf-8', errors='ignore')
            data = json.loads(text)
            if isinstance(data, dict) and ('name' in data or 'dependencies' in data or 'scripts' in data):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        try:
            text = content.decode('utf-8', errors='ignore')
            data = json.loads(text)
            package_name = data.get('name', 'unknown')
            version = data.get('version', 'unknown')
        except:
            package_name = 'unknown'
            version = 'unknown'
        
        return DocumentTypeInfo(
            type_name="package.json",
            confidence=0.95,
            category="config",
            version=version,
            subtype="npm_package",
            metadata={"package_name": package_name}
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="package.json",
            category="config",
            key_findings=findings,
            ai_use_cases=[
                "Dependency vulnerability scanning",
                "Package upgrade recommendations",
                "License compliance checking",
                "Bundle size optimization",
                "Script automation analysis",
                "Security audit automation",
                "Monorepo management",
                "CI/CD pipeline configuration",
                "Performance monitoring setup",
                "Package publishing automation"
            ],
            quality_metrics={
                "dependency_health": findings.get("dependency_health", 0.7),
                "security_score": findings.get("security_score", 0.8),
                "maintenance_score": findings.get("maintenance_score", 0.6),
                "ai_readiness": 0.95
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        try:
            text = content.decode('utf-8', errors='replace')
            package_data = json.loads(text)
        except json.JSONDecodeError:
            return {
                "file_size": len(content),
                "format": "package.json",
                "parse_error": "Invalid JSON"
            }
        
        data = {
            "file_size": len(content),
            "format": "package.json"
        }
        
        # Basic package info
        data["name"] = package_data.get("name", "unknown")
        data["version"] = package_data.get("version", "unknown")
        data["description"] = package_data.get("description", "")
        data["author"] = package_data.get("author", "")
        data["license"] = package_data.get("license", "unknown")
        
        # Dependencies analysis
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})
        peer_dependencies = package_data.get("peerDependencies", {})
        
        data["dependency_count"] = len(dependencies)
        data["dev_dependency_count"] = len(dev_dependencies)
        data["peer_dependency_count"] = len(peer_dependencies)
        data["total_dependencies"] = len(dependencies) + len(dev_dependencies) + len(peer_dependencies)
        
        if dependencies:
            data["dependencies"] = list(dependencies.keys())[:20]
        if dev_dependencies:
            data["dev_dependencies"] = list(dev_dependencies.keys())[:20]
        
        # Scripts analysis
        scripts = package_data.get("scripts", {})
        data["script_count"] = len(scripts)
        data["scripts"] = list(scripts.keys())
        
        # Common framework detection
        frameworks = []
        all_deps = {**dependencies, **dev_dependencies}
        
        framework_indicators = {
            "React": ["react", "react-dom"],
            "Vue": ["vue"],
            "Angular": ["@angular/core"],
            "Express": ["express"],
            "Next.js": ["next"],
            "Nuxt": ["nuxt"],
            "Gatsby": ["gatsby"],
            "Webpack": ["webpack"],
            "TypeScript": ["typescript"],
            "Jest": ["jest"],
            "ESLint": ["eslint"]
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in all_deps for indicator in indicators):
                frameworks.append(framework)
        
        data["detected_frameworks"] = frameworks
        
        # Quality metrics
        # Dependency health (fewer dependencies generally better)
        dep_health = max(0.9 - (data["total_dependencies"] / 100), 0.1)
        data["dependency_health"] = dep_health
        
        # Security score (based on having security-related scripts/deps)
        security_indicators = ["audit", "security", "snyk", "nsp"]
        has_security = any(
            any(indicator in key.lower() for indicator in security_indicators)
            for key in scripts.keys()
        ) or any(
            any(indicator in key.lower() for indicator in security_indicators)
            for key in all_deps.keys()
        )
        data["security_score"] = 0.9 if has_security else 0.6
        
        # Maintenance score (based on having proper scripts and metadata)
        maintenance_indicators = ["test", "build", "lint", "format"]
        maintenance_score = 0.5
        if data.get("description"):
            maintenance_score += 0.1
        if data.get("license") != "unknown":
            maintenance_score += 0.1
        script_matches = sum(1 for indicator in maintenance_indicators if any(indicator in script for script in scripts.keys()))
        maintenance_score += min(script_matches * 0.1, 0.3)
        
        data["maintenance_score"] = min(maintenance_score, 1.0)
        
        return data

class RequirementsHandler(DocumentHandler):
    """Handler for Python requirements.txt files"""
    
    handler_type = "config"
    supported_types = ["requirements.txt", "Python Requirements"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        filename = Path(file_path).name.lower()
        if filename in ['requirements.txt', 'requirements-dev.txt', 'requirements-test.txt'] or filename.startswith('requirements'):
            return True, 0.95
        
        # Check content for pip package patterns
        try:
            text = content.decode('utf-8', errors='ignore')
            lines = [line.strip() for line in text.split('\n') if line.strip() and not line.strip().startswith('#')]
            if lines:
                # Look for package name patterns
                package_patterns = [r'^[a-zA-Z][\w-]*[=<>!]', r'^[a-zA-Z][\w-]*$']
                matches = sum(1 for line in lines[:10] if any(re.match(pattern, line) for pattern in package_patterns))
                if matches >= 2:
                    return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        filename = Path(file_path).name.lower()
        
        if 'dev' in filename:
            subtype = "development"
        elif 'test' in filename:
            subtype = "testing"
        elif 'prod' in filename:
            subtype = "production"
        else:
            subtype = "general"
        
        return DocumentTypeInfo(
            type_name="Python Requirements",
            confidence=0.95,
            category="config",
            subtype=subtype,
            language="python"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Python Requirements",
            category="config",
            key_findings=findings,
            ai_use_cases=[
                "Dependency vulnerability scanning",
                "Package upgrade planning",
                "License compliance checking",
                "Environment reproducibility",
                "Security audit automation",
                "Virtual environment management",
                "CI/CD pipeline optimization",
                "Containerization support",
                "Package conflict resolution",
                "Performance impact analysis"
            ],
            quality_metrics={
                "version_specificity": findings.get("version_specificity", 0.5),
                "security_awareness": findings.get("security_awareness", 0.6),
                "maintainability": findings.get("maintainability", 0.7),
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
            "format": "requirements.txt",
            "line_count": text.count('\n') + 1
        }
        
        lines = text.split('\n')
        packages = []
        comments = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elif line.startswith('#'):
                comments.append(line[1:].strip())
            elif line.startswith('-'):
                # pip options like -r, -e, etc.
                data["has_pip_options"] = True
            else:
                # Package specification
                packages.append(line)
        
        data["package_count"] = len(packages)
        data["comment_count"] = len(comments)
        
        # Parse package specifications
        parsed_packages = []
        version_operators = {'==', '>=', '<=', '>', '<', '!=', '~='}
        pinned_count = 0
        
        for pkg in packages:
            # Remove inline comments
            pkg = pkg.split('#')[0].strip()
            if not pkg:
                continue
            
            # Parse package name and version spec
            name = pkg
            version_spec = ""
            has_version = False
            
            for op in version_operators:
                if op in pkg:
                    parts = pkg.split(op, 1)
                    name = parts[0].strip()
                    version_spec = op + parts[1].strip() if len(parts) > 1 else op
                    has_version = True
                    if op == '==':
                        pinned_count += 1
                    break
            
            parsed_packages.append({
                "name": name,
                "version_spec": version_spec,
                "has_version": has_version,
                "original": pkg
            })
        
        data["packages"] = [p["name"] for p in parsed_packages[:20]]  # First 20 package names
        data["pinned_versions"] = pinned_count
        data["version_specificity"] = pinned_count / len(packages) if packages else 0
        
        # Detect common Python packages and frameworks
        well_known_packages = {
            "web_frameworks": ["django", "flask", "fastapi", "tornado", "pyramid"],
            "data_science": ["numpy", "pandas", "matplotlib", "seaborn", "scikit-learn", "tensorflow", "pytorch"],
            "testing": ["pytest", "unittest2", "nose", "mock", "coverage"],
            "deployment": ["gunicorn", "uwsgi", "celery", "redis", "docker"],
            "security": ["cryptography", "pyjwt", "bcrypt", "passlib"]
        }
        
        detected_categories = {}
        package_names = [p["name"].lower() for p in parsed_packages]
        
        for category, pkg_list in well_known_packages.items():
            matches = [pkg for pkg in pkg_list if pkg in package_names]
            if matches:
                detected_categories[category] = matches
        
        data["detected_categories"] = detected_categories
        
        # Quality metrics
        # Security awareness (based on having security-related packages or comments)
        security_keywords = ["security", "crypto", "auth", "hash", "ssl", "tls"]
        has_security = any(
            any(keyword in pkg.lower() for keyword in security_keywords)
            for pkg in package_names
        ) or any(
            any(keyword in comment.lower() for keyword in security_keywords)
            for comment in comments
        )
        data["security_awareness"] = 0.8 if has_security else 0.5
        
        # Maintainability (based on comments, version pinning, organization)
        maintainability = 0.5
        if data["comment_count"] > 0:
            maintainability += 0.2
        if data["version_specificity"] > 0.5:
            maintainability += 0.2
        if len(detected_categories) > 0:
            maintainability += 0.1
        
        data["maintainability"] = min(maintainability, 1.0)
        
        return data

class MakefileHandler(DocumentHandler):
    """Handler for Makefile build configuration files"""
    
    handler_type = "config"
    supported_types = ["Makefile", "GNU Make"]
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        filename = Path(file_path).name.lower()
        if filename in ['makefile', 'makefile.am', 'gnumakefile'] or filename.startswith('makefile'):
            return True, 0.95
        
        # Check content for Makefile patterns
        try:
            text = content.decode('utf-8', errors='ignore')[:1000]
            makefile_patterns = [
                r'^\w+\s*:.*$',  # Target: dependencies
                r'^\t.*$',  # Tab-indented commands
                r'^\w+\s*=\s*.*$',  # Variable assignments
                r'\$\(\w+\)',  # Variable references
            ]
            matches = sum(1 for pattern in makefile_patterns if re.search(pattern, text, re.MULTILINE))
            if matches >= 2:
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        # Try to detect Makefile type
        try:
            text = content.decode('utf-8', errors='ignore')
            if 'automake' in text.lower() or 'makefile.am' in file_path.lower():
                subtype = "Automake"
            elif 'cmake' in text.lower():
                subtype = "CMake"
            elif any(target in text for target in ['install:', 'clean:', 'all:']):
                subtype = "GNU Make"
            else:
                subtype = "Generic Make"
        except:
            subtype = "Generic Make"
        
        return DocumentTypeInfo(
            type_name="Makefile",
            confidence=0.95,
            category="config",
            subtype=subtype,
            language="make"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Makefile",
            category="config",
            key_findings=findings,
            ai_use_cases=[
                "Build system analysis and optimization",
                "Dependency tree visualization",
                "Cross-platform compatibility analysis",
                "Build performance optimization",
                "CI/CD pipeline integration",
                "Project structure analysis",
                "Tool chain configuration",
                "Automated build troubleshooting"
            ],
            quality_metrics={
                "build_complexity": findings.get("complexity_score", 0.5),
                "organization_quality": findings.get("organization_quality", 0.6),
                "portability_score": findings.get("portability_score", 0.7),
                "ai_readiness": 0.8
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
            "format": "Makefile",
            "line_count": text.count('\n') + 1
        }
        
        lines = text.split('\n')
        
        # Parse Makefile structure
        targets = []
        variables = []
        comments = 0
        
        for line in lines:
            line = line.rstrip()
            if line.startswith('#'):
                comments += 1
            elif ':' in line and not line.startswith('\t'):
                # Target definition
                target_part = line.split(':')[0].strip()
                if target_part and not target_part.startswith('$'):
                    targets.append(target_part)
            elif '=' in line and not line.startswith('\t'):
                # Variable assignment
                var_name = line.split('=')[0].strip()
                if var_name and not var_name.startswith('$'):
                    variables.append(var_name)
        
        data["target_count"] = len(targets)
        data["targets"] = targets[:20]  # First 20 targets
        data["variable_count"] = len(variables)
        data["variables"] = variables[:20]  # First 20 variables
        data["comment_lines"] = comments
        
        # Detect common targets and variables
        common_targets = ['all', 'clean', 'install', 'test', 'dist', 'distclean']
        found_common_targets = [t for t in targets if t.lower() in common_targets]
        data["standard_targets"] = found_common_targets
        
        common_variables = ['CC', 'CXX', 'CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'PREFIX']
        found_common_vars = [v for v in variables if v.upper() in common_variables]
        data["standard_variables"] = found_common_vars
        
        # Analyze complexity
        # Count variable references
        var_refs = len(re.findall(r'\$\(\w+\)', text))
        data["variable_references"] = var_refs
        
        # Count function calls
        func_calls = len(re.findall(r'\$\([\w-]+\s+', text))
        data["function_calls"] = func_calls
        
        # Count conditional statements
        conditionals = len(re.findall(r'^\s*if', text, re.MULTILINE))
        data["conditionals"] = conditionals
        
        # Calculate complexity score
        complexity_factors = [
            len(targets) / 20,  # Normalize by expected max
            len(variables) / 30,
            var_refs / 50,
            func_calls / 20,
            conditionals / 10
        ]
        data["complexity_score"] = min(sum(complexity_factors) / len(complexity_factors), 1.0)
        
        # Organization quality
        org_score = 0.5
        if len(found_common_targets) >= 3:
            org_score += 0.2
        if len(found_common_vars) >= 2:
            org_score += 0.2
        if comments > 5:
            org_score += 0.1
        data["organization_quality"] = min(org_score, 1.0)
        
        # Portability assessment
        portability_issues = []
        if 'gcc' in text.lower():
            portability_issues.append("GCC-specific")
        if '/usr/local' in text:
            portability_issues.append("Hardcoded paths")
        if '.exe' in text:
            portability_issues.append("Windows-specific")
        
        data["portability_issues"] = portability_issues
        data["portability_score"] = max(0.9 - len(portability_issues) * 0.2, 0.3)
        
        return data