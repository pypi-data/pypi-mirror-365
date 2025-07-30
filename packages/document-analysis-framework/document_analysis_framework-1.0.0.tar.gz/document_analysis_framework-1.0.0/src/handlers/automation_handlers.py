"""
Automation handlers for Ansible and infrastructure automation files

Handles analysis of Ansible playbooks, roles, and automation configurations
for infrastructure as code and configuration management.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import yaml
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class AnsibleHandler(DocumentHandler):
    """
    Handler for Ansible files (playbooks, roles, inventory, etc.).
    
    Analyzes Ansible automation files including playbooks, roles,
    variables, and inventory configurations.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Ansible file."""
        # Common Ansible file patterns
        ansible_patterns = [
            'playbook.yml', 'playbook.yaml',
            'site.yml', 'site.yaml',
            'main.yml', 'main.yaml',
            'tasks/main.yml', 'handlers/main.yml',
            'vars/main.yml', 'defaults/main.yml',
            'meta/main.yml',
            'requirements.yml', 'requirements.yaml',
            'inventory', 'hosts',
            'ansible.cfg',
            '.ansible-lint'
        ]
        
        file_lower = file_path.lower()
        if any(pattern in file_lower for pattern in ansible_patterns):
            return True, 0.9
        
        # Check for role structure
        if '/tasks/' in file_path or '/handlers/' in file_path or '/vars/' in file_path:
            if file_path.endswith(('.yml', '.yaml')):
                return True, 0.85
        
        try:
            text = content.decode('utf-8', errors='ignore')
            
            # Ansible-specific patterns
            if any(pattern in text for pattern in [
                '- hosts:', '- name:', 'tasks:', 'handlers:',
                'become:', 'become_user:', 'ansible_',
                'register:', 'when:', 'with_items:', 'loop:',
                'notify:', 'tags:', 'vars:', 'roles:',
                'include_tasks:', 'import_playbook:'
            ]):
                # Try to parse as YAML
                try:
                    data = yaml.safe_load(text)
                    # Check for playbook structure
                    if isinstance(data, list) and any('hosts' in item for item in data if isinstance(item, dict)):
                        return True, 0.85
                    # Check for tasks structure
                    if isinstance(data, list) and any('name' in item for item in data if isinstance(item, dict)):
                        return True, 0.8
                except:
                    pass
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect Ansible file type."""
        file_lower = file_path.lower()
        text = content.decode('utf-8', errors='ignore')
        
        # Detect specific Ansible file types
        if 'playbook' in file_lower or 'site.yml' in file_lower:
            type_name = "Ansible Playbook"
        elif '/tasks/' in file_path:
            type_name = "Ansible Tasks"
        elif '/handlers/' in file_path:
            type_name = "Ansible Handlers"
        elif '/vars/' in file_path or '/defaults/' in file_path:
            type_name = "Ansible Variables"
        elif '/meta/' in file_path:
            type_name = "Ansible Role Metadata"
        elif 'requirements' in file_lower:
            type_name = "Ansible Requirements"
        elif 'inventory' in file_lower or 'hosts' in file_lower:
            type_name = "Ansible Inventory"
        elif 'ansible.cfg' in file_lower:
            type_name = "Ansible Configuration"
        else:
            # Try to detect from content
            try:
                data = yaml.safe_load(text)
                if isinstance(data, list) and any('hosts' in item for item in data if isinstance(item, dict)):
                    type_name = "Ansible Playbook"
                else:
                    type_name = "Ansible YAML"
            except:
                type_name = "Ansible File"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="automation",
            format="ansible"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed Ansible file analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Ansible",
            category="automation",
            key_findings=findings,
            ai_use_cases=[
                "Playbook optimization and refactoring",
                "Security hardening recommendations",
                "Role generation and modularization",
                "Idempotency verification",
                "Multi-environment configuration",
                "Error handling improvements"
            ],
            quality_metrics={
                "best_practices": self._assess_best_practices(findings),
                "security": self._assess_security(findings),
                "maintainability": self._assess_maintainability(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract Ansible file data."""
        text = content.decode('utf-8', errors='ignore')
        file_lower = file_path.lower()
        
        # Handle Ansible configuration files
        if 'ansible.cfg' in file_lower:
            return self._analyze_ansible_cfg(text)
        
        # Handle inventory files
        if 'inventory' in file_lower or 'hosts' in file_lower:
            if not text.strip().startswith(('---', '-')):
                return self._analyze_inventory_ini(text)
        
        # Handle YAML files
        try:
            data = yaml.safe_load(text)
            
            # Detect file type and analyze accordingly
            if isinstance(data, list) and any('hosts' in item for item in data if isinstance(item, dict)):
                return self._analyze_playbook(data)
            elif isinstance(data, list) and all('name' in item for item in data if isinstance(item, dict)):
                return self._analyze_tasks(data)
            elif isinstance(data, dict):
                if 'dependencies' in data or 'galaxy_info' in data:
                    return self._analyze_role_meta(data)
                elif any(key in data for key in ['roles', 'collections']):
                    return self._analyze_requirements(data)
                else:
                    return self._analyze_variables(data)
            else:
                return {"file_type": "unknown", "data": data}
                
        except Exception as e:
            return {"error": f"Failed to parse Ansible YAML: {str(e)}"}
    
    def _analyze_playbook(self, plays: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Ansible playbook."""
        analysis = {
            "file_type": "playbook",
            "play_count": len(plays),
            "plays": [],
            "total_tasks": 0,
            "hosts": set(),
            "roles_used": [],
            "variables": {},
            "tags": set(),
            "become_usage": False,
            "handlers": [],
            "includes": [],
            "strategies": set()
        }
        
        for play in plays:
            if not isinstance(play, dict):
                continue
                
            play_info = {
                "name": play.get('name', 'Unnamed play'),
                "hosts": play.get('hosts', 'all'),
                "gather_facts": play.get('gather_facts', True),
                "become": play.get('become', False),
                "become_user": play.get('become_user'),
                "serial": play.get('serial'),
                "strategy": play.get('strategy', 'linear'),
                "task_count": 0
            }
            
            # Collect hosts
            if isinstance(play_info['hosts'], str):
                analysis['hosts'].add(play_info['hosts'])
            elif isinstance(play_info['hosts'], list):
                analysis['hosts'].update(play_info['hosts'])
            
            # Analyze tasks
            tasks = play.get('tasks', [])
            if tasks:
                play_info['task_count'] = len(tasks)
                analysis['total_tasks'] += len(tasks)
                self._analyze_task_list(tasks, analysis)
            
            # Analyze pre_tasks and post_tasks
            for task_type in ['pre_tasks', 'post_tasks']:
                if task_type in play:
                    analysis['total_tasks'] += len(play[task_type])
                    self._analyze_task_list(play[task_type], analysis)
            
            # Roles
            if 'roles' in play:
                roles = play['roles']
                if isinstance(roles, list):
                    for role in roles:
                        if isinstance(role, str):
                            analysis['roles_used'].append(role)
                        elif isinstance(role, dict) and 'role' in role:
                            analysis['roles_used'].append(role['role'])
            
            # Variables
            if 'vars' in play:
                analysis['variables'].update(play['vars'])
            
            # Handlers
            if 'handlers' in play:
                analysis['handlers'].extend(play['handlers'])
            
            # Become usage
            if play.get('become'):
                analysis['become_usage'] = True
            
            # Strategy
            if play.get('strategy'):
                analysis['strategies'].add(play['strategy'])
            
            analysis['plays'].append(play_info)
        
        # Convert sets to lists for JSON serialization
        analysis['hosts'] = list(analysis['hosts'])
        analysis['tags'] = list(analysis['tags'])
        analysis['strategies'] = list(analysis['strategies'])
        
        return analysis
    
    def _analyze_task_list(self, tasks: List[Dict[str, Any]], analysis: Dict[str, Any]) -> None:
        """Analyze a list of tasks and update analysis."""
        for task in tasks:
            if not isinstance(task, dict):
                continue
            
            # Collect tags
            if 'tags' in task:
                tags = task['tags']
                if isinstance(tags, str):
                    analysis['tags'].add(tags)
                elif isinstance(tags, list):
                    analysis['tags'].update(tags)
            
            # Check for includes
            for include_type in ['include_tasks', 'import_tasks', 'include_role', 'import_role']:
                if include_type in task:
                    analysis['includes'].append({
                        "type": include_type,
                        "target": task[include_type]
                    })
            
            # Check for become
            if task.get('become'):
                analysis['become_usage'] = True
    
    def _analyze_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze standalone tasks file."""
        analysis = {
            "file_type": "tasks",
            "task_count": len(tasks),
            "tasks": [],
            "modules_used": {},
            "conditionals": 0,
            "loops": 0,
            "register_vars": [],
            "notify_handlers": [],
            "tags": set()
        }
        
        for task in tasks:
            if not isinstance(task, dict):
                continue
            
            task_info = {
                "name": task.get('name', 'Unnamed task'),
                "module": None,
                "has_when": 'when' in task,
                "has_loop": any(loop in task for loop in ['loop', 'with_items', 'with_dict', 'with_list']),
                "has_register": 'register' in task,
                "has_notify": 'notify' in task
            }
            
            # Find the module (first key that's not a known task keyword)
            task_keywords = {
                'name', 'when', 'register', 'loop', 'with_items', 'with_dict',
                'with_list', 'notify', 'tags', 'become', 'become_user',
                'delegate_to', 'run_once', 'ignore_errors', 'changed_when',
                'failed_when', 'until', 'retries', 'delay', 'vars'
            }
            
            for key in task:
                if key not in task_keywords:
                    task_info['module'] = key
                    analysis['modules_used'][key] = analysis['modules_used'].get(key, 0) + 1
                    break
            
            # Count features
            if task_info['has_when']:
                analysis['conditionals'] += 1
            if task_info['has_loop']:
                analysis['loops'] += 1
            if task_info['has_register']:
                analysis['register_vars'].append(task.get('register'))
            if task_info['has_notify']:
                notify = task.get('notify')
                if isinstance(notify, str):
                    analysis['notify_handlers'].append(notify)
                elif isinstance(notify, list):
                    analysis['notify_handlers'].extend(notify)
            
            # Collect tags
            if 'tags' in task:
                tags = task['tags']
                if isinstance(tags, str):
                    analysis['tags'].add(tags)
                elif isinstance(tags, list):
                    analysis['tags'].update(tags)
            
            analysis['tasks'].append(task_info)
        
        analysis['tags'] = list(analysis['tags'])
        return analysis
    
    def _analyze_variables(self, vars_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze variables file."""
        analysis = {
            "file_type": "variables",
            "variable_count": len(vars_data),
            "variables": {},
            "has_vault": False,
            "complex_vars": 0,
            "list_vars": 0,
            "dict_vars": 0
        }
        
        for key, value in vars_data.items():
            var_info = {
                "type": type(value).__name__,
                "is_complex": isinstance(value, (dict, list))
            }
            
            # Check for vault encrypted values
            if isinstance(value, str) and value.startswith('$ANSIBLE_VAULT'):
                analysis['has_vault'] = True
                var_info['is_vault'] = True
            
            # Count variable types
            if isinstance(value, dict):
                analysis['dict_vars'] += 1
                analysis['complex_vars'] += 1
            elif isinstance(value, list):
                analysis['list_vars'] += 1
                analysis['complex_vars'] += 1
            
            analysis['variables'][key] = var_info
        
        return analysis
    
    def _analyze_role_meta(self, meta_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze role metadata."""
        galaxy_info = meta_data.get('galaxy_info', {})
        
        return {
            "file_type": "role_metadata",
            "role_name": galaxy_info.get('role_name'),
            "author": galaxy_info.get('author'),
            "description": galaxy_info.get('description'),
            "license": galaxy_info.get('license'),
            "min_ansible_version": galaxy_info.get('min_ansible_version'),
            "platforms": galaxy_info.get('platforms', []),
            "galaxy_tags": galaxy_info.get('galaxy_tags', []),
            "dependencies": [
                dep if isinstance(dep, str) else dep.get('role', 'unknown')
                for dep in meta_data.get('dependencies', [])
            ],
            "dependency_count": len(meta_data.get('dependencies', []))
        }
    
    def _analyze_requirements(self, req_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements file."""
        analysis = {
            "file_type": "requirements",
            "roles": [],
            "collections": [],
            "total_dependencies": 0
        }
        
        # Analyze roles
        if 'roles' in req_data:
            for role in req_data['roles']:
                if isinstance(role, dict):
                    analysis['roles'].append({
                        "name": role.get('name') or role.get('role'),
                        "src": role.get('src'),
                        "version": role.get('version'),
                        "scm": role.get('scm')
                    })
                elif isinstance(role, str):
                    analysis['roles'].append({"name": role})
        
        # Analyze collections
        if 'collections' in req_data:
            for collection in req_data['collections']:
                if isinstance(collection, dict):
                    analysis['collections'].append({
                        "name": collection.get('name'),
                        "version": collection.get('version'),
                        "source": collection.get('source')
                    })
                elif isinstance(collection, str):
                    analysis['collections'].append({"name": collection})
        
        analysis['total_dependencies'] = len(analysis['roles']) + len(analysis['collections'])
        
        return analysis
    
    def _analyze_inventory_ini(self, text: str) -> Dict[str, Any]:
        """Analyze INI-style inventory file."""
        analysis = {
            "file_type": "inventory",
            "format": "ini",
            "groups": {},
            "hosts": set(),
            "has_variables": False
        }
        
        current_group = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Group header
            if line.startswith('[') and line.endswith(']'):
                current_group = line[1:-1]
                if ':' not in current_group:  # Skip [group:vars] sections
                    analysis['groups'][current_group] = []
            
            # Host definition
            elif current_group is not None and ':' not in current_group:
                # Extract hostname (before any variables)
                parts = line.split()
                if parts:
                    hostname = parts[0]
                    analysis['hosts'].add(hostname)
                    if current_group in analysis['groups']:
                        analysis['groups'][current_group].append(hostname)
                    
                    # Check for inline variables
                    if len(parts) > 1 or '=' in line:
                        analysis['has_variables'] = True
        
        analysis['hosts'] = list(analysis['hosts'])
        analysis['group_count'] = len(analysis['groups'])
        analysis['host_count'] = len(analysis['hosts'])
        
        return analysis
    
    def _analyze_ansible_cfg(self, text: str) -> Dict[str, Any]:
        """Analyze ansible.cfg configuration file."""
        analysis = {
            "file_type": "configuration",
            "sections": {},
            "has_custom_modules": False,
            "has_vault": False,
            "has_callbacks": False
        }
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                analysis['sections'][current_section] = {}
            
            # Configuration option
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                analysis['sections'][current_section][key] = value
                
                # Check for specific configurations
                if key == 'library' or key == 'module_utils':
                    analysis['has_custom_modules'] = True
                elif key == 'vault_password_file':
                    analysis['has_vault'] = True
                elif key == 'callback_plugins' or key == 'stdout_callback':
                    analysis['has_callbacks'] = True
        
        return analysis
    
    def _assess_best_practices(self, findings: Dict[str, Any]) -> float:
        """Assess Ansible best practices."""
        score = 0.5
        file_type = findings.get('file_type')
        
        if file_type == 'playbook':
            # Named plays
            plays = findings.get('plays', [])
            if plays and all(p.get('name') != 'Unnamed play' for p in plays):
                score += 0.1
            
            # Using roles for modularity
            if findings.get('roles_used'):
                score += 0.15
            
            # Using tags for organization
            if findings.get('tags'):
                score += 0.1
            
            # Using handlers
            if findings.get('handlers'):
                score += 0.1
            
        elif file_type == 'tasks':
            # All tasks are named
            tasks = findings.get('tasks', [])
            if tasks and all(t.get('name') != 'Unnamed task' for t in tasks):
                score += 0.15
            
            # Using conditionals appropriately
            if findings.get('conditionals', 0) > 0:
                score += 0.1
            
            # Using register for task results
            if findings.get('register_vars'):
                score += 0.1
            
            # Using handlers for idempotency
            if findings.get('notify_handlers'):
                score += 0.1
        
        elif file_type == 'variables':
            # Using vault for sensitive data
            if findings.get('has_vault'):
                score += 0.2
            
            # Organized complex variables
            if findings.get('complex_vars', 0) > 0:
                score += 0.1
        
        elif file_type == 'inventory':
            # Using groups
            if findings.get('group_count', 0) > 1:
                score += 0.2
            
            # Has variables
            if findings.get('has_variables'):
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        """Assess security practices."""
        score = 0.5
        file_type = findings.get('file_type')
        
        if file_type == 'playbook':
            # Using become appropriately (not always root)
            if findings.get('become_usage'):
                score += 0.1
                # Check if become_user is specified
                plays = findings.get('plays', [])
                if any(p.get('become_user') for p in plays):
                    score += 0.1
        
        elif file_type == 'variables':
            # Using vault for sensitive data
            if findings.get('has_vault'):
                score += 0.3
        
        elif file_type == 'configuration':
            # Has vault configuration
            if findings.get('has_vault'):
                score += 0.2
        
        # Common security checks
        if file_type in ['playbook', 'tasks']:
            # Not too many tasks running as root
            if not findings.get('become_usage'):
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_maintainability(self, findings: Dict[str, Any]) -> float:
        """Assess maintainability."""
        score = 0.5
        file_type = findings.get('file_type')
        
        if file_type == 'playbook':
            # Reasonable number of plays
            play_count = findings.get('play_count', 0)
            if 1 <= play_count <= 5:
                score += 0.1
            
            # Using includes for modularity
            if findings.get('includes'):
                score += 0.15
            
            # Good task organization
            total_tasks = findings.get('total_tasks', 0)
            if total_tasks > 0 and total_tasks < 50:
                score += 0.1
        
        elif file_type == 'tasks':
            # Reasonable task count
            task_count = findings.get('task_count', 0)
            if 1 <= task_count <= 20:
                score += 0.15
            
            # Good module variety (not doing everything with shell/command)
            modules = findings.get('modules_used', {})
            if len(modules) > 3:
                score += 0.1
            
            # Not overusing shell/command modules
            shell_usage = modules.get('shell', 0) + modules.get('command', 0)
            if task_count > 0 and shell_usage / task_count < 0.3:
                score += 0.1
        
        elif file_type == 'role_metadata':
            # Good metadata
            if findings.get('description'):
                score += 0.1
            if findings.get('platforms'):
                score += 0.1
            if findings.get('min_ansible_version'):
                score += 0.1
        
        elif file_type == 'requirements':
            # Version pinning
            roles = findings.get('roles', [])
            collections = findings.get('collections', [])
            
            versioned_deps = sum(1 for r in roles if r.get('version'))
            versioned_deps += sum(1 for c in collections if c.get('version'))
            total_deps = len(roles) + len(collections)
            
            if total_deps > 0 and versioned_deps / total_deps > 0.7:
                score += 0.2
        
        return min(score, 1.0) 