"""
Extended configuration handlers for additional config file types
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import configparser
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class INIHandler(DocumentHandler):
    """Handler for INI configuration files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith(('.ini', '.cfg')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # INI file patterns
            if re.search(r'^\[.+\]', text, re.MULTILINE) and '=' in text:
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        text = content.decode('utf-8', errors='ignore')
        
        # Try to identify specific INI file types
        if 'php.ini' in file_path or 'extension=' in text:
            type_name = "PHP Configuration"
        elif 'my.cnf' in file_path or '[mysqld]' in text:
            type_name = "MySQL Configuration"
        elif '.gitconfig' in file_path or '[user]' in text and '[core]' in text:
            type_name = "Git Configuration"
        else:
            type_name = "INI Configuration"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="configuration",
            format="ini"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="INI Configuration",
            category="configuration",
            key_findings=findings,
            ai_use_cases=[
                "Configuration validation",
                "Settings optimization",
                "Security hardening",
                "Migration assistance",
                "Documentation generation"
            ],
            quality_metrics={
                "completeness": self._assess_completeness(findings),
                "security": self._assess_security(content),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        # Parse INI file
        config = configparser.ConfigParser()
        try:
            config.read_string(text)
            sections = dict(config)
            # Remove DEFAULT section if empty
            if 'DEFAULT' in sections and not sections['DEFAULT']:
                sections.pop('DEFAULT')
        except:
            # Fallback to regex parsing
            sections = self._parse_ini_manually(text)
        
        return {
            "sections": list(sections.keys()),
            "total_settings": sum(len(section) for section in sections.values()),
            "configuration": sections,
            "comments": len(re.findall(r'^\s*[;#]', text, re.MULTILINE)),
            "empty_values": self._count_empty_values(sections)
        }
    
    def _parse_ini_manually(self, text: str) -> Dict[str, Dict[str, str]]:
        """Fallback manual INI parsing"""
        sections = {}
        current_section = 'DEFAULT'
        
        for line in text.split('\n'):
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue
            
            # Section header
            section_match = re.match(r'^\[(.+)\]$', line)
            if section_match:
                current_section = section_match.group(1)
                sections[current_section] = {}
                continue
            
            # Key-value pair
            kv_match = re.match(r'^([^=]+)=(.*)$', line)
            if kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()
                if current_section not in sections:
                    sections[current_section] = {}
                sections[current_section][key] = value
        
        return sections
    
    def _count_empty_values(self, sections: Dict[str, Dict[str, str]]) -> int:
        count = 0
        for section in sections.values():
            for value in section.values():
                if not value or value.isspace():
                    count += 1
        return count
    
    def _assess_completeness(self, findings: Dict[str, Any]) -> float:
        total = findings.get('total_settings', 0)
        empty = findings.get('empty_values', 0)
        if total == 0:
            return 0.0
        return (total - empty) / total
    
    def _assess_security(self, content: bytes) -> float:
        text = content.decode('utf-8', errors='ignore')
        
        # Check for potential security issues
        security_issues = [
            len(re.findall(r'password\s*=\s*\S+', text, re.IGNORECASE)),
            len(re.findall(r'secret\s*=\s*\S+', text, re.IGNORECASE)),
            len(re.findall(r'api_key\s*=\s*\S+', text, re.IGNORECASE))
        ]
        
        # Check for good practices
        good_practices = [
            len(re.findall(r'password\s*=\s*\${', text, re.IGNORECASE)),  # Environment variables
            len(re.findall(r'secret\s*=\s*\${', text, re.IGNORECASE))
        ]
        
        if sum(security_issues) == 0:
            return 1.0
        
        return min(sum(good_practices) / sum(security_issues), 1.0)


class EnvFileHandler(DocumentHandler):
    """Handler for .env environment files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if '.env' in file_path:
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Environment variable patterns
            if re.search(r'^[A-Z_]+=[^\n]*$', text, re.MULTILINE):
                return True, 0.7
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        return DocumentTypeInfo(
            type_name="Environment Variables File",
            confidence=0.95,
            category="configuration",
            format="env"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Environment File",
            category="configuration",
            key_findings=findings,
            ai_use_cases=[
                "Secret management",
                "Environment configuration",
                "Docker/Kubernetes setup",
                "Security audit",
                "Configuration templating"
            ],
            quality_metrics={
                "security_score": self._assess_security(findings),
                "completeness": self._assess_completeness(findings),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        variables = {}
        sensitive_vars = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', line)
            if match:
                key = match.group(1)
                value = match.group(2)
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                variables[key] = value
                
                # Check for sensitive variables
                if any(term in key.lower() for term in ['password', 'secret', 'key', 'token', 'api']):
                    sensitive_vars.append(key)
        
        return {
            "variables": variables,
            "total_vars": len(variables),
            "sensitive_vars": sensitive_vars,
            "comments": len(re.findall(r'^\s*#', text, re.MULTILINE)),
            "empty_values": sum(1 for v in variables.values() if not v),
            "uses_quotes": self._check_quote_usage(text)
        }
    
    def _check_quote_usage(self, text: str) -> Dict[str, int]:
        return {
            "double_quotes": len(re.findall(r'="[^"]*"', text)),
            "single_quotes": len(re.findall(r"='[^']*'", text)),
            "no_quotes": len(re.findall(r'=[^"\'\s]+(?:\s|$)', text))
        }
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        sensitive_count = len(findings.get('sensitive_vars', []))
        total_vars = findings.get('total_vars', 0)
        
        if sensitive_count == 0:
            return 1.0
        
        # Check if sensitive vars have values (bad) or are empty/placeholder (good)
        variables = findings.get('variables', {})
        exposed_secrets = 0
        
        for var in findings.get('sensitive_vars', []):
            value = variables.get(var, '')
            if value and not value.startswith('${') and value != 'changeme':
                exposed_secrets += 1
        
        if exposed_secrets == 0:
            return 0.9
        
        return max(0.3, 1.0 - (exposed_secrets / sensitive_count))
    
    def _assess_completeness(self, findings: Dict[str, Any]) -> float:
        total = findings.get('total_vars', 0)
        empty = findings.get('empty_values', 0)
        
        if total == 0:
            return 0.0
        
        return (total - empty) / total


class ApacheConfigHandler(DocumentHandler):
    """Handler for Apache configuration files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith(('.conf', '.htaccess')) or 'httpd.conf' in file_path or 'apache2.conf' in file_path:
            return True, 0.9
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Apache config patterns
            if any(pattern in text for pattern in [
                '<VirtualHost', '<Directory', 'ServerName', 'DocumentRoot',
                'RewriteEngine', 'LoadModule', '<Location'
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        if '.htaccess' in file_path:
            type_name = "Apache .htaccess"
        elif 'httpd.conf' in file_path:
            type_name = "Apache Main Configuration"
        elif 'sites-' in file_path:
            type_name = "Apache Site Configuration"
        else:
            type_name = "Apache Configuration"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="configuration",
            format="apache"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Apache Configuration",
            category="configuration",
            key_findings=findings,
            ai_use_cases=[
                "Security hardening",
                "Performance optimization",
                "Virtual host configuration",
                "SSL/TLS setup",
                "Rewrite rules optimization"
            ],
            quality_metrics={
                "security": self._assess_security(findings),
                "performance": self._assess_performance(findings),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "directives": self._extract_directives(text),
            "virtual_hosts": self._extract_virtual_hosts(text),
            "modules": self._extract_modules(text),
            "directories": self._extract_directories(text),
            "rewrite_rules": self._extract_rewrite_rules(text),
            "security_headers": self._extract_security_headers(text),
            "ssl_config": self._check_ssl_config(text)
        }
    
    def _extract_directives(self, text: str) -> List[str]:
        # Common Apache directives
        directives = []
        directive_patterns = [
            r'^\s*(ServerName|ServerAlias|DocumentRoot|ErrorLog|CustomLog)\s+',
            r'^\s*(Options|AllowOverride|Require|Order|Allow|Deny)\s+',
            r'^\s*(RewriteEngine|RewriteCond|RewriteRule)\s+'
        ]
        
        for pattern in directive_patterns:
            directives.extend(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE))
        
        return list(set(directives))
    
    def _extract_virtual_hosts(self, text: str) -> List[Dict[str, str]]:
        vhosts = []
        vhost_blocks = re.findall(r'<VirtualHost\s+([^>]+)>(.*?)</VirtualHost>', text, re.DOTALL | re.IGNORECASE)
        
        for addr, content in vhost_blocks:
            server_name = re.search(r'ServerName\s+(\S+)', content)
            vhosts.append({
                'address': addr,
                'server_name': server_name.group(1) if server_name else 'unknown'
            })
        
        return vhosts
    
    def _extract_modules(self, text: str) -> List[str]:
        return re.findall(r'LoadModule\s+(\w+)', text)
    
    def _extract_directories(self, text: str) -> List[str]:
        return re.findall(r'<Directory\s+"?([^">]+)"?>', text, re.IGNORECASE)
    
    def _extract_rewrite_rules(self, text: str) -> int:
        return len(re.findall(r'RewriteRule\s+', text, re.IGNORECASE))
    
    def _extract_security_headers(self, text: str) -> List[str]:
        security_headers = []
        header_patterns = [
            'X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection',
            'Strict-Transport-Security', 'Content-Security-Policy'
        ]
        
        for header in header_patterns:
            if re.search(rf'Header\s+set\s+{header}', text, re.IGNORECASE):
                security_headers.append(header)
        
        return security_headers
    
    def _check_ssl_config(self, text: str) -> Dict[str, Any]:
        return {
            "ssl_enabled": bool(re.search(r'SSLEngine\s+on', text, re.IGNORECASE)),
            "ssl_protocols": re.findall(r'SSLProtocol\s+([^\n]+)', text),
            "ssl_ciphers": bool(re.search(r'SSLCipherSuite\s+', text))
        }
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        score = 0.5  # Base score
        
        # Check for security headers
        security_headers = findings.get('security_headers', [])
        score += len(security_headers) * 0.1
        
        # Check SSL configuration
        ssl_config = findings.get('ssl_config', {})
        if ssl_config.get('ssl_enabled'):
            score += 0.2
        
        # Check for potentially insecure directives
        directives = findings.get('directives', [])
        if 'AllowOverride' in directives:
            score -= 0.1
        
        return min(max(score, 0), 1.0)
    
    def _assess_performance(self, findings: Dict[str, Any]) -> float:
        # Simple performance assessment based on configuration
        modules = findings.get('modules', [])
        rewrite_rules = findings.get('rewrite_rules', 0)
        
        # Many modules can impact performance
        module_score = max(0, 1.0 - (len(modules) / 50))
        
        # Many rewrite rules can impact performance
        rewrite_score = max(0, 1.0 - (rewrite_rules / 100))
        
        return (module_score + rewrite_score) / 2


class NginxConfigHandler(DocumentHandler):
    """Handler for Nginx configuration files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if 'nginx' in file_path.lower() or file_path.endswith('.nginx'):
            return True, 0.9
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Nginx config patterns
            if any(pattern in text for pattern in [
                'server {', 'location ', 'upstream ', 'proxy_pass',
                'server_name ', 'listen ', 'root '
            ]):
                return True, 0.85
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        if 'nginx.conf' in file_path:
            type_name = "Nginx Main Configuration"
        elif 'sites-' in file_path:
            type_name = "Nginx Site Configuration"
        else:
            type_name = "Nginx Configuration"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="configuration",
            format="nginx"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Nginx Configuration",
            category="configuration",
            key_findings=findings,
            ai_use_cases=[
                "Performance tuning",
                "Security hardening",
                "Load balancing setup",
                "SSL/TLS optimization",
                "Reverse proxy configuration"
            ],
            quality_metrics={
                "security": self._assess_security(findings),
                "performance": self._assess_performance(findings),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        return {
            "servers": self._extract_servers(text),
            "upstreams": self._extract_upstreams(text),
            "locations": self._extract_locations(text),
            "directives": self._extract_directives(text),
            "ssl_config": self._check_ssl_config(text),
            "proxy_config": self._check_proxy_config(text),
            "cache_config": self._check_cache_config(text)
        }
    
    def _extract_servers(self, text: str) -> List[Dict[str, Any]]:
        servers = []
        server_blocks = re.findall(r'server\s*{([^}]+)}', text, re.DOTALL)
        
        for block in server_blocks:
            listen = re.search(r'listen\s+([^;]+);', block)
            server_name = re.search(r'server_name\s+([^;]+);', block)
            
            servers.append({
                'listen': listen.group(1).strip() if listen else 'unknown',
                'server_name': server_name.group(1).strip() if server_name else 'unknown'
            })
        
        return servers
    
    def _extract_upstreams(self, text: str) -> List[str]:
        return re.findall(r'upstream\s+(\w+)', text)
    
    def _extract_locations(self, text: str) -> List[str]:
        return re.findall(r'location\s+([^\s{]+)', text)
    
    def _extract_directives(self, text: str) -> List[str]:
        common_directives = [
            'worker_processes', 'worker_connections', 'keepalive_timeout',
            'client_max_body_size', 'gzip', 'proxy_pass', 'proxy_set_header'
        ]
        
        found_directives = []
        for directive in common_directives:
            if re.search(rf'{directive}\s+', text):
                found_directives.append(directive)
        
        return found_directives
    
    def _check_ssl_config(self, text: str) -> Dict[str, Any]:
        return {
            "ssl_enabled": bool(re.search(r'listen\s+.*\s+ssl', text)),
            "ssl_protocols": re.findall(r'ssl_protocols\s+([^;]+);', text),
            "ssl_ciphers": bool(re.search(r'ssl_ciphers\s+', text)),
            "ssl_certificate": bool(re.search(r'ssl_certificate\s+', text))
        }
    
    def _check_proxy_config(self, text: str) -> Dict[str, Any]:
        return {
            "proxy_pass_count": len(re.findall(r'proxy_pass\s+', text)),
            "proxy_headers": len(re.findall(r'proxy_set_header\s+', text)),
            "proxy_cache": bool(re.search(r'proxy_cache\s+', text))
        }
    
    def _check_cache_config(self, text: str) -> Dict[str, Any]:
        return {
            "cache_enabled": bool(re.search(r'proxy_cache_path\s+', text)),
            "cache_zones": re.findall(r'keys_zone=(\w+):', text)
        }
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        score = 0.5
        
        # SSL configuration
        ssl_config = findings.get('ssl_config', {})
        if ssl_config.get('ssl_enabled'):
            score += 0.2
            if ssl_config.get('ssl_protocols'):
                score += 0.1
        
        # Security headers via proxy
        directives = findings.get('directives', [])
        if 'proxy_set_header' in directives:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_performance(self, findings: Dict[str, Any]) -> float:
        score = 0.5
        
        # Caching configuration
        cache_config = findings.get('cache_config', {})
        if cache_config.get('cache_enabled'):
            score += 0.2
        
        # Gzip compression
        directives = findings.get('directives', [])
        if 'gzip' in directives:
            score += 0.1
        
        # Worker configuration
        if 'worker_processes' in directives:
            score += 0.1
        if 'worker_connections' in directives:
            score += 0.1
        
        return min(score, 1.0)


class PropertiesFileHandler(DocumentHandler):
    """Handler for Java-style properties files"""
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        if file_path.endswith('.properties'):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # Properties file pattern: key=value or key:value
            if re.search(r'^\s*[a-zA-Z][a-zA-Z0-9._-]*\s*[=:]\s*', text, re.MULTILINE):
                lines = text.strip().split('\n')
                prop_lines = sum(1 for line in lines if '=' in line or ':' in line)
                if prop_lines / len(lines) > 0.5:
                    return True, 0.8
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        filename = file_path.lower()
        
        if 'application.properties' in filename:
            type_name = "Spring Boot Properties"
        elif 'log4j.properties' in filename:
            type_name = "Log4j Properties"
        elif 'build.properties' in filename:
            type_name = "Build Properties"
        else:
            type_name = "Java Properties File"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="configuration",
            format="properties"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Properties File",
            category="configuration",
            key_findings=findings,
            ai_use_cases=[
                "Configuration management",
                "Property validation",
                "Environment-specific setup",
                "Spring Boot optimization",
                "Internationalization"
            ],
            quality_metrics={
                "completeness": self._assess_completeness(findings),
                "organization": self._assess_organization(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        text = content.decode('utf-8', errors='ignore')
        
        properties = {}
        categories = {}
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            # Handle line continuations
            while line.endswith('\\') and '\n' in text:
                line = line[:-1] + text.split('\n', 1)[0].strip()
                text = text.split('\n', 1)[1]
            
            # Parse property
            for separator in ['=', ':']:
                if separator in line:
                    key, value = line.split(separator, 1)
                    key = key.strip()
                    value = value.strip()
                    properties[key] = value
                    
                    # Categorize by prefix
                    if '.' in key:
                        category = key.split('.')[0]
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(key)
                    break
        
        return {
            "properties": properties,
            "total_properties": len(properties),
            "categories": categories,
            "comments": len(re.findall(r'^\s*[#!]', text, re.MULTILINE)),
            "empty_values": sum(1 for v in properties.values() if not v),
            "placeholders": self._find_placeholders(properties)
        }
    
    def _find_placeholders(self, properties: Dict[str, str]) -> List[str]:
        placeholders = []
        for key, value in properties.items():
            # Find ${...} style placeholders
            found = re.findall(r'\$\{([^}]+)\}', value)
            placeholders.extend(found)
        return list(set(placeholders))
    
    def _assess_completeness(self, findings: Dict[str, Any]) -> float:
        total = findings.get('total_properties', 0)
        empty = findings.get('empty_values', 0)
        
        if total == 0:
            return 0.0
        
        return (total - empty) / total
    
    def _assess_organization(self, findings: Dict[str, Any]) -> float:
        # Check if properties are well-organized by categories
        categories = findings.get('categories', {})
        total_props = findings.get('total_properties', 0)
        
        if total_props == 0:
            return 0.0
        
        # Properties in categories vs total
        categorized = sum(len(props) for props in categories.values())
        return categorized / total_props 