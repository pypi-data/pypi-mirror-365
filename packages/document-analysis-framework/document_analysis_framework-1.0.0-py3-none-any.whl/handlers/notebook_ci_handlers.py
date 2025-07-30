"""
Notebook and CI/CD handlers for Jupyter notebooks and GitHub Actions

Handles analysis of data science notebooks and continuous integration
workflow files.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import json
import yaml
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class JupyterNotebookHandler(DocumentHandler):
    """
    Handler for Jupyter Notebook files (.ipynb).
    
    Analyzes notebook structure including cells, outputs, metadata,
    and computational patterns.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the Jupyter notebook file."""
        if file_path.endswith('.ipynb'):
            return True, 0.95
        
        try:
            # Try to parse as JSON
            data = json.loads(content.decode('utf-8', errors='ignore'))
            # Check for notebook structure
            if isinstance(data, dict) and 'cells' in data and 'metadata' in data:
                return True, 0.9
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect notebook type and kernel."""
        try:
            data = json.loads(content.decode('utf-8', errors='ignore'))
            
            # Get kernel info
            kernel_info = data.get('metadata', {}).get('kernelspec', {})
            kernel_name = kernel_info.get('display_name', 'Unknown')
            language = kernel_info.get('language', 'unknown')
            
            # Detect notebook type
            if 'google.colab' in str(data.get('metadata', {})):
                notebook_type = "Google Colab Notebook"
            elif 'databricks' in str(data.get('metadata', {})):
                notebook_type = "Databricks Notebook"
            else:
                notebook_type = "Jupyter Notebook"
            
            type_name = f"{notebook_type} ({kernel_name})"
        except:
            type_name = "Jupyter Notebook"
            language = "unknown"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="notebook",
            format="ipynb",
            language=language
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed notebook analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="Jupyter Notebook",
            category="notebook",
            key_findings=findings,
            ai_use_cases=[
                "Code cell optimization",
                "Documentation generation",
                "Notebook to script conversion",
                "Dependency extraction",
                "Output visualization analysis",
                "Computational workflow extraction"
            ],
            quality_metrics={
                "documentation_quality": self._assess_documentation(findings),
                "code_organization": self._assess_organization(findings),
                "reproducibility": self._assess_reproducibility(findings),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract notebook structure and content."""
        try:
            data = json.loads(content.decode('utf-8', errors='ignore'))
        except Exception as e:
            return {"error": f"Failed to parse notebook: {str(e)}"}
        
        return {
            "metadata": self._extract_metadata(data),
            "cells": self._analyze_cells(data.get('cells', [])),
            "imports": self._extract_imports(data.get('cells', [])),
            "functions": self._extract_functions(data.get('cells', [])),
            "variables": self._extract_variables(data.get('cells', [])),
            "outputs": self._analyze_outputs(data.get('cells', [])),
            "execution_order": self._analyze_execution_order(data.get('cells', [])),
            "dependencies": self._extract_dependencies(data.get('cells', [])),
            "magic_commands": self._extract_magic_commands(data.get('cells', [])),
            "file_size_bytes": len(content),
            "notebook_format": data.get('nbformat', 0)
        }
    
    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract notebook metadata."""
        metadata = data.get('metadata', {})
        
        return {
            "kernel": metadata.get('kernelspec', {}).get('display_name', 'Unknown'),
            "language": metadata.get('kernelspec', {}).get('language', 'unknown'),
            "language_info": metadata.get('language_info', {}).get('name', 'unknown'),
            "created_with": self._detect_notebook_creator(metadata),
            "has_toc": 'toc' in metadata,
            "has_variables_inspector": 'varInspector' in metadata,
            "colab_specific": 'colab' in metadata,
            "widgets_used": 'widgets' in str(metadata)
        }
    
    def _detect_notebook_creator(self, metadata: Dict[str, Any]) -> str:
        """Detect which tool created the notebook."""
        if 'colab' in metadata:
            return "Google Colab"
        elif 'databricks' in metadata:
            return "Databricks"
        elif 'vscode' in str(metadata):
            return "VS Code"
        elif 'jupyterlab' in str(metadata):
            return "JupyterLab"
        else:
            return "Jupyter Notebook"
    
    def _analyze_cells(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cell types and content."""
        cell_stats = {
            "total_cells": len(cells),
            "code_cells": 0,
            "markdown_cells": 0,
            "raw_cells": 0,
            "empty_cells": 0,
            "cells_with_output": 0,
            "cells_with_errors": 0,
            "average_lines_per_cell": 0,
            "max_lines_in_cell": 0
        }
        
        total_lines = 0
        max_lines = 0
        
        for cell in cells:
            cell_type = cell.get('cell_type', 'unknown')
            
            if cell_type == 'code':
                cell_stats["code_cells"] += 1
                
                # Check for outputs
                if cell.get('outputs'):
                    cell_stats["cells_with_output"] += 1
                    
                    # Check for errors
                    for output in cell.get('outputs', []):
                        if output.get('output_type') == 'error':
                            cell_stats["cells_with_errors"] += 1
                            break
            
            elif cell_type == 'markdown':
                cell_stats["markdown_cells"] += 1
            elif cell_type == 'raw':
                cell_stats["raw_cells"] += 1
            
            # Count lines
            source = cell.get('source', [])
            if isinstance(source, list):
                lines = len(source)
            else:
                lines = len(source.split('\n'))
            
            if lines == 0:
                cell_stats["empty_cells"] += 1
            
            total_lines += lines
            max_lines = max(max_lines, lines)
        
        if cells:
            cell_stats["average_lines_per_cell"] = round(total_lines / len(cells), 2)
        cell_stats["max_lines_in_cell"] = max_lines
        
        return cell_stats
    
    def _extract_imports(self, cells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract import statements from code cells."""
        imports = []
        seen_imports = set()
        
        for cell in cells:
            if cell.get('cell_type') != 'code':
                continue
            
            source = self._get_cell_source(cell)
            
            # Python imports
            for match in re.finditer(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', source, re.MULTILINE):
                from_module = match.group(1)
                import_items = match.group(2)
                
                import_str = f"from {from_module} import {import_items}" if from_module else f"import {import_items}"
                
                if import_str not in seen_imports:
                    seen_imports.add(import_str)
                    
                    # Determine import type
                    if from_module:
                        module = from_module.split('.')[0]
                    else:
                        module = import_items.split()[0].split('.')[0]
                    
                    imports.append({
                        "statement": import_str,
                        "module": module,
                        "is_standard": self._is_standard_library(module),
                        "is_data_science": self._is_data_science_library(module)
                    })
        
        return imports
    
    def _get_cell_source(self, cell: Dict[str, Any]) -> str:
        """Get source code from a cell."""
        source = cell.get('source', [])
        if isinstance(source, list):
            return ''.join(source)
        return source
    
    def _is_standard_library(self, module: str) -> bool:
        """Check if module is from Python standard library."""
        standard_libs = {
            'os', 'sys', 'json', 'csv', 'math', 'random', 'datetime',
            'collections', 'itertools', 're', 'urllib', 'pathlib',
            'typing', 'functools', 'operator', 'time', 'io'
        }
        return module in standard_libs
    
    def _is_data_science_library(self, module: str) -> bool:
        """Check if module is a common data science library."""
        ds_libs = {
            'numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy',
            'sklearn', 'tensorflow', 'torch', 'keras', 'plotly',
            'statsmodels', 'xgboost', 'lightgbm', 'cv2', 'PIL'
        }
        return module in ds_libs
    
    def _extract_functions(self, cells: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract function definitions."""
        functions = []
        
        for cell in cells:
            if cell.get('cell_type') != 'code':
                continue
            
            source = self._get_cell_source(cell)
            
            # Extract function definitions
            for match in re.finditer(r'^def\s+(\w+)\s*\(([^)]*)\):', source, re.MULTILINE):
                func_name = match.group(1)
                params = match.group(2)
                
                functions.append({
                    "name": func_name,
                    "params": params,
                    "has_params": bool(params.strip())
                })
        
        return functions
    
    def _extract_variables(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract variable assignments and data loading."""
        variables = {
            "dataframes": [],
            "models": [],
            "file_reads": [],
            "api_calls": [],
            "constants": []
        }
        
        for cell in cells:
            if cell.get('cell_type') != 'code':
                continue
            
            source = self._get_cell_source(cell)
            
            # DataFrames
            df_patterns = [
                r'(\w+)\s*=\s*pd\.DataFrame',
                r'(\w+)\s*=\s*pd\.read_',
                r'(\w+)\s*=\s*df\.'
            ]
            for pattern in df_patterns:
                for match in re.finditer(pattern, source):
                    var_name = match.group(1)
                    if var_name not in variables["dataframes"]:
                        variables["dataframes"].append(var_name)
            
            # Models
            model_patterns = [
                r'(\w+)\s*=\s*\w+Classifier\(',
                r'(\w+)\s*=\s*\w+Regressor\(',
                r'(\w+)\s*=\s*Sequential\(',
                r'(\w+)\s*=\s*Model\('
            ]
            for pattern in model_patterns:
                for match in re.finditer(pattern, source):
                    var_name = match.group(1)
                    if var_name not in variables["models"]:
                        variables["models"].append(var_name)
            
            # File reads
            if re.search(r'open\(|\.read\(|\.load\(', source):
                variables["file_reads"].append(True)
            
            # API calls
            if re.search(r'requests\.|urllib\.|http\.|api\.|\.get\(|\.post\(', source):
                variables["api_calls"].append(True)
            
            # Constants (UPPER_CASE variables)
            for match in re.finditer(r'^([A-Z_]+)\s*=', source, re.MULTILINE):
                const_name = match.group(1)
                if const_name not in variables["constants"]:
                    variables["constants"].append(const_name)
        
        return {
            "dataframe_count": len(variables["dataframes"]),
            "model_count": len(variables["models"]),
            "has_file_io": len(variables["file_reads"]) > 0,
            "has_api_calls": len(variables["api_calls"]) > 0,
            "constant_count": len(variables["constants"]),
            "dataframe_names": variables["dataframes"][:10],  # First 10
            "model_names": variables["models"][:10]
        }
    
    def _analyze_outputs(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cell outputs."""
        output_stats = {
            "total_outputs": 0,
            "text_outputs": 0,
            "display_data": 0,
            "execute_results": 0,
            "errors": 0,
            "warnings": 0,
            "plots": 0,
            "tables": 0,
            "images": 0
        }
        
        for cell in cells:
            if cell.get('cell_type') != 'code':
                continue
            
            for output in cell.get('outputs', []):
                output_stats["total_outputs"] += 1
                
                output_type = output.get('output_type', '')
                
                if output_type == 'stream':
                    output_stats["text_outputs"] += 1
                    
                    # Check for warnings
                    text = output.get('text', '')
                    if isinstance(text, list):
                        text = ''.join(text)
                    if 'warning' in text.lower() or 'warn' in text.lower():
                        output_stats["warnings"] += 1
                
                elif output_type == 'display_data':
                    output_stats["display_data"] += 1
                    
                    # Check for plots/images
                    data = output.get('data', {})
                    if 'image/png' in data or 'image/jpeg' in data:
                        output_stats["images"] += 1
                    if 'text/html' in data and '<table' in str(data.get('text/html', '')):
                        output_stats["tables"] += 1
                    if 'application/vnd.plotly' in data or 'matplotlib' in str(data):
                        output_stats["plots"] += 1
                
                elif output_type == 'execute_result':
                    output_stats["execute_results"] += 1
                
                elif output_type == 'error':
                    output_stats["errors"] += 1
        
        return output_stats
    
    def _analyze_execution_order(self, cells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cell execution order."""
        execution_counts = []
        
        for cell in cells:
            if cell.get('cell_type') == 'code':
                exec_count = cell.get('execution_count')
                if exec_count is not None:
                    execution_counts.append(exec_count)
        
        if not execution_counts:
            return {
                "has_been_executed": False,
                "execution_sequential": True,
                "max_execution": 0,
                "execution_gaps": 0
            }
        
        # Check if execution is sequential
        sorted_counts = sorted(execution_counts)
        is_sequential = sorted_counts == list(range(sorted_counts[0], sorted_counts[-1] + 1))
        
        # Check for gaps
        gaps = 0
        for i in range(1, len(sorted_counts)):
            if sorted_counts[i] - sorted_counts[i-1] > 1:
                gaps += 1
        
        return {
            "has_been_executed": True,
            "execution_sequential": is_sequential,
            "max_execution": max(execution_counts),
            "execution_gaps": gaps,
            "executed_cells": len(execution_counts)
        }
    
    def _extract_dependencies(self, cells: List[Dict[str, Any]]) -> List[str]:
        """Extract package dependencies."""
        dependencies = set()
        
        for cell in cells:
            if cell.get('cell_type') != 'code':
                continue
            
            source = self._get_cell_source(cell)
            
            # pip install commands
            for match in re.finditer(r'!pip\s+install\s+([^\s]+)', source):
                pkg = match.group(1).strip()
                dependencies.add(pkg)
            
            # conda install commands
            for match in re.finditer(r'!conda\s+install\s+(?:-c\s+\w+\s+)?([^\s]+)', source):
                pkg = match.group(1).strip()
                dependencies.add(pkg)
        
        return list(dependencies)
    
    def _extract_magic_commands(self, cells: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract IPython magic commands."""
        magic_commands = {}
        
        for cell in cells:
            if cell.get('cell_type') != 'code':
                continue
            
            source = self._get_cell_source(cell)
            
            # Line magics
            for match in re.finditer(r'^%(\w+)', source, re.MULTILINE):
                magic = match.group(1)
                magic_commands[magic] = magic_commands.get(magic, 0) + 1
            
            # Cell magics
            for match in re.finditer(r'^%%(\w+)', source, re.MULTILINE):
                magic = match.group(1)
                magic_commands[f"%%{magic}"] = magic_commands.get(f"%%{magic}", 0) + 1
        
        return magic_commands
    
    def _assess_documentation(self, findings: Dict[str, Any]) -> float:
        """Assess notebook documentation quality."""
        score = 0.5
        
        cells = findings.get('cells', {})
        
        # Has markdown cells
        markdown_cells = cells.get('markdown_cells', 0)
        total_cells = cells.get('total_cells', 1)
        
        if total_cells > 0:
            markdown_ratio = markdown_cells / total_cells
            if markdown_ratio > 0.2:
                score += 0.2
            elif markdown_ratio > 0.1:
                score += 0.1
        
        # Has function definitions (structured code)
        if findings.get('functions'):
            score += 0.1
        
        # Good balance of code and markdown
        code_cells = cells.get('code_cells', 0)
        if markdown_cells > 0 and code_cells > 0:
            balance = min(markdown_cells, code_cells) / max(markdown_cells, code_cells)
            if balance > 0.3:
                score += 0.1
        
        # Not too many empty cells
        empty_cells = cells.get('empty_cells', 0)
        if total_cells > 0 and empty_cells / total_cells < 0.1:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_organization(self, findings: Dict[str, Any]) -> float:
        """Assess code organization."""
        score = 0.5
        
        # Imports at the beginning
        imports = findings.get('imports', [])
        if imports:
            score += 0.1
        
        # Uses functions
        if findings.get('functions'):
            score += 0.15
        
        # Sequential execution
        execution = findings.get('execution_order', {})
        if execution.get('execution_sequential'):
            score += 0.1
        
        # Reasonable cell sizes
        cells = findings.get('cells', {})
        avg_lines = cells.get('average_lines_per_cell', 0)
        if 5 <= avg_lines <= 30:
            score += 0.1
        
        # No errors in outputs
        outputs = findings.get('outputs', {})
        if outputs.get('errors', 0) == 0:
            score += 0.05
        
        return min(score, 1.0)
    
    def _assess_reproducibility(self, findings: Dict[str, Any]) -> float:
        """Assess notebook reproducibility."""
        score = 0.5
        
        # Has dependency information
        if findings.get('dependencies'):
            score += 0.15
        
        # Uses constants
        variables = findings.get('variables', {})
        if variables.get('constant_count', 0) > 0:
            score += 0.1
        
        # Sequential execution
        execution = findings.get('execution_order', {})
        if execution.get('execution_sequential'):
            score += 0.15
        
        # No execution gaps
        if execution.get('execution_gaps', 0) == 0:
            score += 0.1
        
        # Imports standard libraries
        imports = findings.get('imports', [])
        if any(imp.get('is_standard') for imp in imports):
            score += 0.05
        
        return min(score, 1.0)


class GitHubActionsHandler(DocumentHandler):
    """
    Handler for GitHub Actions workflow files.
    
    Analyzes workflow definitions including jobs, steps, triggers,
    and CI/CD patterns.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the GitHub Actions file."""
        # Check file path
        if '.github/workflows' in file_path and file_path.endswith(('.yml', '.yaml')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # GitHub Actions patterns
            if any(pattern in text for pattern in [
                'on:', 'jobs:', 'runs-on:', 'steps:',
                'uses:', 'with:', 'env:', 'workflow_dispatch:'
            ]):
                # Try to parse as YAML
                try:
                    data = yaml.safe_load(text)
                    if isinstance(data, dict) and ('on' in data or 'jobs' in data):
                        return True, 0.85
                except:
                    pass
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect workflow type."""
        text = content.decode('utf-8', errors='ignore')
        
        # Detect workflow purpose
        workflow_type = "GitHub Actions Workflow"
        
        if 'deploy' in text.lower():
            workflow_type = "GitHub Actions Deployment Workflow"
        elif 'test' in text.lower() or 'ci' in text.lower():
            workflow_type = "GitHub Actions CI Workflow"
        elif 'release' in text.lower():
            workflow_type = "GitHub Actions Release Workflow"
        elif 'security' in text.lower() or 'scan' in text.lower():
            workflow_type = "GitHub Actions Security Workflow"
        
        return DocumentTypeInfo(
            type_name=workflow_type,
            confidence=0.95,
            category="ci",
            format="github-actions"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed GitHub Actions analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="GitHub Actions",
            category="ci",
            key_findings=findings,
            ai_use_cases=[
                "Workflow optimization",
                "Security hardening",
                "Matrix build generation",
                "Dependency caching strategies",
                "Parallel job optimization",
                "Secret management improvements"
            ],
            quality_metrics={
                "workflow_efficiency": self._assess_efficiency(findings),
                "security_practices": self._assess_security(findings),
                "maintainability": self._assess_maintainability(findings),
                "ai_readiness": 0.9
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract GitHub Actions workflow data."""
        text = content.decode('utf-8', errors='ignore')
        
        try:
            data = yaml.safe_load(text)
            if not isinstance(data, dict):
                return {"error": "Invalid YAML structure"}
        except Exception as e:
            return {"error": f"YAML parsing error: {str(e)}"}
        
        return {
            "name": data.get('name', 'Unnamed Workflow'),
            "triggers": self._extract_triggers(data.get('on', {})),
            "jobs": self._analyze_jobs(data.get('jobs', {})),
            "env": self._extract_environment(data),
            "permissions": data.get('permissions', {}),
            "concurrency": data.get('concurrency', {}),
            "defaults": data.get('defaults', {}),
            "secrets": self._extract_secrets(data),
            "actions_used": self._extract_actions(data),
            "artifacts": self._analyze_artifacts(data),
            "caching": self._analyze_caching(data),
            "matrix_builds": self._analyze_matrix_builds(data),
            "conditionals": self._analyze_conditionals(data)
        }
    
    def _extract_triggers(self, triggers: Any) -> Dict[str, Any]:
        """Extract workflow triggers."""
        if isinstance(triggers, str):
            # Simple trigger
            return {
                "types": [triggers],
                "is_manual": triggers == 'workflow_dispatch',
                "is_scheduled": triggers == 'schedule',
                "branches": [],
                "paths": []
            }
        
        if isinstance(triggers, list):
            # List of triggers
            return {
                "types": triggers,
                "is_manual": 'workflow_dispatch' in triggers,
                "is_scheduled": 'schedule' in triggers,
                "branches": [],
                "paths": []
            }
        
        if isinstance(triggers, dict):
            # Complex triggers
            trigger_info = {
                "types": list(triggers.keys()),
                "is_manual": 'workflow_dispatch' in triggers,
                "is_scheduled": 'schedule' in triggers,
                "branches": [],
                "paths": []
            }
            
            # Extract push/pull_request details
            for event in ['push', 'pull_request', 'pull_request_target']:
                if event in triggers and isinstance(triggers[event], dict):
                    event_config = triggers[event]
                    if 'branches' in event_config:
                        trigger_info["branches"].extend(event_config['branches'])
                    if 'paths' in event_config:
                        trigger_info["paths"].extend(event_config['paths'])
            
            # Schedule details
            if 'schedule' in triggers:
                schedule = triggers['schedule']
                if isinstance(schedule, list) and schedule:
                    trigger_info["cron_expressions"] = [
                        s.get('cron', '') for s in schedule if isinstance(s, dict)
                    ]
            
            return trigger_info
        
        return {"types": [], "is_manual": False, "is_scheduled": False}
    
    def _analyze_jobs(self, jobs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow jobs."""
        job_list = []
        total_steps = 0
        
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            
            steps = job_config.get('steps', [])
            
            job_info = {
                "name": job_name,
                "runs_on": job_config.get('runs-on', 'unknown'),
                "needs": job_config.get('needs', []),
                "if": job_config.get('if'),
                "strategy": bool(job_config.get('strategy')),
                "matrix": bool(job_config.get('strategy', {}).get('matrix')),
                "container": bool(job_config.get('container')),
                "services": bool(job_config.get('services')),
                "step_count": len(steps),
                "timeout_minutes": job_config.get('timeout-minutes'),
                "continue_on_error": job_config.get('continue-on-error', False)
            }
            
            job_list.append(job_info)
            total_steps += len(steps)
        
        # Analyze job dependencies
        dependency_graph = {}
        for job in job_list:
            needs = job['needs']
            if isinstance(needs, str):
                needs = [needs]
            elif not isinstance(needs, list):
                needs = []
            dependency_graph[job['name']] = needs
        
        return {
            "count": len(jobs),
            "jobs": job_list,
            "total_steps": total_steps,
            "dependency_graph": dependency_graph,
            "has_parallel_jobs": len(jobs) > 1 and any(not job['needs'] for job in job_list),
            "max_dependency_depth": self._calculate_dependency_depth(dependency_graph)
        }
    
    def _calculate_dependency_depth(self, graph: Dict[str, List[str]]) -> int:
        """Calculate maximum dependency depth in job graph."""
        def get_depth(job: str, visited: set) -> int:
            if job in visited:
                return 0
            visited.add(job)
            
            deps = graph.get(job, [])
            if not deps:
                return 0
            
            max_dep_depth = 0
            for dep in deps:
                max_dep_depth = max(max_dep_depth, get_depth(dep, visited))
            
            return max_dep_depth + 1
        
        max_depth = 0
        for job in graph:
            max_depth = max(max_depth, get_depth(job, set()))
        
        return max_depth
    
    def _extract_environment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract environment variables."""
        env_vars = {
            "workflow_level": {},
            "job_level": {},
            "step_level": 0
        }
        
        # Workflow level
        if 'env' in data:
            env_vars["workflow_level"] = data['env']
        
        # Job and step level
        for job_name, job_config in data.get('jobs', {}).items():
            if isinstance(job_config, dict):
                if 'env' in job_config:
                    env_vars["job_level"][job_name] = job_config['env']
                
                # Count steps with env
                for step in job_config.get('steps', []):
                    if isinstance(step, dict) and 'env' in step:
                        env_vars["step_level"] += 1
        
        return env_vars
    
    def _extract_secrets(self, data: Dict[str, Any]) -> List[str]:
        """Extract secret references."""
        secrets = set()
        
        # Search entire workflow for secret references
        def find_secrets(obj):
            if isinstance(obj, str):
                # Look for ${{ secrets.* }} pattern
                for match in re.finditer(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', obj):
                    secrets.add(match.group(1))
            elif isinstance(obj, dict):
                for value in obj.values():
                    find_secrets(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_secrets(item)
        
        find_secrets(data)
        
        return list(secrets)
    
    def _extract_actions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract GitHub Actions used."""
        actions = []
        seen_actions = set()
        
        for job_config in data.get('jobs', {}).values():
            if not isinstance(job_config, dict):
                continue
            
            for step in job_config.get('steps', []):
                if isinstance(step, dict) and 'uses' in step:
                    action = step['uses']
                    
                    if action not in seen_actions:
                        seen_actions.add(action)
                        
                        # Parse action reference
                        action_info = {
                            "full_name": action,
                            "is_docker": action.startswith('docker://'),
                            "is_local": action.startswith('./'),
                            "is_github": not action.startswith(('docker://', './')),
                            "has_version": '@' in action
                        }
                        
                        if action_info["is_github"] and '@' in action:
                            parts = action.split('@')
                            action_info["name"] = parts[0]
                            action_info["version"] = parts[1]
                        
                        actions.append(action_info)
        
        return actions
    
    def _analyze_artifacts(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Analyze artifact usage."""
        artifact_stats = {
            "upload_count": 0,
            "download_count": 0
        }
        
        for job_config in data.get('jobs', {}).values():
            if not isinstance(job_config, dict):
                continue
            
            for step in job_config.get('steps', []):
                if isinstance(step, dict) and 'uses' in step:
                    action = step['uses']
                    if 'actions/upload-artifact' in action:
                        artifact_stats["upload_count"] += 1
                    elif 'actions/download-artifact' in action:
                        artifact_stats["download_count"] += 1
        
        return artifact_stats
    
    def _analyze_caching(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze caching strategies."""
        cache_info = {
            "uses_cache": False,
            "cache_actions": 0,
            "setup_actions_with_cache": []
        }
        
        for job_config in data.get('jobs', {}).values():
            if not isinstance(job_config, dict):
                continue
            
            for step in job_config.get('steps', []):
                if isinstance(step, dict) and 'uses' in step:
                    action = step['uses']
                    
                    # Direct cache action
                    if 'actions/cache' in action:
                        cache_info["uses_cache"] = True
                        cache_info["cache_actions"] += 1
                    
                    # Setup actions with built-in caching
                    setup_actions = [
                        'actions/setup-node',
                        'actions/setup-python',
                        'actions/setup-java',
                        'actions/setup-go',
                        'actions/setup-dotnet'
                    ]
                    
                    for setup_action in setup_actions:
                        if setup_action in action:
                            with_config = step.get('with', {})
                            if isinstance(with_config, dict) and 'cache' in with_config:
                                cache_info["uses_cache"] = True
                                cache_info["setup_actions_with_cache"].append(setup_action)
        
        return cache_info
    
    def _analyze_matrix_builds(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze matrix build configurations."""
        matrix_info = {
            "uses_matrix": False,
            "matrix_jobs": [],
            "total_matrix_combinations": 0
        }
        
        for job_name, job_config in data.get('jobs', {}).items():
            if isinstance(job_config, dict) and 'strategy' in job_config:
                strategy = job_config['strategy']
                if isinstance(strategy, dict) and 'matrix' in strategy:
                    matrix_info["uses_matrix"] = True
                    
                    matrix = strategy['matrix']
                    if isinstance(matrix, dict):
                        # Calculate combinations
                        combinations = 1
                        dimensions = []
                        
                        for key, values in matrix.items():
                            if key not in ['include', 'exclude'] and isinstance(values, list):
                                combinations *= len(values)
                                dimensions.append({
                                    "dimension": key,
                                    "values": len(values)
                                })
                        
                        matrix_info["matrix_jobs"].append({
                            "job": job_name,
                            "dimensions": dimensions,
                            "combinations": combinations,
                            "has_include": 'include' in matrix,
                            "has_exclude": 'exclude' in matrix
                        })
                        
                        matrix_info["total_matrix_combinations"] += combinations
        
        return matrix_info
    
    def _analyze_conditionals(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Analyze conditional execution."""
        conditional_stats = {
            "jobs_with_conditions": 0,
            "steps_with_conditions": 0,
            "always_conditions": 0,
            "failure_conditions": 0,
            "success_conditions": 0
        }
        
        # Analyze all strings for condition patterns
        def count_conditions(text: str):
            if 'always()' in text:
                conditional_stats["always_conditions"] += 1
            if 'failure()' in text:
                conditional_stats["failure_conditions"] += 1
            if 'success()' in text:
                conditional_stats["success_conditions"] += 1
        
        for job_config in data.get('jobs', {}).values():
            if isinstance(job_config, dict):
                if 'if' in job_config:
                    conditional_stats["jobs_with_conditions"] += 1
                    count_conditions(str(job_config['if']))
                
                for step in job_config.get('steps', []):
                    if isinstance(step, dict) and 'if' in step:
                        conditional_stats["steps_with_conditions"] += 1
                        count_conditions(str(step['if']))
        
        return conditional_stats
    
    def _assess_efficiency(self, findings: Dict[str, Any]) -> float:
        """Assess workflow efficiency."""
        score = 0.5
        
        # Uses caching
        if findings.get('caching', {}).get('uses_cache'):
            score += 0.15
        
        # Parallel jobs
        jobs = findings.get('jobs', {})
        if jobs.get('has_parallel_jobs'):
            score += 0.1
        
        # Matrix builds for similar jobs
        if findings.get('matrix_builds', {}).get('uses_matrix'):
            score += 0.1
        
        # Artifacts for job communication
        artifacts = findings.get('artifacts', {})
        if artifacts.get('upload_count') > 0 and artifacts.get('download_count') > 0:
            score += 0.1
        
        # Not too deep dependency chain
        if jobs.get('max_dependency_depth', 0) <= 3:
            score += 0.05
        
        return min(score, 1.0)
    
    def _assess_security(self, findings: Dict[str, Any]) -> float:
        """Assess security practices."""
        score = 0.5
        
        # Uses secrets properly
        if findings.get('secrets'):
            score += 0.1
        
        # Has permissions defined
        if findings.get('permissions'):
            score += 0.15
        
        # Uses specific action versions
        actions = findings.get('actions_used', [])
        if actions:
            versioned = sum(1 for a in actions if a.get('has_version'))
            if versioned / len(actions) > 0.8:
                score += 0.15
        
        # Uses concurrency controls
        if findings.get('concurrency'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_maintainability(self, findings: Dict[str, Any]) -> float:
        """Assess workflow maintainability."""
        score = 0.5
        
        # Has workflow name
        if findings.get('name') != 'Unnamed Workflow':
            score += 0.1
        
        # Uses environment variables
        env = findings.get('env', {})
        if env.get('workflow_level') or env.get('job_level'):
            score += 0.1
        
        # Reasonable number of jobs
        job_count = findings.get('jobs', {}).get('count', 0)
        if 1 <= job_count <= 10:
            score += 0.1
        
        # Uses conditionals appropriately
        conditionals = findings.get('conditionals', {})
        if conditionals.get('failure_conditions') > 0:
            score += 0.1  # Handles failures
        
        # Clear trigger configuration
        triggers = findings.get('triggers', {})
        if triggers.get('types'):
            score += 0.1
        
        return min(score, 1.0) 