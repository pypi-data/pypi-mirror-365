"""
Scientific programming language handlers for R

Handles analysis of statistical and data science code files,
particularly R scripts and R Markdown documents.
"""

from typing import Dict, Any, Tuple, List, Optional
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import DocumentHandler, DocumentTypeInfo, SpecializedAnalysis


class RHandler(DocumentHandler):
    """
    Handler for R language files (.r, .R).
    
    Analyzes R scripts including functions, data operations,
    statistical analyses, and visualization code.
    """
    
    def can_handle(self, file_path: str, mime_type: str, content: bytes) -> Tuple[bool, float]:
        """Check if this handler can process the R file."""
        if file_path.endswith(('.r', '.R')):
            return True, 0.95
        
        try:
            text = content.decode('utf-8', errors='ignore')
            # R-specific patterns
            if any(pattern in text for pattern in [
                '<-', '<<-',  # R assignment operators
                'function(', 'function (',  # Function definitions
                'library(', 'require(',  # Package loading
                'data.frame(', 'c(',  # Common R functions
                '%%', '%>%',  # Operators
                'ggplot(', 'plot(',  # Plotting
                'lm(', 'glm('  # Statistical models
            ]):
                # Count R-specific patterns
                r_score = 0
                r_score += len(re.findall(r'<-', text)) * 0.1
                r_score += len(re.findall(r'function\s*\(', text)) * 0.2
                r_score += len(re.findall(r'(library|require)\s*\(', text)) * 0.15
                
                return True, min(0.7 + r_score, 0.9)
        except:
            pass
        
        return False, 0.0
    
    def detect_type(self, file_path: str, mime_type: str, content: bytes) -> DocumentTypeInfo:
        """Detect R script type and features."""
        text = content.decode('utf-8', errors='ignore')
        
        # Detect script type
        if 'shiny' in text.lower() and any(x in text for x in ['ui', 'server', 'shinyApp']):
            type_name = "R Shiny Application"
        elif re.search(r'(ggplot|plot|hist|boxplot|barplot)\s*\(', text):
            type_name = "R Visualization Script"
        elif re.search(r'(lm|glm|aov|t\.test|cor\.test)\s*\(', text):
            type_name = "R Statistical Analysis"
        elif 'test_that(' in text or 'testthat::' in text:
            type_name = "R Test Script"
        else:
            type_name = "R Script"
        
        return DocumentTypeInfo(
            type_name=type_name,
            confidence=0.95,
            category="code",
            language="r",
            format="r"
        )
    
    def analyze(self, file_path: str, content: bytes) -> SpecializedAnalysis:
        """Perform detailed R script analysis."""
        findings = self.extract_key_data(file_path, content)
        
        return SpecializedAnalysis(
            document_type="R",
            category="code",
            key_findings=findings,
            ai_use_cases=[
                "Statistical code optimization",
                "Data pipeline generation",
                "Visualization enhancement",
                "Function documentation",
                "Package dependency analysis",
                "Performance optimization"
            ],
            quality_metrics={
                "code_style": self._assess_code_style(findings),
                "statistical_rigor": self._assess_statistical_rigor(findings),
                "reproducibility": self._assess_reproducibility(findings),
                "ai_readiness": 0.85
            },
            structured_data=findings
        )
    
    def extract_key_data(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """Extract R script structure and patterns."""
        text = content.decode('utf-8', errors='ignore')
        
        # Remove comments for some analyses
        text_no_comments = re.sub(r'#[^\n]*', '', text)
        
        return {
            "packages": self._extract_packages(text),
            "functions": self._extract_functions(text_no_comments),
            "variables": self._extract_variables(text_no_comments),
            "data_operations": self._extract_data_operations(text_no_comments),
            "statistical_tests": self._extract_statistical_tests(text_no_comments),
            "visualizations": self._extract_visualizations(text_no_comments),
            "control_flow": self._extract_control_flow(text_no_comments),
            "pipe_usage": self._analyze_pipe_usage(text_no_comments),
            "comments": self._analyze_comments(text),
            "code_patterns": self._extract_code_patterns(text_no_comments),
            "file_io": self._extract_file_io(text_no_comments),
            "shiny_components": self._extract_shiny_components(text_no_comments) if 'shiny' in text.lower() else {}
        }
    
    def _extract_packages(self, text: str) -> Dict[str, Any]:
        """Extract package usage information."""
        packages = {
            "loaded": [],
            "attached": [],
            "namespaced": [],
            "installed": []
        }
        
        # library() and require() calls
        for match in re.finditer(r'(library|require)\s*\(\s*["\']?(\w+)["\']?\s*\)', text):
            func = match.group(1)
            pkg = match.group(2)
            
            if func == 'library':
                packages["loaded"].append(pkg)
            else:
                packages["attached"].append(pkg)
        
        # Namespaced calls (pkg::function)
        for match in re.finditer(r'(\w+)::', text):
            pkg = match.group(1)
            if pkg not in packages["namespaced"]:
                packages["namespaced"].append(pkg)
        
        # install.packages() calls
        for match in re.finditer(r'install\.packages\s*\(\s*["\']([^"\']+)["\']', text):
            packages["installed"].append(match.group(1))
        
        # Categorize packages
        all_packages = set(packages["loaded"] + packages["attached"] + packages["namespaced"])
        
        packages["categories"] = self._categorize_packages(all_packages)
        packages["total_unique"] = len(all_packages)
        
        return packages
    
    def _categorize_packages(self, packages: set) -> Dict[str, List[str]]:
        """Categorize R packages by their primary use."""
        categories = {
            "tidyverse": [],
            "visualization": [],
            "statistics": [],
            "machine_learning": [],
            "data_import": [],
            "shiny": [],
            "other": []
        }
        
        # Package categorization
        tidyverse_pkgs = {'tidyverse', 'dplyr', 'ggplot2', 'tidyr', 'readr', 'purrr', 'tibble', 'stringr', 'forcats'}
        viz_pkgs = {'ggplot2', 'plotly', 'lattice', 'ggvis', 'highcharter', 'leaflet', 'networkD3'}
        stats_pkgs = {'stats', 'MASS', 'nlme', 'lme4', 'survival', 'forecast', 'tseries'}
        ml_pkgs = {'caret', 'randomForest', 'xgboost', 'e1071', 'nnet', 'rpart', 'glmnet'}
        data_pkgs = {'readr', 'readxl', 'haven', 'foreign', 'data.table', 'DBI', 'odbc'}
        shiny_pkgs = {'shiny', 'shinydashboard', 'shinyWidgets', 'DT', 'plotly'}
        
        for pkg in packages:
            if pkg in tidyverse_pkgs:
                categories["tidyverse"].append(pkg)
            elif pkg in viz_pkgs:
                categories["visualization"].append(pkg)
            elif pkg in stats_pkgs:
                categories["statistics"].append(pkg)
            elif pkg in ml_pkgs:
                categories["machine_learning"].append(pkg)
            elif pkg in data_pkgs:
                categories["data_import"].append(pkg)
            elif pkg in shiny_pkgs:
                categories["shiny"].append(pkg)
            else:
                categories["other"].append(pkg)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _extract_functions(self, text: str) -> List[Dict[str, Any]]:
        """Extract function definitions."""
        functions = []
        
        # Standard function definitions
        for match in re.finditer(r'(\w+)\s*<-\s*function\s*\(([^)]*)\)', text):
            func_name = match.group(1)
            params = match.group(2).strip()
            
            functions.append({
                "name": func_name,
                "params": params,
                "param_count": len(params.split(',')) if params else 0,
                "has_defaults": '=' in params
            })
        
        # Alternative assignment
        for match in re.finditer(r'(\w+)\s*=\s*function\s*\(([^)]*)\)', text):
            func_name = match.group(1)
            params = match.group(2).strip()
            
            functions.append({
                "name": func_name,
                "params": params,
                "param_count": len(params.split(',')) if params else 0,
                "has_defaults": '=' in params
            })
        
        return functions
    
    def _extract_variables(self, text: str) -> Dict[str, Any]:
        """Extract variable assignments and data structures."""
        variables = {
            "assignments": 0,
            "data_frames": [],
            "vectors": [],
            "lists": [],
            "matrices": [],
            "models": [],
            "constants": []
        }
        
        # Count assignments
        variables["assignments"] = len(re.findall(r'<-|=(?!=)', text))
        
        # Data frames
        for match in re.finditer(r'(\w+)\s*<-\s*(?:data\.frame|read\.|.*_read|as\.data\.frame)', text):
            var_name = match.group(1)
            if var_name not in variables["data_frames"]:
                variables["data_frames"].append(var_name)
        
        # Vectors
        for match in re.finditer(r'(\w+)\s*<-\s*c\(', text):
            var_name = match.group(1)
            if var_name not in variables["vectors"]:
                variables["vectors"].append(var_name)
        
        # Lists
        for match in re.finditer(r'(\w+)\s*<-\s*list\(', text):
            var_name = match.group(1)
            if var_name not in variables["lists"]:
                variables["lists"].append(var_name)
        
        # Matrices
        for match in re.finditer(r'(\w+)\s*<-\s*(?:matrix|as\.matrix)', text):
            var_name = match.group(1)
            if var_name not in variables["matrices"]:
                variables["matrices"].append(var_name)
        
        # Models
        for match in re.finditer(r'(\w+)\s*<-\s*(?:lm|glm|aov|gam|randomForest|xgboost)', text):
            var_name = match.group(1)
            if var_name not in variables["models"]:
                variables["models"].append(var_name)
        
        # Constants (UPPER_CASE)
        for match in re.finditer(r'([A-Z_]+)\s*<-', text):
            const_name = match.group(1)
            if const_name not in variables["constants"]:
                variables["constants"].append(const_name)
        
        return variables
    
    def _extract_data_operations(self, text: str) -> Dict[str, Any]:
        """Extract data manipulation operations."""
        operations = {
            "dplyr_verbs": {},
            "base_r": {},
            "data_table": {},
            "joins": [],
            "reshaping": []
        }
        
        # dplyr verbs
        dplyr_verbs = ['filter', 'select', 'mutate', 'arrange', 'summarize', 'summarise', 'group_by', 'ungroup']
        for verb in dplyr_verbs:
            count = len(re.findall(rf'{verb}\s*\(', text))
            if count > 0:
                operations["dplyr_verbs"][verb] = count
        
        # Base R operations
        base_ops = ['subset', 'merge', 'aggregate', 'tapply', 'lapply', 'sapply', 'apply']
        for op in base_ops:
            count = len(re.findall(rf'{op}\s*\(', text))
            if count > 0:
                operations["base_r"][op] = count
        
        # Joins
        join_types = ['left_join', 'right_join', 'inner_join', 'full_join', 'anti_join', 'semi_join']
        for join in join_types:
            if re.search(rf'{join}\s*\(', text):
                operations["joins"].append(join)
        
        # Reshaping
        reshape_ops = ['pivot_longer', 'pivot_wider', 'gather', 'spread', 'melt', 'dcast']
        for op in reshape_ops:
            if re.search(rf'{op}\s*\(', text):
                operations["reshaping"].append(op)
        
        return operations
    
    def _extract_statistical_tests(self, text: str) -> List[Dict[str, str]]:
        """Extract statistical tests and models."""
        tests = []
        
        # Common statistical tests
        stat_functions = {
            't.test': 't-test',
            'wilcox.test': 'Wilcoxon test',
            'cor.test': 'Correlation test',
            'chisq.test': 'Chi-squared test',
            'aov': 'ANOVA',
            'lm': 'Linear regression',
            'glm': 'Generalized linear model',
            'lmer': 'Linear mixed-effects model',
            'glmer': 'Generalized linear mixed-effects model',
            'anova': 'ANOVA comparison',
            'kruskal.test': 'Kruskal-Wallis test',
            'shapiro.test': 'Shapiro-Wilk test',
            'ks.test': 'Kolmogorov-Smirnov test'
        }
        
        for func, test_name in stat_functions.items():
            if re.search(rf'{func}\s*\(', text):
                tests.append({
                    "function": func,
                    "test_type": test_name,
                    "count": len(re.findall(rf'{func}\s*\(', text))
                })
        
        return tests
    
    def _extract_visualizations(self, text: str) -> Dict[str, Any]:
        """Extract visualization code."""
        viz_info = {
            "base_r_plots": {},
            "ggplot2": {},
            "other_packages": {},
            "plot_types": []
        }
        
        # Base R plotting
        base_plots = ['plot', 'hist', 'boxplot', 'barplot', 'pie', 'pairs', 'heatmap']
        for plot in base_plots:
            count = len(re.findall(rf'{plot}\s*\(', text))
            if count > 0:
                viz_info["base_r_plots"][plot] = count
        
        # ggplot2
        if 'ggplot' in text:
            viz_info["ggplot2"]["uses_ggplot"] = True
            
            # Geoms
            geoms = re.findall(r'geom_(\w+)\s*\(', text)
            viz_info["ggplot2"]["geoms"] = list(set(geoms))
            
            # Themes
            themes = re.findall(r'theme_(\w+)\s*\(', text)
            viz_info["ggplot2"]["themes"] = list(set(themes))
            
            # Faceting
            if re.search(r'facet_(wrap|grid)\s*\(', text):
                viz_info["ggplot2"]["uses_faceting"] = True
        
        # Other visualization packages
        other_viz = ['plotly', 'lattice', 'highcharter', 'leaflet']
        for pkg in other_viz:
            if re.search(rf'{pkg}::', text):
                viz_info["other_packages"][pkg] = True
        
        # Identify plot types
        if 'scatter' in text.lower() or 'geom_point' in text:
            viz_info["plot_types"].append("scatter")
        if 'bar' in text.lower() or 'geom_bar' in text or 'barplot' in text:
            viz_info["plot_types"].append("bar")
        if 'line' in text.lower() or 'geom_line' in text:
            viz_info["plot_types"].append("line")
        if 'box' in text.lower() or 'geom_boxplot' in text or 'boxplot' in text:
            viz_info["plot_types"].append("boxplot")
        
        return viz_info
    
    def _extract_control_flow(self, text: str) -> Dict[str, int]:
        """Extract control flow structures."""
        return {
            "if_statements": len(re.findall(r'\bif\s*\(', text)),
            "else_statements": len(re.findall(r'\belse\b', text)),
            "for_loops": len(re.findall(r'\bfor\s*\(', text)),
            "while_loops": len(re.findall(r'\bwhile\s*\(', text)),
            "repeat_loops": len(re.findall(r'\brepeat\s*\{', text)),
            "switch_statements": len(re.findall(r'\bswitch\s*\(', text)),
            "tryCatch": len(re.findall(r'\btryCatch\s*\(', text))
        }
    
    def _analyze_pipe_usage(self, text: str) -> Dict[str, Any]:
        """Analyze pipe operator usage."""
        return {
            "magrittr_pipes": len(re.findall(r'%>%', text)),
            "native_pipes": len(re.findall(r'\|>', text)),
            "exposition_pipes": len(re.findall(r'%\$%', text)),
            "tee_pipes": len(re.findall(r'%T>%', text)),
            "assignment_pipes": len(re.findall(r'%<>%', text)),
            "uses_pipes": '%>%' in text or '|>' in text
        }
    
    def _analyze_comments(self, text: str) -> Dict[str, Any]:
        """Analyze code comments."""
        comments = re.findall(r'#[^\n]*', text)
        
        # Categorize comments
        roxygen_comments = [c for c in comments if c.startswith("#'")]
        section_comments = [c for c in comments if c.startswith('# ----') or c.startswith('# ====')]
        todo_comments = [c for c in comments if 'TODO' in c.upper() or 'FIXME' in c.upper()]
        
        return {
            "total_comments": len(comments),
            "roxygen_comments": len(roxygen_comments),
            "section_comments": len(section_comments),
            "todo_comments": len(todo_comments),
            "comment_ratio": len(comments) / max(len(text.split('\n')), 1),
            "has_roxygen": len(roxygen_comments) > 0
        }
    
    def _extract_code_patterns(self, text: str) -> Dict[str, Any]:
        """Extract common R coding patterns."""
        patterns = {
            "uses_tidyverse_style": False,
            "uses_base_r_style": False,
            "uses_s3_methods": False,
            "uses_s4_classes": False,
            "uses_r6_classes": False,
            "uses_environments": False,
            "uses_closures": False
        }
        
        # Tidyverse style indicators
        if '%>%' in text and any(verb in text for verb in ['mutate', 'filter', 'select']):
            patterns["uses_tidyverse_style"] = True
        
        # Base R style indicators
        if '$' in text and '[' in text and not patterns["uses_tidyverse_style"]:
            patterns["uses_base_r_style"] = True
        
        # S3 methods
        if re.search(r'UseMethod\s*\(', text) or re.search(r'\.\w+\s*<-\s*function', text):
            patterns["uses_s3_methods"] = True
        
        # S4 classes
        if re.search(r'setClass\s*\(', text) or re.search(r'setMethod\s*\(', text):
            patterns["uses_s4_classes"] = True
        
        # R6 classes
        if 'R6Class' in text:
            patterns["uses_r6_classes"] = True
        
        # Environments
        if re.search(r'new\.env\s*\(', text) or re.search(r'environment\s*\(', text):
            patterns["uses_environments"] = True
        
        # Closures (functions returning functions)
        if re.search(r'function\s*\([^)]*\)\s*\{[^}]*function\s*\(', text):
            patterns["uses_closures"] = True
        
        return patterns
    
    def _extract_file_io(self, text: str) -> Dict[str, Any]:
        """Extract file I/O operations."""
        file_io = {
            "read_operations": {},
            "write_operations": {},
            "data_formats": []
        }
        
        # Read operations
        read_funcs = {
            'read.csv': 'csv',
            'read.table': 'table',
            'readRDS': 'rds',
            'load': 'rdata',
            'read_csv': 'csv',
            'read_excel': 'excel',
            'read_json': 'json',
            'fread': 'csv/table'
        }
        
        for func, format_type in read_funcs.items():
            if re.search(rf'{func}\s*\(', text):
                file_io["read_operations"][func] = True
                if format_type not in file_io["data_formats"]:
                    file_io["data_formats"].append(format_type)
        
        # Write operations
        write_funcs = {
            'write.csv': 'csv',
            'write.table': 'table',
            'saveRDS': 'rds',
            'save': 'rdata',
            'write_csv': 'csv',
            'write_excel': 'excel',
            'write_json': 'json',
            'fwrite': 'csv/table'
        }
        
        for func, format_type in write_funcs.items():
            if re.search(rf'{func}\s*\(', text):
                file_io["write_operations"][func] = True
        
        return file_io
    
    def _extract_shiny_components(self, text: str) -> Dict[str, Any]:
        """Extract Shiny app components if present."""
        shiny_info = {
            "ui_components": [],
            "server_components": [],
            "reactive_components": [],
            "has_ui": False,
            "has_server": False,
            "app_type": None
        }
        
        # UI components
        ui_elements = ['fluidPage', 'dashboardPage', 'navbarPage', 'fixedPage', 
                      'sidebarLayout', 'tabsetPanel', 'conditionalPanel']
        for element in ui_elements:
            if element in text:
                shiny_info["ui_components"].append(element)
                shiny_info["has_ui"] = True
        
        # Input/Output components
        inputs = re.findall(r'(textInput|numericInput|selectInput|sliderInput|checkboxInput|dateInput|fileInput)\s*\(', text)
        outputs = re.findall(r'(plotOutput|tableOutput|textOutput|verbatimTextOutput|uiOutput|downloadHandler)\s*\(', text)
        
        shiny_info["ui_components"].extend([f"input:{i}" for i in set(inputs)])
        shiny_info["ui_components"].extend([f"output:{o}" for o in set(outputs)])
        
        # Server components
        if 'function(input, output' in text:
            shiny_info["has_server"] = True
        
        # Reactive components
        reactive_patterns = ['reactive', 'observe', 'observeEvent', 'reactiveValues', 'eventReactive']
        for pattern in reactive_patterns:
            if re.search(rf'{pattern}\s*\(', text):
                shiny_info["reactive_components"].append(pattern)
        
        # Determine app type
        if 'shinyApp(' in text:
            shiny_info["app_type"] = "single_file"
        elif shiny_info["has_ui"] and shiny_info["has_server"]:
            shiny_info["app_type"] = "multi_file"
        elif 'shinydashboard' in text:
            shiny_info["app_type"] = "dashboard"
        
        return shiny_info
    
    def _assess_code_style(self, findings: Dict[str, Any]) -> float:
        """Assess R code style and organization."""
        score = 0.5
        
        # Uses consistent style
        patterns = findings.get('code_patterns', {})
        if patterns.get('uses_tidyverse_style') or patterns.get('uses_base_r_style'):
            score += 0.15
        
        # Good commenting
        comments = findings.get('comments', {})
        if comments.get('comment_ratio', 0) > 0.1:
            score += 0.1
        
        # Uses functions
        if findings.get('functions'):
            score += 0.15
        
        # Organized with sections
        if comments.get('section_comments', 0) > 0:
            score += 0.1
        
        # Uses roxygen for documentation
        if comments.get('has_roxygen'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_statistical_rigor(self, findings: Dict[str, Any]) -> float:
        """Assess statistical analysis quality."""
        score = 0.5
        
        # Uses statistical tests
        if findings.get('statistical_tests'):
            score += 0.2
        
        # Multiple test types (comprehensive analysis)
        test_types = set(t['test_type'] for t in findings.get('statistical_tests', []))
        if len(test_types) > 2:
            score += 0.1
        
        # Uses appropriate packages
        packages = findings.get('packages', {}).get('categories', {})
        if 'statistics' in packages or 'machine_learning' in packages:
            score += 0.1
        
        # Has visualizations (for exploring data)
        viz = findings.get('visualizations', {})
        if viz.get('base_r_plots') or viz.get('ggplot2'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_reproducibility(self, findings: Dict[str, Any]) -> float:
        """Assess code reproducibility."""
        score = 0.5
        
        # Loads packages explicitly
        packages = findings.get('packages', {})
        if packages.get('loaded') or packages.get('attached'):
            score += 0.15
        
        # Has file I/O (saves results)
        file_io = findings.get('file_io', {})
        if file_io.get('write_operations'):
            score += 0.1
        
        # Uses functions (modular code)
        if findings.get('functions'):
            score += 0.15
        
        # Error handling
        control_flow = findings.get('control_flow', {})
        if control_flow.get('tryCatch', 0) > 0:
            score += 0.1
        
        # Uses constants
        variables = findings.get('variables', {})
        if variables.get('constants'):
            score += 0.05
        
        return min(score, 1.0) 