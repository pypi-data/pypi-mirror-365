"""
Document handlers initialization
"""

from .text_handlers import MarkdownHandler, TextHandler, CSVHandler, JSONHandler, YAMLHandler, TOMLHandler
from .code_handlers import PythonHandler, JavaScriptHandler, SQLHandler, JavaHandler, CppHandler
from .config_handlers import DockerfileHandler, PackageJSONHandler, RequirementsHandler, MakefileHandler

# Extended handlers
from .code_handlers_extended import (
    TypeScriptHandler, GoHandler, RustHandler, RubyHandler,
    PHPHandler, ShellScriptHandler, PowerShellHandler
)
from .config_handlers_extended import (
    INIHandler, EnvFileHandler, ApacheConfigHandler,
    NginxConfigHandler, PropertiesFileHandler
)
from .text_handlers_extended import (
    LaTeXHandler, AsciiDocHandler, ReStructuredTextHandler,
    TSVHandler, LogFileHandler, ExcelHandler
)

# New specialized handlers
from .web_style_handlers import CSSHandler, SCSSHandler
from .web_component_handlers import VueHandler, SvelteHandler
from .container_orchestration_handlers import DockerComposeHandler, TerraformHandler
from .api_definition_handlers import GraphQLHandler, ProtocolBuffersHandler
from .notebook_ci_handlers import JupyterNotebookHandler, GitHubActionsHandler
from .scientific_code_handlers import RHandler

# All available handlers for the framework
ALL_HANDLERS = [
    # Text and Data Handlers
    MarkdownHandler,
    TextHandler,
    CSVHandler,
    JSONHandler,
    YAMLHandler,
    TOMLHandler,
    TSVHandler,  # New
    ExcelHandler,  # New - basic support

    # Document Handlers (New)
    LaTeXHandler,
    AsciiDocHandler,
    ReStructuredTextHandler,
    
    # Code Handlers
    PythonHandler,
    JavaScriptHandler,
    TypeScriptHandler,  # New
    GoHandler,  # New
    RustHandler,  # New
    RubyHandler,  # New
    PHPHandler,  # New
    SQLHandler,
    JavaHandler,
    CppHandler,
    ShellScriptHandler,  # New
    PowerShellHandler,  # New
    RHandler,  # New
    
    # Configuration Handlers
    DockerfileHandler,
    PackageJSONHandler,
    RequirementsHandler,
    MakefileHandler,
    INIHandler,  # New
    EnvFileHandler,  # New
    PropertiesFileHandler,  # New
    ApacheConfigHandler,  # New
    NginxConfigHandler,  # New

    # Web Development Handlers (New)
    CSSHandler,
    SCSSHandler,
    VueHandler,
    SvelteHandler,
    
    # Infrastructure/Orchestration Handlers (New)
    DockerComposeHandler,
    TerraformHandler,
    
    # API Definition Handlers (New)
    GraphQLHandler,
    ProtocolBuffersHandler,
    
    # Notebook and CI/CD Handlers (New)
    JupyterNotebookHandler,
    GitHubActionsHandler,

    # Log Files (New)
    LogFileHandler,
]

# Handler categories for organization
HANDLER_CATEGORIES = {
    "text": [MarkdownHandler, TextHandler],
    "data": [CSVHandler, JSONHandler, YAMLHandler, TOMLHandler, TSVHandler, ExcelHandler],
    "document": [LaTeXHandler, AsciiDocHandler, ReStructuredTextHandler],
    "code": [
        PythonHandler, JavaScriptHandler, TypeScriptHandler, GoHandler,
        RustHandler, RubyHandler, PHPHandler, SQLHandler, JavaHandler,
        CppHandler, ShellScriptHandler, PowerShellHandler, RHandler
    ],
    "config": [
        DockerfileHandler, PackageJSONHandler, RequirementsHandler,
        MakefileHandler, INIHandler, EnvFileHandler, PropertiesFileHandler,
        ApacheConfigHandler, NginxConfigHandler
    ],
    "web": [CSSHandler, SCSSHandler, VueHandler, SvelteHandler],
    "infrastructure": [DockerComposeHandler, TerraformHandler],
    "api": [GraphQLHandler, ProtocolBuffersHandler],
    "notebook": [JupyterNotebookHandler],
    "ci": [GitHubActionsHandler],
    "logs": [LogFileHandler],
}

def get_handlers_by_category(category: str):
    """Get all handlers for a specific category"""
    return HANDLER_CATEGORIES.get(category, [])

def get_handler_info():
    """Get information about all registered handlers"""
    info = {
        "total_handlers": len(ALL_HANDLERS),
        "categories": list(HANDLER_CATEGORIES.keys()),
        "handlers_by_category": {
            cat: len(handlers) for cat, handlers in HANDLER_CATEGORIES.items()
        }
    }
    return info

__all__ = [
    'ALL_HANDLERS',
    'HANDLER_CATEGORIES',
    'get_handlers_by_category',
    'get_handler_info'
]