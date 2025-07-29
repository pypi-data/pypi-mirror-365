"""
XError - AI-powered error analysis and explanation tool.

A smart CLI tool to analyze error logs from multiple programming languages (Python, 
JavaScript, TypeScript, C++, Java) and return AI-generated explanations and fix 
suggestions using Google's Gemini AI.
"""

__version__ = "1.0.0"
__author__ = "Avishek Devnath"
__email__ = "avishekdevnath@gmail.com"

from .explainer import explain_error as ai_explain_error
from .rule_based_explainer import rule_explainer
from .cli import main

# Import API functions
from .api import (
    explain_error,
    explain_current_exception,
    auto_explain_exceptions,
    explain_function_errors,
    setup_logging_integration,
    explain_test_failures,
    quick_explain,
    ai_explain
)

# Import watcher functions
from .watcher import (
    watch_process,
    stop_background_watcher,
    list_background_watchers,
    stop_all_background_watchers
)

# Import multi-language functions
from .language_parsers import (
    detect_language,
    parse_error,
    get_supported_languages,
    Language
)

__all__ = [
    # Core functions
    "explain_error",
    "explain_current_exception",
    "auto_explain_exceptions",
    "explain_function_errors",
    
    # Integration functions
    "setup_logging_integration",
    "explain_test_failures",
    
    # Watcher functions
    "watch_process",
    "stop_background_watcher",
    "list_background_watchers",
    "stop_all_background_watchers",
    
    # Multi-language functions
    "detect_language",
    "parse_error",
    "get_supported_languages",
    "Language",
    
    # Convenience functions
    "quick_explain",
    "ai_explain",
    
    # CLI
    "main",
    
    # Internal components (for advanced users)
    "rule_explainer",
    "ai_explain_error"
] 