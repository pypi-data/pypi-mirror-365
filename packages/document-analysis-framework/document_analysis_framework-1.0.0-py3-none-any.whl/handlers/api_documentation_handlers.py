"""
API documentation handlers for OpenAPI/Swagger specifications

Handles analysis of API documentation files including OpenAPI 3.x
and Swagger 2.0 specifications in YAML and JSON formats.
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


class OpenAPIHandler(DocumentHandler):
    """
    Handler for OpenAPI/Swagger specification files.
    
    Analyzes API specifications including endpoints, schemas,
    security definitions, and API design patterns.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the OpenAPI file."""
        file_lower = file_path.lower()
        
        # Common OpenAPI/Swagger file names
        openapi_patterns = [
            'openapi.yaml', 'openapi.yml', 'openapi.json',
            'swagger.yaml', 'swagger.yml', 'swagger.json',
            'api.yaml', 'api.yml', 'api.json',
            'spec.yaml', 'spec.yml', 'spec.json'
        ]
        
        if any(pattern in file_lower for pattern in openapi_patterns):
            return True, 0.9
        
        try:
            text = content.decode('utf-8', errors='ignore')
            
            # Try JSON first
            try:
                data = json.loads(text)
                if self._is_openapi_spec(data):
                    return True, 0.95
            except:
                # Try YAML
                try:
                    data = yaml.safe_load(text)
                    if self._is_openapi_spec(data):
                        return True, 0.95
                except:
                    pass
        except:
            pass
        
        return False, 0.0
    
    def _is_openapi_spec(self, data: Dict[str, Any]) -> bool:
        """Check if data structure is an OpenAPI specification."""
        if not isinstance(data, dict):
            return False
        
        # OpenAPI 3.x
        if 'openapi' in data and data['openapi'].startswith('3.'):
            return True
        
        # Swagger 2.0
        if 'swagger' in data and data['swagger'] == '2.0':
            return True
        
        # Additional checks for API specs
        if all(key in data for key in ['info', 'paths']):
            return True
        
        return False
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect OpenAPI version and format."""
        text = content.decode('utf-8', errors='ignore')
        
        # Determine format
        is_json = False
        try:
            data = json.loads(text)
            is_json = True
        except:
            try:
                data = yaml.safe_load(text)
            except:
                return DocumentTypeInfo(
                    type_name="Invalid API Specification",
                    confidence=0.5,
                    category="api",
                    format="unknown"
                )
        
        # Determine version
        version = "unknown"
        if 'openapi' in data:
            version = data['openapi']
            spec_type = f"OpenAPI {version}"
        elif 'swagger' in data:
            version = data['swagger']
            spec_type = f"Swagger {version}"
        else:
            spec_type = "API Specification"
        
        format_str = "JSON" if is_json else "YAML"
        
        return DocumentTypeInfo(
            type_name=f"{spec_type} ({format_str})",
            confidence=0.95,
            category="api",
            format="openapi"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed OpenAPI analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="OpenAPI",
            category="api",
            key_findings=findings,
            ai_use_cases=[
                "API client code generation",
                "API documentation generation",
                "Contract testing setup",
                "Security audit and improvements",
                "API versioning strategy",
                "Mock server generation"
            ],
            quality_metrics={
                "api_design": self._assess_api_design(findings),
                "documentation_quality": self._assess_documentation(findings),
                "security": self._assess_security(findings),
                "ai_readiness": 0.95
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract OpenAPI specification data."""
        text = content.decode('utf-8', errors='ignore')
        
        # Parse specification
        try:
            try:
                data = json.loads(text)
                format_type = "json"
            except:
                data = yaml.safe_load(text)
                format_type = "yaml"
        except Exception as e:
            return {"error": f"Failed to parse API specification: {str(e)}"}
        
        # Determine OpenAPI version
        if 'openapi' in data:
            return self._analyze_openapi_3(data, format_type)
        elif 'swagger' in data:
            return self._analyze_swagger_2(data, format_type)
        else:
            return {"error": "Unknown API specification format"}
    
    def _analyze_openapi_3(self, spec: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """Analyze OpenAPI 3.x specification."""
        analysis = {
            "format": format_type,
            "version": spec.get('openapi', '3.0.0'),
            "info": self._analyze_info(spec.get('info', {})),
            "servers": self._analyze_servers(spec.get('servers', [])),
            "paths": self._analyze_paths(spec.get('paths', {})),
            "components": self._analyze_components(spec.get('components', {})),
            "security": self._analyze_security_schemes(spec.get('components', {}).get('securitySchemes', {})),
            "tags": spec.get('tags', []),
            "external_docs": spec.get('externalDocs'),
            "webhooks": self._analyze_webhooks(spec.get('webhooks', {})),
            "statistics": self._calculate_statistics(spec)
        }
        
        return analysis
    
    def _analyze_swagger_2(self, spec: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """Analyze Swagger 2.0 specification."""
        analysis = {
            "format": format_type,
            "version": spec.get('swagger', '2.0'),
            "info": self._analyze_info(spec.get('info', {})),
            "host": spec.get('host'),
            "basePath": spec.get('basePath', '/'),
            "schemes": spec.get('schemes', []),
            "paths": self._analyze_paths(spec.get('paths', {})),
            "definitions": self._analyze_definitions(spec.get('definitions', {})),
            "security": self._analyze_security_definitions(spec.get('securityDefinitions', {})),
            "tags": spec.get('tags', []),
            "external_docs": spec.get('externalDocs'),
            "statistics": self._calculate_statistics(spec)
        }
        
        return analysis
    
    def _analyze_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API info section."""
        return {
            "title": info.get('title', 'Untitled API'),
            "version": info.get('version', '1.0.0'),
            "description": info.get('description', ''),
            "has_description": bool(info.get('description')),
            "has_terms_of_service": bool(info.get('termsOfService')),
            "has_contact": bool(info.get('contact')),
            "has_license": bool(info.get('license')),
            "license_name": info.get('license', {}).get('name') if isinstance(info.get('license'), dict) else None
        }
    
    def _analyze_servers(self, servers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze server configurations (OpenAPI 3.x)."""
        analyzed_servers = []
        
        for server in servers:
            if isinstance(server, dict):
                analyzed_servers.append({
                    "url": server.get('url', ''),
                    "description": server.get('description', ''),
                    "has_variables": bool(server.get('variables'))
                })
        
        return analyzed_servers
    
    def _analyze_paths(self, paths: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API paths/endpoints."""
        analysis = {
            "total_endpoints": 0,
            "methods": {},
            "endpoints": [],
            "parameters": {
                "path": 0,
                "query": 0,
                "header": 0,
                "cookie": 0
            },
            "has_examples": False,
            "has_descriptions": 0,
            "deprecated_count": 0
        }
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            
            # Analyze each HTTP method
            for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                if method in path_item:
                    operation = path_item[method]
                    if isinstance(operation, dict):
                        analysis['total_endpoints'] += 1
                        analysis['methods'][method] = analysis['methods'].get(method, 0) + 1
                        
                        endpoint_info = {
                            "path": path,
                            "method": method.upper(),
                            "operation_id": operation.get('operationId'),
                            "summary": operation.get('summary'),
                            "has_description": bool(operation.get('description')),
                            "has_parameters": bool(operation.get('parameters')),
                            "has_request_body": bool(operation.get('requestBody')),
                            "has_responses": bool(operation.get('responses')),
                            "tags": operation.get('tags', []),
                            "deprecated": operation.get('deprecated', False)
                        }
                        
                        # Count descriptions
                        if endpoint_info['has_description']:
                            analysis['has_descriptions'] += 1
                        
                        # Count deprecated
                        if endpoint_info['deprecated']:
                            analysis['deprecated_count'] += 1
                        
                        # Analyze parameters
                        for param in operation.get('parameters', []):
                            if isinstance(param, dict):
                                param_in = param.get('in', 'query')
                                if param_in in analysis['parameters']:
                                    analysis['parameters'][param_in] += 1
                        
                        # Check for examples
                        if self._has_examples(operation):
                            analysis['has_examples'] = True
                        
                        analysis['endpoints'].append(endpoint_info)
        
        return analysis
    
    def _has_examples(self, operation: Dict[str, Any]) -> bool:
        """Check if operation has examples."""
        # Check responses for examples
        responses = operation.get('responses', {})
        for response in responses.values():
            if isinstance(response, dict):
                # OpenAPI 3.x
                if 'content' in response:
                    for content in response['content'].values():
                        if isinstance(content, dict) and ('example' in content or 'examples' in content):
                            return True
                # Swagger 2.0
                if 'examples' in response:
                    return True
        
        # Check request body for examples (OpenAPI 3.x)
        request_body = operation.get('requestBody', {})
        if isinstance(request_body, dict) and 'content' in request_body:
            for content in request_body['content'].values():
                if isinstance(content, dict) and ('example' in content or 'examples' in content):
                    return True
        
        return False
    
    def _analyze_components(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze components section (OpenAPI 3.x)."""
        return {
            "schemas": len(components.get('schemas', {})),
            "responses": len(components.get('responses', {})),
            "parameters": len(components.get('parameters', {})),
            "examples": len(components.get('examples', {})),
            "request_bodies": len(components.get('requestBodies', {})),
            "headers": len(components.get('headers', {})),
            "security_schemes": len(components.get('securitySchemes', {})),
            "links": len(components.get('links', {})),
            "callbacks": len(components.get('callbacks', {}))
        }
    
    def _analyze_definitions(self, definitions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze definitions section (Swagger 2.0)."""
        return {
            "total_schemas": len(definitions),
            "schema_names": list(definitions.keys())[:20]  # First 20
        }
    
    def _analyze_security_schemes(self, schemes: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security schemes (OpenAPI 3.x)."""
        analysis = {
            "total_schemes": len(schemes),
            "types": {},
            "oauth2_flows": [],
            "api_key_locations": []
        }
        
        for name, scheme in schemes.items():
            if isinstance(scheme, dict):
                scheme_type = scheme.get('type', 'unknown')
                analysis['types'][scheme_type] = analysis['types'].get(scheme_type, 0) + 1
                
                # OAuth2 specific
                if scheme_type == 'oauth2' and 'flows' in scheme:
                    analysis['oauth2_flows'].extend(list(scheme['flows'].keys()))
                
                # API Key specific
                if scheme_type == 'apiKey':
                    location = scheme.get('in', 'unknown')
                    if location not in analysis['api_key_locations']:
                        analysis['api_key_locations'].append(location)
        
        return analysis
    
    def _analyze_security_definitions(self, definitions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security definitions (Swagger 2.0)."""
        analysis = {
            "total_schemes": len(definitions),
            "types": {},
            "oauth2_flows": [],
            "api_key_locations": []
        }
        
        for name, definition in definitions.items():
            if isinstance(definition, dict):
                def_type = definition.get('type', 'unknown')
                analysis['types'][def_type] = analysis['types'].get(def_type, 0) + 1
                
                # OAuth2 specific
                if def_type == 'oauth2':
                    flow = definition.get('flow')
                    if flow and flow not in analysis['oauth2_flows']:
                        analysis['oauth2_flows'].append(flow)
                
                # API Key specific
                if def_type == 'apiKey':
                    location = definition.get('in', 'unknown')
                    if location not in analysis['api_key_locations']:
                        analysis['api_key_locations'].append(location)
        
        return analysis
    
    def _analyze_webhooks(self, webhooks: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze webhooks (OpenAPI 3.1+)."""
        return {
            "total_webhooks": len(webhooks),
            "webhook_names": list(webhooks.keys())[:10]  # First 10
        }
    
    def _calculate_statistics(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall API statistics."""
        stats = {
            "total_paths": len(spec.get('paths', {})),
            "total_operations": 0,
            "has_external_docs": bool(spec.get('externalDocs')),
            "tag_count": len(spec.get('tags', [])),
            "content_types": set(),
            "response_codes": set()
        }
        
        # Count operations and analyze content types
        paths = spec.get('paths', {})
        for path_item in paths.values():
            if isinstance(path_item, dict):
                for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    if method in path_item:
                        stats['total_operations'] += 1
                        operation = path_item[method]
                        
                        # Analyze content types (OpenAPI 3.x)
                        if isinstance(operation, dict):
                            # Request content types
                            request_body = operation.get('requestBody', {})
                            if isinstance(request_body, dict) and 'content' in request_body:
                                stats['content_types'].update(request_body['content'].keys())
                            
                            # Response content types
                            responses = operation.get('responses', {})
                            for code, response in responses.items():
                                stats['response_codes'].add(code)
                                if isinstance(response, dict) and 'content' in response:
                                    stats['content_types'].update(response['content'].keys())
                            
                            # Swagger 2.0 content types
                            if 'produces' in operation:
                                stats['content_types'].update(operation['produces'])
                            if 'consumes' in operation:
                                stats['content_types'].update(operation['consumes'])
        
        # Convert sets to lists
        stats['content_types'] = list(stats['content_types'])
        stats['response_codes'] = list(stats['response_codes'])
        
        return stats
    
    def _assess_api_design(self, findings: Dict[str, Any]) -> float:
        """Assess API design quality."""
        score = 0.5
        
        # RESTful design (variety of HTTP methods)
        methods = findings.get('paths', {}).get('methods', {})
        if len(methods) >= 3:  # Using GET, POST, PUT/PATCH, DELETE
            score += 0.15
        
        # Consistent naming (operationIds present)
        endpoints = findings.get('paths', {}).get('endpoints', [])
        if endpoints:
            with_operation_ids = sum(1 for e in endpoints if e.get('operation_id'))
            if with_operation_ids / len(endpoints) > 0.8:
                score += 0.1
        
        # Proper status codes used
        response_codes = findings.get('statistics', {}).get('response_codes', [])
        if len(response_codes) > 3:  # Using various status codes
            score += 0.1
        
        # API versioning
        info = findings.get('info', {})
        if info.get('version') and info['version'] != '1.0.0':
            score += 0.05
        
        # Using tags for organization
        if findings.get('tags'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_documentation(self, findings: Dict[str, Any]) -> float:
        """Assess documentation quality."""
        score = 0.5
        
        # API description
        info = findings.get('info', {})
        if info.get('has_description'):
            score += 0.1
        
        # Contact information
        if info.get('has_contact'):
            score += 0.05
        
        # License information
        if info.get('has_license'):
            score += 0.05
        
        # Endpoint descriptions
        paths = findings.get('paths', {})
        total_endpoints = paths.get('total_endpoints', 0)
        described_endpoints = paths.get('has_descriptions', 0)
        
        if total_endpoints > 0:
            description_ratio = described_endpoints / total_endpoints
            if description_ratio > 0.8:
                score += 0.15
            elif description_ratio > 0.5:
                score += 0.1
        
        # Examples provided
        if paths.get('has_examples'):
            score += 0.1
        
        # External documentation
        if findings.get('statistics', {}).get('has_external_docs'):
            score += 0.05
        
        return min(score, 1.0)
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        """Assess API security configuration."""
        score = 0.5
        
        # Has security schemes defined
        security = findings.get('security', {})
        if security.get('total_schemes', 0) > 0:
            score += 0.2
            
            # Using modern auth methods
            types = security.get('types', {})
            if 'oauth2' in types or 'openIdConnect' in types:
                score += 0.1
            
            # API keys not in URL
            api_key_locations = security.get('api_key_locations', [])
            if 'query' not in api_key_locations and api_key_locations:
                score += 0.1
        
        # HTTPS usage (OpenAPI 3.x servers or Swagger 2.0 schemes)
        servers = findings.get('servers', [])
        if servers:
            https_servers = sum(1 for s in servers if s.get('url', '').startswith('https://'))
            if servers and https_servers == len(servers):
                score += 0.1
        else:
            schemes = findings.get('schemes', [])
            if 'https' in schemes and 'http' not in schemes:
                score += 0.1
        
        return min(score, 1.0) 