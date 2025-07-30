"""
API definition handlers for GraphQL and Protocol Buffers

Handles analysis of API schema and service definition files including
GraphQL schemas and Protocol Buffer definitions.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class GraphQLHandler(DocumentHandler):
    """
    Handler for GraphQL schema and query files (.graphql, .gql).
    
    Analyzes GraphQL schemas including types, queries, mutations,
    subscriptions, and directives.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the GraphQL file."""
        if file_path.endswith(('.graphql', '.gql')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # GraphQL patterns
            if any(pattern in text for pattern in [
                'type Query', 'type Mutation', 'type Subscription',
                'schema {', 'scalar ', 'enum ', 'interface ',
                'query ', 'mutation ', 'subscription ',
                'fragment ', 'directive @'
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect GraphQL file type."""
        text = content.decode('utf-8', errors='ignore')
        
        # Determine if it's a schema or query file
        if any(pattern in text for pattern in ['type Query', 'type Mutation', 'schema {']):
            type_name = "GraphQL Schema"
        elif any(pattern in text for pattern in ['query ', 'mutation ', 'subscription ']):
            type_name = "GraphQL Operations"
        else:
            type_name = "GraphQL Definition"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="api",
            format="graphql"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed GraphQL analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="GraphQL",
            category="api",
            key_findings=findings,
            ai_use_cases=[
                "Schema optimization and validation",
                "Query complexity analysis",
                "Type generation for clients",
                "Documentation generation",
                "Schema stitching and federation",
                "Performance optimization"
            ],
            quality_metrics={
                "schema_design": self._assess_schema_design(findings),
                "type_safety": self._assess_type_safety(findings),
                "complexity": self._assess_complexity(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract GraphQL schema and query data."""
        text = content.decode('utf-8', errors='ignore')
        
        # Remove comments for analysis
        text_no_comments = re.sub(r'#[^\n]*', '', text)
        
        return {
            "types": self._extract_types(text_no_comments),
            "operations": self._extract_operations(text_no_comments),
            "fields": self._extract_fields(text_no_comments),
            "directives": self._extract_directives(text_no_comments),
            "scalars": self._extract_scalars(text_no_comments),
            "enums": self._extract_enums(text_no_comments),
            "interfaces": self._extract_interfaces(text_no_comments),
            "unions": self._extract_unions(text_no_comments),
            "fragments": self._extract_fragments(text_no_comments),
            "schema_definition": self._extract_schema_definition(text_no_comments),
            "comments": len(re.findall(r'#[^\n]*', text)),
            "documentation": self._extract_documentation(text)
        }
    
    def _extract_types(self, text: str) -> Dict[str, Any]:
        """Extract type definitions."""
        types = {
            "object_types": [],
            "input_types": [],
            "total_count": 0
        }
        
        # Object types
        for match in re.finditer(r'type\s+(\w+)(?:\s+implements\s+([^{]+))?\s*{', text):
            type_name = match.group(1)
            implements = match.group(2)
            
            if type_name not in ['Query', 'Mutation', 'Subscription']:
                types["object_types"].append({
                    "name": type_name,
                    "implements": implements.strip().split('&') if implements else []
                })
        
        # Input types
        for match in re.finditer(r'input\s+(\w+)\s*{', text):
            types["input_types"].append(match.group(1))
        
        types["total_count"] = len(types["object_types"]) + len(types["input_types"])
        
        return types
    
    def _extract_operations(self, text: str) -> Dict[str, Any]:
        """Extract GraphQL operations."""
        operations = {
            "queries": [],
            "mutations": [],
            "subscriptions": []
        }
        
        # Schema operations (from type Query/Mutation/Subscription)
        query_type = self._extract_type_fields(text, "Query")
        operations["queries"] = [f["name"] for f in query_type]
        
        mutation_type = self._extract_type_fields(text, "Mutation")
        operations["mutations"] = [f["name"] for f in mutation_type]
        
        subscription_type = self._extract_type_fields(text, "Subscription")
        operations["subscriptions"] = [f["name"] for f in subscription_type]
        
        # Also look for operation definitions (in .gql files)
        operations["query_definitions"] = len(re.findall(r'query\s+\w+', text))
        operations["mutation_definitions"] = len(re.findall(r'mutation\s+\w+', text))
        operations["subscription_definitions"] = len(re.findall(r'subscription\s+\w+', text))
        
        return operations
    
    def _extract_type_fields(self, text: str, type_name: str) -> List[Dict[str, Any]]:
        """Extract fields from a specific type."""
        fields = []
        
        # Find the type definition
        type_match = re.search(rf'type\s+{type_name}\s*{{([^}}]+)}}', text, re.DOTALL)
        if not type_match:
            return fields
        
        type_content = type_match.group(1)
        
        # Extract fields
        for match in re.finditer(r'(\w+)(?:\(([^)]*)\))?\s*:\s*([^!\n]+)(!)?', type_content):
            field_name = match.group(1)
            args = match.group(2)
            return_type = match.group(3).strip()
            required = bool(match.group(4))
            
            field_info = {
                "name": field_name,
                "type": return_type,
                "required": required,
                "has_arguments": bool(args)
            }
            
            if args:
                field_info["argument_count"] = len(args.split(','))
            
            fields.append(field_info)
        
        return fields
    
    def _extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract general field statistics."""
        # Count different field patterns
        total_fields = len(re.findall(r'\w+\s*:\s*\w+', text))
        required_fields = len(re.findall(r'\w+\s*:\s*[^!]+!', text))
        list_fields = len(re.findall(r'\w+\s*:\s*\[[^\]]+\]', text))
        
        return {
            "total_count": total_fields,
            "required_count": required_fields,
            "list_count": list_fields,
            "nullable_count": total_fields - required_fields
        }
    
    def _extract_directives(self, text: str) -> List[Dict[str, Any]]:
        """Extract directive definitions and usage."""
        directives = []
        
        # Directive definitions
        for match in re.finditer(r'directive\s+@(\w+)(?:\(([^)]*)\))?\s+on\s+([^\n]+)', text):
            directive_name = match.group(1)
            args = match.group(2)
            locations = match.group(3).strip()
            
            directives.append({
                "name": directive_name,
                "has_arguments": bool(args),
                "locations": [loc.strip() for loc in locations.split('|')]
            })
        
        # Common directive usage
        deprecated_count = len(re.findall(r'@deprecated', text))
        if deprecated_count > 0:
            directives.append({
                "name": "deprecated",
                "usage_count": deprecated_count,
                "is_builtin": True
            })
        
        return directives
    
    def _extract_scalars(self, text: str) -> List[str]:
        """Extract scalar type definitions."""
        scalars = re.findall(r'scalar\s+(\w+)', text)
        return list(set(scalars))
    
    def _extract_enums(self, text: str) -> List[Dict[str, Any]]:
        """Extract enum definitions."""
        enums = []
        
        for match in re.finditer(r'enum\s+(\w+)\s*{([^}]+)}', text, re.DOTALL):
            enum_name = match.group(1)
            enum_content = match.group(2)
            
            # Count enum values
            values = re.findall(r'^\s*(\w+)', enum_content, re.MULTILINE)
            
            enums.append({
                "name": enum_name,
                "value_count": len(values),
                "values": values[:10]  # First 10 values
            })
        
        return enums
    
    def _extract_interfaces(self, text: str) -> List[Dict[str, Any]]:
        """Extract interface definitions."""
        interfaces = []
        
        for match in re.finditer(r'interface\s+(\w+)\s*{', text):
            interface_name = match.group(1)
            
            # Find implementing types
            implementers = re.findall(rf'type\s+\w+\s+implements\s+[^{{]*{interface_name}', text)
            
            interfaces.append({
                "name": interface_name,
                "implementer_count": len(implementers)
            })
        
        return interfaces
    
    def _extract_unions(self, text: str) -> List[Dict[str, Any]]:
        """Extract union type definitions."""
        unions = []
        
        for match in re.finditer(r'union\s+(\w+)\s*=\s*([^\n]+)', text):
            union_name = match.group(1)
            union_types = match.group(2).strip()
            
            types = [t.strip() for t in union_types.split('|')]
            
            unions.append({
                "name": union_name,
                "type_count": len(types),
                "types": types
            })
        
        return unions
    
    def _extract_fragments(self, text: str) -> List[Dict[str, str]]:
        """Extract fragment definitions."""
        fragments = []
        
        for match in re.finditer(r'fragment\s+(\w+)\s+on\s+(\w+)', text):
            fragments.append({
                "name": match.group(1),
                "type": match.group(2)
            })
        
        return fragments
    
    def _extract_schema_definition(self, text: str) -> Dict[str, Any]:
        """Extract explicit schema definition."""
        schema_match = re.search(r'schema\s*{([^}]+)}', text, re.DOTALL)
        
        if schema_match:
            schema_content = schema_match.group(1)
            
            query_match = re.search(r'query:\s*(\w+)', schema_content)
            mutation_match = re.search(r'mutation:\s*(\w+)', schema_content)
            subscription_match = re.search(r'subscription:\s*(\w+)', schema_content)
            
            return {
                "has_explicit_schema": True,
                "query_type": query_match.group(1) if query_match else "Query",
                "mutation_type": mutation_match.group(1) if mutation_match else None,
                "subscription_type": subscription_match.group(1) if subscription_match else None
            }
        
        return {"has_explicit_schema": False}
    
    def _extract_documentation(self, text: str) -> Dict[str, Any]:
        """Extract documentation strings."""
        # GraphQL uses """ for documentation
        doc_strings = re.findall(r'"""([^"]+)"""', text, re.DOTALL)
        
        return {
            "count": len(doc_strings),
            "total_length": sum(len(doc) for doc in doc_strings),
            "has_documentation": len(doc_strings) > 0
        }
    
    def _assess_schema_design(self, findings: Dict[str, Any]) -> float:
        """Assess GraphQL schema design quality."""
        score = 0.5
        
        # Has documentation
        if findings.get('documentation', {}).get('has_documentation'):
            score += 0.15
        
        # Uses interfaces or unions for polymorphism
        if findings.get('interfaces') or findings.get('unions'):
            score += 0.1
        
        # Has custom scalars for type safety
        if findings.get('scalars'):
            score += 0.1
        
        # Reasonable number of types
        type_count = findings.get('types', {}).get('total_count', 0)
        if 5 <= type_count <= 50:
            score += 0.1
        
        # Has input types for mutations
        if findings.get('types', {}).get('input_types'):
            score += 0.05
        
        return min(score, 1.0)
    
    def _assess_type_safety(self, findings: Dict[str, Any]) -> float:
        """Assess type safety practices."""
        score = 0.5
        
        # Using required fields appropriately
        fields = findings.get('fields', {})
        total_fields = fields.get('total_count', 0)
        required_fields = fields.get('required_count', 0)
        
        if total_fields > 0:
            required_ratio = required_fields / total_fields
            if 0.3 <= required_ratio <= 0.7:  # Good balance
                score += 0.2
        
        # Using enums for constrained values
        if findings.get('enums'):
            score += 0.1
        
        # Custom scalars for domain types
        if findings.get('scalars'):
            score += 0.1
        
        # Input types for mutations (type safety)
        if findings.get('types', {}).get('input_types'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_complexity(self, findings: Dict[str, Any]) -> float:
        """Assess schema complexity (lower score = more complex)."""
        score = 1.0
        
        # Too many types
        type_count = findings.get('types', {}).get('total_count', 0)
        if type_count > 100:
            score -= 0.2
        elif type_count > 50:
            score -= 0.1
        
        # Deep nesting (many list fields)
        list_fields = findings.get('fields', {}).get('list_count', 0)
        if list_fields > 50:
            score -= 0.1
        
        # Many operations
        operations = findings.get('operations', {})
        total_ops = len(operations.get('queries', [])) + len(operations.get('mutations', []))
        if total_ops > 100:
            score -= 0.1
        
        return max(score, 0.3)


class ProtocolBuffersHandler(DocumentHandler):
    """
    Handler for Protocol Buffers definition files (.proto).
    
    Analyzes protobuf schemas including messages, services, enums,
    and RPC definitions.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Protocol Buffers file."""
        if file_path.endswith('.proto'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Protobuf patterns
            if any(pattern in text for pattern in [
                'syntax = "proto', 'message ', 'service ',
                'rpc ', 'enum ', 'import "',
                'package ', 'option ', 'repeated '
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Protocol Buffers version and type."""
        text = content.decode('utf-8', errors='ignore')
        
        # Detect proto version
        version = "proto2"  # Default
        syntax_match = re.search(r'syntax\s*=\s*"(proto\d)"', text)
        if syntax_match:
            version = syntax_match.group(1)
        
        # Detect if it's primarily service or message definitions
        has_services = 'service ' in text
        has_messages = 'message ' in text
        
        if has_services and not has_messages:
            type_name = f"Protocol Buffers Service ({version})"
        elif has_messages and not has_services:
            type_name = f"Protocol Buffers Messages ({version})"
        else:
            type_name = f"Protocol Buffers Definition ({version})"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="api",
            format="protobuf"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Protocol Buffers analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Protocol Buffers",
            category="api",
            key_findings=findings,
            ai_use_cases=[
                "Code generation for multiple languages",
                "API documentation generation",
                "Schema evolution and versioning",
                "Service stub generation",
                "Validation rule generation",
                "gRPC service implementation"
            ],
            quality_metrics={
                "schema_design": self._assess_schema_design(findings),
                "compatibility": self._assess_compatibility(findings),
                "documentation": self._assess_documentation(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Protocol Buffers schema data."""
        text = content.decode('utf-8', errors='ignore')
        
        # Remove comments for analysis
        text_no_comments = self._remove_comments(text)
        
        return {
            "syntax": self._extract_syntax(text_no_comments),
            "package": self._extract_package(text_no_comments),
            "imports": self._extract_imports(text_no_comments),
            "options": self._extract_options(text_no_comments),
            "messages": self._extract_messages(text_no_comments),
            "services": self._extract_services(text_no_comments),
            "enums": self._extract_enums(text_no_comments),
            "fields": self._analyze_fields(text_no_comments),
            "rpcs": self._extract_rpcs(text_no_comments),
            "comments": self._count_comments(text),
            "extensions": self._extract_extensions(text_no_comments)
        }
    
    def _remove_comments(self, text: str) -> str:
        """Remove comments from protobuf text."""
        # Remove single-line comments
        text = re.sub(r'//[^\n]*', '', text)
        # Remove multi-line comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        return text
    
    def _count_comments(self, text: str) -> Dict[str, int]:
        """Count different types of comments."""
        single_line = len(re.findall(r'//[^\n]*', text))
        multi_line = len(re.findall(r'/\*.*?\*/', text, re.DOTALL))
        
        return {
            "single_line": single_line,
            "multi_line": multi_line,
            "total": single_line + multi_line
        }
    
    def _extract_syntax(self, text: str) -> str:
        """Extract syntax version."""
        match = re.search(r'syntax\s*=\s*"(proto\d)"', text)
        return match.group(1) if match else "proto2"
    
    def _extract_package(self, text: str) -> Optional[str]:
        """Extract package name."""
        match = re.search(r'package\s+([\w.]+);', text)
        return match.group(1) if match else None
    
    def _extract_imports(self, text: str) -> List[Dict[str, Any]]:
        """Extract import statements."""
        imports = []
        
        for match in re.finditer(r'import\s+("([^"]+)"|public\s+"([^"]+)");', text):
            if match.group(2):  # Regular import
                imports.append({
                    "path": match.group(2),
                    "public": False
                })
            else:  # Public import
                imports.append({
                    "path": match.group(3),
                    "public": True
                })
        
        return imports
    
    def _extract_options(self, text: str) -> List[Dict[str, str]]:
        """Extract option statements."""
        options = []
        
        for match in re.finditer(r'option\s+(\w+(?:\.\w+)*)\s*=\s*([^;]+);', text):
            options.append({
                "name": match.group(1),
                "value": match.group(2).strip()
            })
        
        return options
    
    def _extract_messages(self, text: str) -> List[Dict[str, Any]]:
        """Extract message definitions."""
        messages = []
        
        # Find all message definitions (including nested)
        for match in re.finditer(r'message\s+(\w+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', text):
            message_name = match.group(1)
            message_body = match.group(2)
            
            # Count fields
            fields = self._extract_message_fields(message_body)
            
            # Check for nested messages
            nested_messages = re.findall(r'message\s+(\w+)', message_body)
            
            # Check for nested enums
            nested_enums = re.findall(r'enum\s+(\w+)', message_body)
            
            messages.append({
                "name": message_name,
                "field_count": len(fields),
                "nested_message_count": len(nested_messages),
                "nested_enum_count": len(nested_enums),
                "has_repeated_fields": any(f['repeated'] for f in fields),
                "has_optional_fields": any(f['optional'] for f in fields),
                "has_oneof": 'oneof' in message_body
            })
        
        return messages
    
    def _extract_message_fields(self, message_body: str) -> List[Dict[str, Any]]:
        """Extract fields from a message body."""
        fields = []
        
        # Regular fields
        field_pattern = r'(?:(repeated|optional|required)\s+)?(\w+(?:\.\w+)*)\s+(\w+)\s*=\s*(\d+)'
        
        for match in re.finditer(field_pattern, message_body):
            modifier = match.group(1)
            field_type = match.group(2)
            field_name = match.group(3)
            field_number = match.group(4)
            
            fields.append({
                "name": field_name,
                "type": field_type,
                "number": int(field_number),
                "repeated": modifier == "repeated",
                "optional": modifier == "optional",
                "required": modifier == "required"
            })
        
        return fields
    
    def _extract_services(self, text: str) -> List[Dict[str, Any]]:
        """Extract service definitions."""
        services = []
        
        for match in re.finditer(r'service\s+(\w+)\s*{([^}]+)}', text, re.DOTALL):
            service_name = match.group(1)
            service_body = match.group(2)
            
            # Count RPCs
            rpcs = re.findall(r'rpc\s+\w+', service_body)
            
            services.append({
                "name": service_name,
                "rpc_count": len(rpcs)
            })
        
        return services
    
    def _extract_enums(self, text: str) -> List[Dict[str, Any]]:
        """Extract enum definitions."""
        enums = []
        
        for match in re.finditer(r'enum\s+(\w+)\s*{([^}]+)}', text):
            enum_name = match.group(1)
            enum_body = match.group(2)
            
            # Extract enum values
            values = re.findall(r'(\w+)\s*=\s*(\d+)', enum_body)
            
            enums.append({
                "name": enum_name,
                "value_count": len(values),
                "values": [{"name": v[0], "number": int(v[1])} for v in values[:10]]
            })
        
        return enums
    
    def _analyze_fields(self, text: str) -> Dict[str, Any]:
        """Analyze field usage across all messages."""
        all_fields = []
        
        # Extract all field definitions
        field_pattern = r'(?:(repeated|optional|required)\s+)?(\w+(?:\.\w+)*)\s+(\w+)\s*=\s*(\d+)'
        
        for match in re.finditer(field_pattern, text):
            modifier = match.group(1)
            field_type = match.group(2)
            
            all_fields.append({
                "type": field_type,
                "modifier": modifier
            })
        
        # Analyze field types
        type_counts = {}
        for field in all_fields:
            field_type = field['type']
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        # Common types
        common_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_count": len(all_fields),
            "repeated_count": sum(1 for f in all_fields if f['modifier'] == 'repeated'),
            "optional_count": sum(1 for f in all_fields if f['modifier'] == 'optional'),
            "required_count": sum(1 for f in all_fields if f['modifier'] == 'required'),
            "common_types": common_types
        }
    
    def _extract_rpcs(self, text: str) -> List[Dict[str, Any]]:
        """Extract RPC definitions."""
        rpcs = []
        
        for match in re.finditer(
            r'rpc\s+(\w+)\s*\((?:(stream)\s+)?(\w+)\)\s*returns\s*\((?:(stream)\s+)?(\w+)\)',
            text
        ):
            rpc_name = match.group(1)
            client_streaming = bool(match.group(2))
            request_type = match.group(3)
            server_streaming = bool(match.group(4))
            response_type = match.group(5)
            
            rpcs.append({
                "name": rpc_name,
                "request_type": request_type,
                "response_type": response_type,
                "client_streaming": client_streaming,
                "server_streaming": server_streaming,
                "pattern": self._determine_rpc_pattern(client_streaming, server_streaming)
            })
        
        return rpcs
    
    def _determine_rpc_pattern(self, client_streaming: bool, server_streaming: bool) -> str:
        """Determine RPC communication pattern."""
        if not client_streaming and not server_streaming:
            return "unary"
        elif client_streaming and not server_streaming:
            return "client_streaming"
        elif not client_streaming and server_streaming:
            return "server_streaming"
        else:
            return "bidirectional_streaming"
    
    def _extract_extensions(self, text: str) -> Dict[str, Any]:
        """Extract extension definitions and usage."""
        extensions = {
            "definitions": [],
            "usage_count": 0
        }
        
        # Extension definitions
        for match in re.finditer(r'extend\s+(\w+)\s*{', text):
            extensions["definitions"].append(match.group(1))
        
        # Extension ranges
        extension_ranges = re.findall(r'extensions\s+\d+\s+to\s+(?:\d+|max)', text)
        extensions["range_count"] = len(extension_ranges)
        
        return extensions
    
    def _assess_schema_design(self, findings: Dict[str, Any]) -> float:
        """Assess Protocol Buffers schema design."""
        score = 0.5
        
        # Has package (namespace)
        if findings.get('package'):
            score += 0.1
        
        # Uses proto3 (more modern)
        if findings.get('syntax') == 'proto3':
            score += 0.1
        
        # Good use of enums
        if findings.get('enums'):
            score += 0.1
        
        # Services defined (for RPC)
        if findings.get('services'):
            score += 0.1
        
        # Not too many messages
        message_count = len(findings.get('messages', []))
        if 5 <= message_count <= 50:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_compatibility(self, findings: Dict[str, Any]) -> float:
        """Assess backward compatibility practices."""
        score = 0.5
        
        # Using proto3 (better compatibility)
        if findings.get('syntax') == 'proto3':
            score += 0.15
        
        # Not using required fields (proto2 anti-pattern)
        fields = findings.get('fields', {})
        if fields.get('required_count', 0) == 0:
            score += 0.15
        
        # Using optional appropriately
        total_fields = fields.get('total_count', 0)
        optional_fields = fields.get('optional_count', 0)
        if total_fields > 0 and optional_fields / total_fields > 0.3:
            score += 0.1
        
        # Has extension points
        if findings.get('extensions', {}).get('range_count', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_documentation(self, findings: Dict[str, Any]) -> float:
        """Assess documentation quality."""
        score = 0.5
        
        # Has comments
        comments = findings.get('comments', {})
        total_comments = comments.get('total', 0)
        
        if total_comments > 10:
            score += 0.2
        elif total_comments > 5:
            score += 0.1
        
        # Good naming (services and messages)
        messages = findings.get('messages', [])
        services = findings.get('services', [])
        
        # Check if names are descriptive (simple heuristic)
        good_names = sum(1 for m in messages if len(m['name']) > 5)
        if messages and good_names / len(messages) > 0.7:
            score += 0.1
        
        # Has options (often used for documentation)
        if findings.get('options'):
            score += 0.1
        
        # Package structure suggests organization
        package = findings.get('package', '')
        if package and '.' in package:  # Nested package
            score += 0.1
        
        return min(score, 1.0) 