"""
Container and orchestration handlers for docker-compose and Terraform

Handles analysis of container orchestration files like docker-compose.yml
and infrastructure as code files like Terraform configurations.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import yaml
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class DockerComposeHandler(DocumentHandler):
    """
    Handler for docker-compose.yml files.
    
    Analyzes Docker Compose configurations including services, networks,
    volumes, and orchestration patterns.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the docker-compose file."""
        if 'docker-compose' in file_path or 'compose.yml' in file_path or 'compose.yaml' in file_path:
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Docker Compose patterns
            if any(pattern in text for pattern in [
                'version:', 'services:', 'image:', 'container_name:',
                'ports:', 'volumes:', 'networks:', 'depends_on:'
            ]):
                # Try to parse as YAML to confirm
                try:
                    data = yaml.safe_load(text)
                    if isinstance(data, dict) and 'services' in data:
                        return True, 0.9
                except:
                    pass
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Docker Compose version and features."""
        text = content.decode('utf-8', errors='ignore')
        
        version = "unknown"
        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                version = str(data.get('version', 'unspecified'))
        except:
            pass
        
        return DocumentTypeInfo(
            type_name=f"Docker Compose Configuration (v{version})",
            confidence=0.95,
            category="orchestration",
            format="docker-compose"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Docker Compose analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Docker Compose",
            category="orchestration",
            key_findings=findings,
            ai_use_cases=[
                "Service dependency optimization",
                "Security hardening recommendations",
                "Resource allocation tuning",
                "Network topology visualization",
                "Environment configuration management",
                "Multi-stage deployment setup"
            ],
            quality_metrics={
                "security_score": self._assess_security(findings),
                "best_practices": self._assess_best_practices(findings),
                "complexity": self._assess_complexity(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Docker Compose configuration data."""
        text = content.decode('utf-8', errors='ignore')
        
        try:
            data = yaml.safe_load(text)
            if not isinstance(data, dict):
                return {"error": "Invalid YAML structure"}
        except Exception as e:
            return {"error": f"YAML parsing error: {str(e)}"}
        
        return {
            "version": data.get('version', 'unspecified'),
            "services": self._analyze_services(data.get('services', {})),
            "networks": self._analyze_networks(data.get('networks', {})),
            "volumes": self._analyze_volumes(data.get('volumes', {})),
            "secrets": self._analyze_secrets(data.get('secrets', {})),
            "configs": self._analyze_configs(data.get('configs', {})),
            "extensions": self._find_extensions(data),
            "total_services": len(data.get('services', {})),
            "dependencies": self._extract_dependencies(data.get('services', {})),
            "port_mappings": self._extract_port_mappings(data.get('services', {})),
            "environment_usage": self._analyze_environment_usage(data.get('services', {}))
        }
    
    def _analyze_services(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze individual services."""
        service_list = []
        
        for name, config in services.items():
            if not isinstance(config, dict):
                continue
                
            service_info = {
                "name": name,
                "image": config.get('image', 'build'),
                "has_build": 'build' in config,
                "ports": len(config.get('ports', [])),
                "volumes": len(config.get('volumes', [])),
                "environment_vars": self._count_env_vars(config),
                "depends_on": config.get('depends_on', []),
                "networks": config.get('networks', []),
                "restart_policy": config.get('restart', 'no'),
                "healthcheck": 'healthcheck' in config,
                "deploy_config": 'deploy' in config,
                "privileged": config.get('privileged', False),
                "user": config.get('user'),
                "command": bool(config.get('command')),
                "entrypoint": bool(config.get('entrypoint'))
            }
            
            service_list.append(service_info)
        
        return service_list
    
    def _count_env_vars(self, config: Dict[str, Any]) -> int:
        """Count environment variables in a service."""
        count = 0
        
        # environment as list
        if isinstance(config.get('environment'), list):
            count += len(config['environment'])
        # environment as dict
        elif isinstance(config.get('environment'), dict):
            count += len(config['environment'])
        
        # env_file
        if 'env_file' in config:
            count += 1  # We don't know how many vars are in the file
        
        return count
    
    def _analyze_networks(self, networks: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network configurations."""
        if not networks:
            return {"count": 0, "custom_networks": []}
        
        custom_networks = []
        for name, config in networks.items():
            if isinstance(config, dict):
                custom_networks.append({
                    "name": name,
                    "driver": config.get('driver', 'bridge'),
                    "external": config.get('external', False),
                    "attachable": config.get('attachable', False)
                })
        
        return {
            "count": len(networks),
            "custom_networks": custom_networks
        }
    
    def _analyze_volumes(self, volumes: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume configurations."""
        if not volumes:
            return {"count": 0, "named_volumes": []}
        
        named_volumes = []
        for name, config in volumes.items():
            volume_info = {"name": name}
            if isinstance(config, dict):
                volume_info.update({
                    "driver": config.get('driver', 'local'),
                    "external": config.get('external', False),
                    "driver_opts": bool(config.get('driver_opts'))
                })
            named_volumes.append(volume_info)
        
        return {
            "count": len(volumes),
            "named_volumes": named_volumes
        }
    
    def _analyze_secrets(self, secrets: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze secrets configuration."""
        if not secrets:
            return {"count": 0, "external_secrets": 0}
        
        external_count = sum(1 for s in secrets.values() 
                           if isinstance(s, dict) and s.get('external'))
        
        return {
            "count": len(secrets),
            "external_secrets": external_count
        }
    
    def _analyze_configs(self, configs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze configs configuration."""
        if not configs:
            return {"count": 0}
        
        return {"count": len(configs)}
    
    def _find_extensions(self, data: Dict[str, Any]) -> List[str]:
        """Find x- extension fields."""
        extensions = []
        
        def find_x_fields(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.startswith('x-'):
                        extensions.append(f"{path}.{key}" if path else key)
                    find_x_fields(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_x_fields(item, f"{path}[{i}]")
        
        find_x_fields(data)
        return extensions[:10]  # Limit to first 10
    
    def _extract_dependencies(self, services: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract service dependencies."""
        dependencies = {}
        
        for name, config in services.items():
            if isinstance(config, dict) and 'depends_on' in config:
                deps = config['depends_on']
                if isinstance(deps, list):
                    dependencies[name] = deps
                elif isinstance(deps, dict):
                    dependencies[name] = list(deps.keys())
        
        return dependencies
    
    def _extract_port_mappings(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all port mappings."""
        port_mappings = []
        
        for service_name, config in services.items():
            if isinstance(config, dict) and 'ports' in config:
                for port in config['ports']:
                    if isinstance(port, str):
                        # Parse string format "host:container"
                        parts = port.split(':')
                        if len(parts) >= 2:
                            port_mappings.append({
                                "service": service_name,
                                "host": parts[0],
                                "container": parts[-1]
                            })
                    elif isinstance(port, dict):
                        # Long syntax
                        port_mappings.append({
                            "service": service_name,
                            "host": port.get('published'),
                            "container": port.get('target'),
                            "protocol": port.get('protocol', 'tcp')
                        })
        
        return port_mappings
    
    def _analyze_environment_usage(self, services: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environment variable usage patterns."""
        env_stats = {
            "services_with_env": 0,
            "services_with_env_file": 0,
            "total_env_vars": 0,
            "common_vars": []
        }
        
        all_env_vars = []
        
        for config in services.values():
            if not isinstance(config, dict):
                continue
                
            if 'environment' in config:
                env_stats["services_with_env"] += 1
                if isinstance(config['environment'], list):
                    for env in config['environment']:
                        if '=' in env:
                            var_name = env.split('=')[0]
                            all_env_vars.append(var_name)
                elif isinstance(config['environment'], dict):
                    all_env_vars.extend(config['environment'].keys())
            
            if 'env_file' in config:
                env_stats["services_with_env_file"] += 1
        
        env_stats["total_env_vars"] = len(set(all_env_vars))
        
        # Find common variables
        from collections import Counter
        var_counts = Counter(all_env_vars)
        env_stats["common_vars"] = [var for var, count in var_counts.most_common(5) if count > 1]
        
        return env_stats
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        """Assess security configuration."""
        score = 0.7  # Base score
        
        # Check for security issues in services
        services = findings.get('services', [])
        for service in services:
            # Privileged mode is risky
            if service.get('privileged'):
                score -= 0.1
            
            # Running as specific user is good
            if service.get('user'):
                score += 0.02
            
            # Health checks are good
            if service.get('healthcheck'):
                score += 0.01
        
        # Using secrets properly
        secrets = findings.get('secrets', {})
        if secrets.get('count', 0) > 0:
            score += 0.1
        
        # Not exposing too many ports
        port_mappings = findings.get('port_mappings', [])
        if len(port_mappings) > 10:
            score -= 0.05
        
        return max(0.3, min(score, 1.0))
    
    def _assess_best_practices(self, findings: Dict[str, Any]) -> float:
        """Assess Docker Compose best practices."""
        score = 0.5
        
        # Using version 3+ is recommended
        version = findings.get('version', '1')
        if version.startswith('3'):
            score += 0.1
        
        # Named volumes are better than bind mounts
        volumes = findings.get('volumes', {})
        if volumes.get('count', 0) > 0:
            score += 0.1
        
        # Custom networks
        networks = findings.get('networks', {})
        if networks.get('count', 0) > 0:
            score += 0.1
        
        # Health checks
        services = findings.get('services', [])
        services_with_health = sum(1 for s in services if s.get('healthcheck'))
        if services and services_with_health / len(services) > 0.5:
            score += 0.1
        
        # Restart policies
        services_with_restart = sum(1 for s in services if s.get('restart_policy') != 'no')
        if services and services_with_restart / len(services) > 0.5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_complexity(self, findings: Dict[str, Any]) -> float:
        """Assess configuration complexity (lower is more complex)."""
        score = 1.0
        
        # Many services increase complexity
        service_count = findings.get('total_services', 0)
        if service_count > 10:
            score -= 0.2
        elif service_count > 5:
            score -= 0.1
        
        # Complex dependencies
        dependencies = findings.get('dependencies', {})
        if len(dependencies) > 5:
            score -= 0.1
        
        # Many port mappings
        if len(findings.get('port_mappings', [])) > 10:
            score -= 0.1
        
        # Using extensions adds complexity
        if findings.get('extensions'):
            score -= 0.05
        
        return max(0.3, score)


class TerraformHandler(DocumentHandler):
    """
    Handler for Terraform configuration files (.tf).
    
    Analyzes Terraform infrastructure as code including resources,
    variables, outputs, modules, and providers.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Terraform file."""
        if file_path.endswith('.tf') or file_path.endswith('.tfvars'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Terraform HCL patterns
            if any(pattern in text for pattern in [
                'resource "', 'variable "', 'output "', 'module "',
                'provider "', 'terraform {', 'locals {'
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Terraform file type."""
        if file_path.endswith('.tfvars'):
            type_name = "Terraform Variables File"
        elif 'main.tf' in file_path:
            type_name = "Terraform Main Configuration"
        elif 'variables.tf' in file_path:
            type_name = "Terraform Variables Definition"
        elif 'outputs.tf' in file_path:
            type_name = "Terraform Outputs Definition"
        else:
            type_name = "Terraform Configuration"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="infrastructure",
            format="terraform"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Terraform analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Terraform",
            category="infrastructure",
            key_findings=findings,
            ai_use_cases=[
                "Infrastructure optimization",
                "Security compliance checking",
                "Cost estimation and optimization",
                "Module refactoring",
                "Multi-environment configuration",
                "Drift detection setup"
            ],
            quality_metrics={
                "modularity": self._assess_modularity(findings),
                "security": self._assess_security(findings),
                "maintainability": self._assess_maintainability(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Terraform configuration data."""
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "resources": self._extract_resources(text),
            "variables": self._extract_variables(text),
            "outputs": self._extract_outputs(text),
            "modules": self._extract_modules(text),
            "providers": self._extract_providers(text),
            "data_sources": self._extract_data_sources(text),
            "locals": self._extract_locals(text),
            "terraform_block": self._extract_terraform_block(text),
            "backend": self._extract_backend(text),
            "provisioners": self._extract_provisioners(text),
            "dependencies": self._analyze_dependencies(text),
            "interpolations": self._count_interpolations(text),
            "comments": len(re.findall(r'#[^\n]*|//[^\n]*|/\*.*?\*/', text, re.DOTALL))
        }
    
    def _extract_resources(self, text: str) -> List[Dict[str, Any]]:
        """Extract resource definitions."""
        resources = []
        
        for match in re.finditer(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{', text):
            resource_type = match.group(1)
            resource_name = match.group(2)
            
            # Extract the resource block
            block_start = match.end()
            block_content = self._extract_block_content(text[block_start:])
            
            resources.append({
                "type": resource_type,
                "name": resource_name,
                "provider": resource_type.split('_')[0],
                "has_count": 'count' in block_content,
                "has_for_each": 'for_each' in block_content,
                "has_depends_on": 'depends_on' in block_content,
                "has_lifecycle": 'lifecycle' in block_content,
                "lines": len(block_content.split('\n'))
            })
        
        return resources
    
    def _extract_variables(self, text: str) -> List[Dict[str, Any]]:
        """Extract variable definitions."""
        variables = []
        
        for match in re.finditer(r'variable\s+"([^"]+)"\s*{', text):
            var_name = match.group(1)
            
            # Extract the variable block
            block_start = match.end()
            block_content = self._extract_block_content(text[block_start:])
            
            variables.append({
                "name": var_name,
                "has_type": 'type' in block_content,
                "has_default": 'default' in block_content,
                "has_description": 'description' in block_content,
                "has_validation": 'validation' in block_content,
                "sensitive": 'sensitive = true' in block_content
            })
        
        return variables
    
    def _extract_outputs(self, text: str) -> List[Dict[str, Any]]:
        """Extract output definitions."""
        outputs = []
        
        for match in re.finditer(r'output\s+"([^"]+)"\s*{', text):
            output_name = match.group(1)
            
            # Extract the output block
            block_start = match.end()
            block_content = self._extract_block_content(text[block_start:])
            
            outputs.append({
                "name": output_name,
                "has_description": 'description' in block_content,
                "sensitive": 'sensitive = true' in block_content,
                "has_depends_on": 'depends_on' in block_content
            })
        
        return outputs
    
    def _extract_modules(self, text: str) -> List[Dict[str, Any]]:
        """Extract module usage."""
        modules = []
        
        for match in re.finditer(r'module\s+"([^"]+)"\s*{', text):
            module_name = match.group(1)
            
            # Extract the module block
            block_start = match.end()
            block_content = self._extract_block_content(text[block_start:])
            
            # Extract source
            source_match = re.search(r'source\s*=\s*"([^"]+)"', block_content)
            source = source_match.group(1) if source_match else "unknown"
            
            modules.append({
                "name": module_name,
                "source": source,
                "is_registry": source.startswith('terraform-') or '/' in source,
                "is_local": source.startswith('./') or source.startswith('../'),
                "has_version": 'version' in block_content,
                "has_count": 'count' in block_content,
                "has_for_each": 'for_each' in block_content
            })
        
        return modules
    
    def _extract_providers(self, text: str) -> List[Dict[str, Any]]:
        """Extract provider configurations."""
        providers = []
        
        for match in re.finditer(r'provider\s+"([^"]+)"\s*{', text):
            provider_name = match.group(1)
            
            # Extract the provider block
            block_start = match.end()
            block_content = self._extract_block_content(text[block_start:])
            
            providers.append({
                "name": provider_name,
                "has_alias": 'alias' in block_content,
                "has_version": 'version' in block_content,
                "has_region": 'region' in block_content
            })
        
        # Also check required_providers
        terraform_block = self._extract_terraform_block(text)
        if 'required_providers' in terraform_block:
            # This is a simplified extraction
            providers.append({"name": "required_providers", "from_terraform_block": True})
        
        return providers
    
    def _extract_data_sources(self, text: str) -> List[Dict[str, Any]]:
        """Extract data source definitions."""
        data_sources = []
        
        for match in re.finditer(r'data\s+"([^"]+)"\s+"([^"]+)"\s*{', text):
            data_type = match.group(1)
            data_name = match.group(2)
            
            data_sources.append({
                "type": data_type,
                "name": data_name,
                "provider": data_type.split('_')[0]
            })
        
        return data_sources
    
    def _extract_locals(self, text: str) -> Dict[str, Any]:
        """Extract local values."""
        locals_match = re.search(r'locals\s*{([^}]+)}', text, re.DOTALL)
        
        if locals_match:
            locals_content = locals_match.group(1)
            # Count local variables (simplified)
            local_vars = re.findall(r'(\w+)\s*=', locals_content)
            
            return {
                "count": len(local_vars),
                "names": local_vars[:10]  # First 10
            }
        
        return {"count": 0, "names": []}
    
    def _extract_terraform_block(self, text: str) -> Dict[str, Any]:
        """Extract terraform configuration block."""
        terraform_match = re.search(r'terraform\s*{([^}]+)}', text, re.DOTALL)
        
        if terraform_match:
            content = terraform_match.group(1)
            return {
                "has_required_version": 'required_version' in content,
                "has_required_providers": 'required_providers' in content,
                "has_backend": 'backend' in content,
                "has_experiments": 'experiments' in content
            }
        
        return {}
    
    def _extract_backend(self, text: str) -> Dict[str, Any]:
        """Extract backend configuration."""
        # Look for backend in terraform block
        terraform_match = re.search(r'terraform\s*{[^}]*backend\s+"([^"]+)"', text, re.DOTALL)
        
        if terraform_match:
            backend_type = terraform_match.group(1)
            return {
                "type": backend_type,
                "is_remote": backend_type in ['remote', 's3', 'azurerm', 'gcs']
            }
        
        return {"type": None, "is_remote": False}
    
    def _extract_provisioners(self, text: str) -> List[str]:
        """Extract provisioner usage."""
        provisioners = re.findall(r'provisioner\s+"([^"]+)"', text)
        return list(set(provisioners))
    
    def _extract_block_content(self, text: str) -> str:
        """Extract content of a HCL block."""
        brace_count = 1
        pos = 0
        
        while pos < len(text) and brace_count > 0:
            if text[pos] == '{':
                brace_count += 1
            elif text[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return text[:pos-1] if brace_count == 0 else text
    
    def _analyze_dependencies(self, text: str) -> Dict[str, Any]:
        """Analyze resource dependencies."""
        # Count explicit dependencies
        explicit_deps = len(re.findall(r'depends_on\s*=', text))
        
        # Count references (simplified - looks for ${} and resource.name patterns)
        references = len(re.findall(r'\${[^}]+}|[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+', text))
        
        return {
            "explicit_dependencies": explicit_deps,
            "reference_count": references
        }
    
    def _count_interpolations(self, text: str) -> int:
        """Count string interpolations."""
        # Both ${} and %{} syntax
        return len(re.findall(r'[$%]{[^}]+}', text))
    
    def _assess_modularity(self, findings: Dict[str, Any]) -> float:
        """Assess code modularity."""
        score = 0.5
        
        # Using modules is good
        modules = findings.get('modules', [])
        if modules:
            score += min(0.2, len(modules) * 0.05)
        
        # Using locals for DRY
        if findings.get('locals', {}).get('count', 0) > 0:
            score += 0.1
        
        # Variables with defaults and descriptions
        variables = findings.get('variables', [])
        if variables:
            well_defined = sum(1 for v in variables if v.get('has_description') and v.get('has_type'))
            if well_defined / len(variables) > 0.5:
                score += 0.1
        
        # Outputs for module interface
        if findings.get('outputs'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        """Assess security practices."""
        score = 0.6
        
        # Sensitive variables marked
        variables = findings.get('variables', [])
        sensitive_vars = sum(1 for v in variables if v.get('sensitive'))
        if sensitive_vars > 0:
            score += 0.1
        
        # Sensitive outputs marked
        outputs = findings.get('outputs', [])
        sensitive_outputs = sum(1 for o in outputs if o.get('sensitive'))
        if sensitive_outputs > 0:
            score += 0.1
        
        # Remote backend (better than local)
        backend = findings.get('backend', {})
        if backend.get('is_remote'):
            score += 0.1
        
        # Not using provisioners (they can be security risks)
        if not findings.get('provisioners'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_maintainability(self, findings: Dict[str, Any]) -> float:
        """Assess maintainability."""
        score = 0.5
        
        # Good variable documentation
        variables = findings.get('variables', [])
        if variables:
            documented = sum(1 for v in variables if v.get('has_description'))
            if documented / len(variables) > 0.7:
                score += 0.15
        
        # Good output documentation
        outputs = findings.get('outputs', [])
        if outputs:
            documented = sum(1 for o in outputs if o.get('has_description'))
            if outputs and documented / len(outputs) > 0.7:
                score += 0.1
        
        # Comments
        if findings.get('comments', 0) > 5:
            score += 0.1
        
        # Not too many resources in one file
        if len(findings.get('resources', [])) < 20:
            score += 0.1
        
        # Using data sources (better than hardcoding)
        if findings.get('data_sources'):
            score += 0.05
        
        return min(score, 1.0) 