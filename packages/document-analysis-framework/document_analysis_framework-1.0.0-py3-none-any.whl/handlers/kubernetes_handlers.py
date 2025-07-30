"""
Kubernetes and Helm handlers for container orchestration files

Handles analysis of Kubernetes manifests and Helm chart configurations
for cloud-native applications.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import yaml
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class KubernetesHandler(DocumentHandler):
    """
    Handler for Kubernetes manifest files (YAML).
    
    Analyzes Kubernetes resources including deployments, services,
    configmaps, and other Kubernetes objects.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Kubernetes file."""
        # Common Kubernetes file patterns
        k8s_patterns = [
            'deployment.yaml', 'deployment.yml',
            'service.yaml', 'service.yml',
            'configmap.yaml', 'configmap.yml',
            'secret.yaml', 'secret.yml',
            'ingress.yaml', 'ingress.yml',
            'pod.yaml', 'pod.yml',
            '-k8s.yaml', '-k8s.yml',
            'kustomization.yaml', 'kustomization.yml'
        ]
        
        if any(pattern in file_path.lower() for pattern in k8s_patterns):
            return True, 0.9
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Kubernetes API patterns
            if any(pattern in text for pattern in [
                'apiVersion:', 'kind:', 'metadata:',
                'spec:', 'containers:', 'replicas:',
                'v1', 'apps/v1', 'batch/v1',
                'Deployment', 'Service', 'ConfigMap', 'Secret'
            ]):
                # Try to parse as YAML
                try:
                    docs = list(yaml.safe_load_all(text))
                    # Check if it has Kubernetes structure
                    for doc in docs:
                        if isinstance(doc, dict) and 'apiVersion' in doc and 'kind' in doc:
                            return True, 0.85
                except:
                    pass
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Kubernetes resource types."""
        text = content.decode('utf-8', errors='ignore')
        
        # Parse YAML documents
        try:
            docs = list(yaml.safe_load_all(text))
            kinds = [doc.get('kind', 'Unknown') for doc in docs if isinstance(doc, dict)]
            
            if len(kinds) == 1:
                type_name = f"Kubernetes {kinds[0]}"
            elif len(kinds) > 1:
                type_name = f"Kubernetes Manifests ({len(kinds)} resources)"
            else:
                type_name = "Kubernetes Configuration"
                
            # Check for Kustomization
            if any(k == 'Kustomization' for k in kinds) or 'kustomization' in file_path.lower():
                type_name = "Kustomization Configuration"
                
        except:
            type_name = "Kubernetes YAML"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="orchestration",
            format="kubernetes"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Kubernetes manifest analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Kubernetes",
            category="orchestration",
            key_findings=findings,
            ai_use_cases=[
                "Resource optimization and scaling",
                "Security policy generation",
                "Network policy configuration",
                "Resource quota management",
                "Multi-environment deployment",
                "GitOps workflow setup"
            ],
            quality_metrics={
                "security_score": self._assess_security(findings),
                "best_practices": self._assess_best_practices(findings),
                "resource_efficiency": self._assess_resource_efficiency(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Kubernetes manifest data."""
        text = content.decode('utf-8', errors='ignore')
        
        try:
            docs = list(yaml.safe_load_all(text))
            resources = []
            
            for doc in docs:
                if isinstance(doc, dict) and 'kind' in doc:
                    resources.append(self._analyze_resource(doc))
            
            return {
                "resources": resources,
                "resource_count": len(resources),
                "namespaces": self._extract_namespaces(resources),
                "images": self._extract_images(resources),
                "labels": self._extract_labels(resources),
                "annotations": self._extract_annotations(resources),
                "services": self._analyze_services(resources),
                "deployments": self._analyze_deployments(resources),
                "configmaps": self._analyze_configmaps(resources),
                "secrets": self._analyze_secrets(resources),
                "rbac": self._analyze_rbac(resources),
                "network_policies": self._analyze_network_policies(resources),
                "resource_requirements": self._analyze_resource_requirements(resources)
            }
            
        except Exception as e:
            return {"error": f"Failed to parse Kubernetes YAML: {str(e)}"}
    
    def _analyze_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single Kubernetes resource."""
        return {
            "apiVersion": resource.get('apiVersion', 'unknown'),
            "kind": resource.get('kind', 'unknown'),
            "name": resource.get('metadata', {}).get('name', 'unnamed'),
            "namespace": resource.get('metadata', {}).get('namespace', 'default'),
            "labels": resource.get('metadata', {}).get('labels', {}),
            "annotations": resource.get('metadata', {}).get('annotations', {}),
            "has_owner_references": bool(resource.get('metadata', {}).get('ownerReferences')),
            "has_finalizers": bool(resource.get('metadata', {}).get('finalizers'))
        }
    
    def _extract_namespaces(self, resources: List[Dict[str, Any]]) -> List[str]:
        """Extract unique namespaces."""
        namespaces = set()
        for resource in resources:
            namespaces.add(resource.get('namespace', 'default'))
        return sorted(list(namespaces))
    
    def _extract_images(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract container images from all resources."""
        images = []
        
        for resource in resources:
            if resource['kind'] in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Pod']:
                # Find the original resource data
                for doc in yaml.safe_load_all(resource.get('_raw', '')):
                    if isinstance(doc, dict):
                        containers = self._get_containers_from_spec(doc.get('spec', {}))
                        for container in containers:
                            image = container.get('image', '')
                            if image:
                                images.append({
                                    "image": image,
                                    "resource": f"{resource['kind']}/{resource['name']}",
                                    "has_tag": ':' in image and not image.endswith(':latest'),
                                    "is_latest": image.endswith(':latest') or ':' not in image
                                })
        
        return images
    
    def _get_containers_from_spec(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract containers from various spec types."""
        containers = []
        
        # Direct containers (Pod)
        if 'containers' in spec:
            containers.extend(spec['containers'])
        
        # Template spec (Deployment, StatefulSet, etc.)
        if 'template' in spec and 'spec' in spec['template']:
            if 'containers' in spec['template']['spec']:
                containers.extend(spec['template']['spec']['containers'])
        
        # Job spec
        if 'jobTemplate' in spec and 'spec' in spec['jobTemplate']:
            template_spec = spec['jobTemplate']['spec']
            if 'template' in template_spec and 'spec' in template_spec['template']:
                if 'containers' in template_spec['template']['spec']:
                    containers.extend(template_spec['template']['spec']['containers'])
        
        return containers
    
    def _extract_labels(self, resources: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract and categorize labels."""
        all_labels = {}
        
        for resource in resources:
            for key, value in resource.get('labels', {}).items():
                if key not in all_labels:
                    all_labels[key] = []
                if value not in all_labels[key]:
                    all_labels[key].append(value)
        
        return all_labels
    
    def _extract_annotations(self, resources: List[Dict[str, Any]]) -> List[str]:
        """Extract unique annotation keys."""
        annotations = set()
        
        for resource in resources:
            annotations.update(resource.get('annotations', {}).keys())
        
        return sorted(list(annotations))
    
    def _analyze_services(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Service resources."""
        services = [r for r in resources if r['kind'] == 'Service']
        
        return {
            "count": len(services),
            "types": self._count_service_types(services),
            "has_loadbalancer": any(self._is_loadbalancer(s) for s in services),
            "has_nodeport": any(self._is_nodeport(s) for s in services)
        }
    
    def _count_service_types(self, services: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count service types."""
        # This is simplified - would need full resource data for accurate counting
        return {
            "ClusterIP": sum(1 for s in services if 'loadbalancer' not in str(s).lower()),
            "LoadBalancer": sum(1 for s in services if self._is_loadbalancer(s)),
            "NodePort": sum(1 for s in services if self._is_nodeport(s))
        }
    
    def _is_loadbalancer(self, service: Dict[str, Any]) -> bool:
        """Check if service is LoadBalancer type."""
        return 'loadbalancer' in str(service).lower()
    
    def _is_nodeport(self, service: Dict[str, Any]) -> bool:
        """Check if service is NodePort type."""
        return 'nodeport' in str(service).lower()
    
    def _analyze_deployments(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Deployment resources."""
        deployments = [r for r in resources if r['kind'] == 'Deployment']
        
        return {
            "count": len(deployments),
            "namespaces": list(set(d['namespace'] for d in deployments)),
            "has_replicas": len(deployments) > 0  # Simplified
        }
    
    def _analyze_configmaps(self, resources: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze ConfigMap resources."""
        configmaps = [r for r in resources if r['kind'] == 'ConfigMap']
        
        return {
            "count": len(configmaps)
        }
    
    def _analyze_secrets(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Secret resources."""
        secrets = [r for r in resources if r['kind'] == 'Secret']
        
        return {
            "count": len(secrets),
            "has_secrets": len(secrets) > 0
        }
    
    def _analyze_rbac(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze RBAC resources."""
        rbac_kinds = ['Role', 'ClusterRole', 'RoleBinding', 'ClusterRoleBinding', 'ServiceAccount']
        rbac_resources = [r for r in resources if r['kind'] in rbac_kinds]
        
        return {
            "has_rbac": len(rbac_resources) > 0,
            "service_accounts": sum(1 for r in rbac_resources if r['kind'] == 'ServiceAccount'),
            "roles": sum(1 for r in rbac_resources if r['kind'] in ['Role', 'ClusterRole']),
            "bindings": sum(1 for r in rbac_resources if 'Binding' in r['kind'])
        }
    
    def _analyze_network_policies(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze NetworkPolicy resources."""
        policies = [r for r in resources if r['kind'] == 'NetworkPolicy']
        
        return {
            "count": len(policies),
            "has_network_policies": len(policies) > 0
        }
    
    def _analyze_resource_requirements(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resource requirements across all resources."""
        # Simplified analysis
        has_limits = False
        has_requests = False
        
        for resource in resources:
            resource_str = str(resource)
            if 'limits:' in resource_str:
                has_limits = True
            if 'requests:' in resource_str:
                has_requests = True
        
        return {
            "has_resource_limits": has_limits,
            "has_resource_requests": has_requests
        }
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        """Assess security practices."""
        score = 0.5
        
        # RBAC configured
        if findings.get('rbac', {}).get('has_rbac'):
            score += 0.15
        
        # Network policies
        if findings.get('network_policies', {}).get('has_network_policies'):
            score += 0.15
        
        # Not using latest tags
        images = findings.get('images', [])
        if images:
            latest_count = sum(1 for img in images if img.get('is_latest'))
            if latest_count == 0:
                score += 0.1
            elif latest_count / len(images) < 0.3:
                score += 0.05
        
        # Secrets management
        if findings.get('secrets', {}).get('has_secrets'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_best_practices(self, findings: Dict[str, Any]) -> float:
        """Assess Kubernetes best practices."""
        score = 0.5
        
        # Resource requirements defined
        resources = findings.get('resource_requirements', {})
        if resources.get('has_resource_limits'):
            score += 0.1
        if resources.get('has_resource_requests'):
            score += 0.1
        
        # Labels used
        if findings.get('labels'):
            score += 0.1
        
        # Multiple namespaces (not everything in default)
        namespaces = findings.get('namespaces', [])
        if len(namespaces) > 1 or (len(namespaces) == 1 and 'default' not in namespaces):
            score += 0.1
        
        # Using ConfigMaps
        if findings.get('configmaps', {}).get('count', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_resource_efficiency(self, findings: Dict[str, Any]) -> float:
        """Assess resource efficiency."""
        score = 0.5
        
        # Has resource requests (scheduling efficiency)
        if findings.get('resource_requirements', {}).get('has_resource_requests'):
            score += 0.2
        
        # Has resource limits (prevent resource hogging)
        if findings.get('resource_requirements', {}).get('has_resource_limits'):
            score += 0.2
        
        # Using appropriate service types
        services = findings.get('services', {})
        if services.get('count', 0) > 0 and not services.get('has_loadbalancer'):
            score += 0.1  # Not overusing LoadBalancers
        
        return min(score, 1.0)


class HelmChartHandler(DocumentHandler):
    """
    Handler for Helm chart files (Chart.yaml, values.yaml).
    
    Analyzes Helm chart structure, dependencies, and configuration
    patterns for Kubernetes package management.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Helm chart file."""
        # Helm-specific files
        helm_files = ['chart.yaml', 'chart.yml', 'values.yaml', 'values.yml', 
                     'requirements.yaml', 'requirements.yml']
        
        file_lower = file_path.lower()
        if any(file_lower.endswith(f) for f in helm_files):
            return True, 0.95
        
        # Check for values files with environment suffixes
        if re.search(r'values[.-](dev|test|staging|prod|qa)\.ya?ml$', file_lower):
            return True, 0.9
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Chart.yaml patterns
            if all(pattern in text for pattern in ['apiVersion:', 'name:', 'version:']):
                if 'description:' in text or 'appVersion:' in text:
                    return True, 0.85
            
            # values.yaml patterns (harder to detect definitively)
            if 'values' in file_lower and any(pattern in text for pattern in [
                'replicaCount:', 'image:', 'service:', 'ingress:',
                'resources:', 'nodeSelector:', 'tolerations:'
            ]):
                return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Helm file type."""
        file_lower = file_path.lower()
        
        if 'chart.yaml' in file_lower or 'chart.yml' in file_lower:
            type_name = "Helm Chart Definition"
        elif 'requirements' in file_lower:
            type_name = "Helm Requirements"
        elif 'values' in file_lower:
            # Check for environment-specific values
            env_match = re.search(r'values[.-](dev|test|staging|prod|qa)', file_lower)
            if env_match:
                env = env_match.group(1)
                type_name = f"Helm Values ({env.upper()})"
            else:
                type_name = "Helm Values"
        else:
            type_name = "Helm Configuration"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="orchestration",
            format="helm"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Helm chart analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Helm",
            category="orchestration",
            key_findings=findings,
            ai_use_cases=[
                "Multi-environment configuration management",
                "Dependency version updates",
                "Security scanning integration",
                "Value validation and defaults",
                "Chart testing automation",
                "Release management"
            ],
            quality_metrics={
                "chart_quality": self._assess_chart_quality(findings),
                "configuration_flexibility": self._assess_flexibility(findings),
                "security": self._assess_security(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Helm chart data."""
        text = content.decode('utf-8', errors='ignore')
        file_lower = file_path.lower()
        
        try:
            data = yaml.safe_load(text)
            if not isinstance(data, dict):
                return {"error": "Invalid YAML structure"}
            
            if 'chart.yaml' in file_lower or 'chart.yml' in file_lower:
                return self._analyze_chart_yaml(data)
            elif 'values' in file_lower:
                return self._analyze_values_yaml(data, file_path)
            elif 'requirements' in file_lower:
                return self._analyze_requirements_yaml(data)
            else:
                return {"file_type": "unknown", "data": data}
                
        except Exception as e:
            return {"error": f"Failed to parse Helm YAML: {str(e)}"}
    
    def _analyze_chart_yaml(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Chart.yaml file."""
        return {
            "file_type": "chart",
            "apiVersion": data.get('apiVersion', 'v1'),
            "name": data.get('name', 'unknown'),
            "version": data.get('version', '0.0.0'),
            "appVersion": data.get('appVersion'),
            "description": data.get('description', ''),
            "type": data.get('type', 'application'),
            "keywords": data.get('keywords', []),
            "home": data.get('home'),
            "sources": data.get('sources', []),
            "dependencies": self._analyze_dependencies(data.get('dependencies', [])),
            "maintainers": data.get('maintainers', []),
            "icon": data.get('icon'),
            "deprecated": data.get('deprecated', False),
            "annotations": data.get('annotations', {}),
            "kubeVersion": data.get('kubeVersion')
        }
    
    def _analyze_dependencies(self, dependencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze chart dependencies."""
        return {
            "count": len(dependencies),
            "charts": [
                {
                    "name": dep.get('name'),
                    "version": dep.get('version'),
                    "repository": dep.get('repository'),
                    "condition": dep.get('condition'),
                    "enabled": dep.get('enabled', True)
                }
                for dep in dependencies
            ],
            "has_conditions": any('condition' in dep for dep in dependencies),
            "repositories": list(set(dep.get('repository', '') for dep in dependencies if dep.get('repository')))
        }
    
    def _analyze_values_yaml(self, data: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Analyze values.yaml file."""
        # Detect environment from filename
        env_match = re.search(r'values[.-](dev|test|staging|prod|qa)', file_path.lower())
        environment = env_match.group(1) if env_match else 'default'
        
        return {
            "file_type": "values",
            "environment": environment,
            "sections": list(data.keys()),
            "has_image_config": 'image' in data,
            "has_ingress": 'ingress' in data,
            "has_service": 'service' in data,
            "has_resources": 'resources' in data,
            "has_autoscaling": 'autoscaling' in data or 'hpa' in data,
            "has_persistence": 'persistence' in data or 'volumeClaimTemplates' in data,
            "has_security_context": 'securityContext' in data or 'podSecurityContext' in data,
            "has_probes": any(probe in str(data) for probe in ['livenessProbe', 'readinessProbe', 'startupProbe']),
            "image_details": self._extract_image_details(data.get('image', {})),
            "replica_count": data.get('replicaCount'),
            "service_type": data.get('service', {}).get('type'),
            "ingress_enabled": data.get('ingress', {}).get('enabled', False),
            "custom_values": self._identify_custom_values(data)
        }
    
    def _extract_image_details(self, image_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract image configuration details."""
        if not isinstance(image_config, dict):
            return {}
        
        return {
            "repository": image_config.get('repository'),
            "tag": image_config.get('tag'),
            "pull_policy": image_config.get('pullPolicy'),
            "has_pull_secrets": bool(image_config.get('pullSecrets'))
        }
    
    def _identify_custom_values(self, data: Dict[str, Any]) -> List[str]:
        """Identify custom/application-specific values."""
        standard_keys = {
            'replicaCount', 'image', 'imagePullSecrets', 'nameOverride',
            'fullnameOverride', 'serviceAccount', 'podAnnotations',
            'podSecurityContext', 'securityContext', 'service', 'ingress',
            'resources', 'autoscaling', 'nodeSelector', 'tolerations',
            'affinity', 'persistence', 'volumeMounts', 'volumes'
        }
        
        custom_keys = []
        for key in data.keys():
            if key not in standard_keys:
                custom_keys.append(key)
        
        return custom_keys
    
    def _analyze_requirements_yaml(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements.yaml (Helm v2 style)."""
        dependencies = data.get('dependencies', [])
        
        return {
            "file_type": "requirements",
            "dependencies": self._analyze_dependencies(dependencies),
            "helm_version": "v2"  # requirements.yaml is Helm v2
        }
    
    def _assess_chart_quality(self, findings: Dict[str, Any]) -> float:
        """Assess Helm chart quality."""
        score = 0.5
        
        if findings.get('file_type') == 'chart':
            # Has proper metadata
            if findings.get('description'):
                score += 0.1
            if findings.get('maintainers'):
                score += 0.1
            if findings.get('version') and findings.get('version') != '0.0.0':
                score += 0.1
            if findings.get('appVersion'):
                score += 0.1
            if findings.get('sources'):
                score += 0.05
            if findings.get('home'):
                score += 0.05
        
        elif findings.get('file_type') == 'values':
            # Has security configurations
            if findings.get('has_security_context'):
                score += 0.15
            # Has health checks
            if findings.get('has_probes'):
                score += 0.15
            # Has resource limits
            if findings.get('has_resources'):
                score += 0.1
            # Has proper image configuration
            if findings.get('has_image_config'):
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_flexibility(self, findings: Dict[str, Any]) -> float:
        """Assess configuration flexibility."""
        score = 0.5
        
        if findings.get('file_type') == 'values':
            # Has multiple configuration sections
            sections = findings.get('sections', [])
            if len(sections) > 5:
                score += 0.1
            
            # Has custom values (extensible)
            if findings.get('custom_values'):
                score += 0.15
            
            # Has optional features
            if findings.get('has_ingress'):
                score += 0.05
            if findings.get('has_autoscaling'):
                score += 0.05
            if findings.get('has_persistence'):
                score += 0.05
            
            # Environment-specific values
            if findings.get('environment') != 'default':
                score += 0.1
        
        elif findings.get('file_type') == 'chart':
            # Has conditional dependencies
            deps = findings.get('dependencies', {})
            if deps.get('has_conditions'):
                score += 0.2
            
            # Multiple dependencies (modular)
            if deps.get('count', 0) > 2:
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        """Assess security configurations."""
        score = 0.5
        
        if findings.get('file_type') == 'values':
            # Security context defined
            if findings.get('has_security_context'):
                score += 0.2
            
            # Image pull policy
            image = findings.get('image_details', {})
            if image.get('pull_policy') == 'Always':
                score += 0.1
            
            # Not using latest tag
            if image.get('tag') and image.get('tag') != 'latest':
                score += 0.1
            
            # Has pull secrets
            if image.get('has_pull_secrets'):
                score += 0.1
        
        elif findings.get('file_type') == 'chart':
            # Not deprecated
            if not findings.get('deprecated'):
                score += 0.1
            
            # Has Kubernetes version constraint
            if findings.get('kubeVersion'):
                score += 0.1
        
        return min(score, 1.0) 