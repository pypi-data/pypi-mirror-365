"""
Python API for Error Explainer - Programmatic usage.
"""

import sys
import traceback
from typing import Dict, Optional, Union, Callable
from contextlib import contextmanager
from .explainer import ErrorExplainer
from .rule_based_explainer import rule_explainer
from .parser import parser
from .config import config


def explain_error(
    error_content: str,
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    save_explanation: bool = False
) -> Dict:
    """
    Explain an error programmatically.
    
    Args:
        error_content: Error log content or traceback string
        use_ai: Whether to use AI explanation (True) or rule-based (False)
        api_key: Google Gemini API key (optional, uses environment variable if not provided)
        model: AI model to use (only applies when use_ai=True)
        save_explanation: Whether to save explanation to log directory
        
    Returns:
        Dictionary containing explanation and metadata
        
    Example:
        >>> import error_explainer
        >>> result = error_explainer.explain_error("NameError: name 'x' is not defined")
        >>> print(result['explanation'])
    """
    if use_ai:
        try:
            explainer = ErrorExplainer(api_key=api_key, model=model)
            result = explainer.explain_error(error_content)
        except Exception as e:
            # Fallback to rule-based if AI fails
            result = rule_explainer.explain_error(error_content)
            result['ai_fallback'] = True
            result['ai_error'] = str(e)
    else:
        result = rule_explainer.explain_error(error_content)
    
    # Save if requested
    if save_explanation and result.get('success', False):
        from .utils import save_explanation as save_func
        try:
            save_func(result)
        except Exception:
            pass  # Don't fail if saving doesn't work
    
    return result


def explain_current_exception(
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    save_explanation: bool = False
) -> Dict:
    """
    Explain the currently active exception.
    
    Args:
        use_ai: Whether to use AI explanation (True) or rule-based (False)
        api_key: Google Gemini API key (optional)
        model: AI model to use (only applies when use_ai=True)
        save_explanation: Whether to save explanation to log directory
        
    Returns:
        Dictionary containing explanation and metadata
        
    Example:
        >>> try:
        ...     undefined_variable
        ... except Exception:
        ...     result = error_explainer.explain_current_exception()
        ...     print(result['explanation'])
    """
    if not sys.exc_info()[0]:
        return {
            'success': False,
            'error': 'No active exception to explain'
        }
    
    # Get current exception info
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    # Format the exception
    error_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error_content = ''.join(error_lines)
    
    return explain_error(error_content, use_ai, api_key, model, save_explanation)


@contextmanager
def auto_explain_exceptions(
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    save_explanation: bool = False,
    on_error: Optional[Callable[[Dict], None]] = None,
    reraise: bool = True
):
    """
    Context manager to automatically explain exceptions.
    
    Args:
        use_ai: Whether to use AI explanation (True) or rule-based (False)
        api_key: Google Gemini API key (optional)
        model: AI model to use (only applies when use_ai=True)
        save_explanation: Whether to save explanation to log directory
        on_error: Callback function called with explanation when exception occurs
        reraise: Whether to reraise the exception after explaining it
        
    Example:
        >>> with error_explainer.auto_explain_exceptions() as explainer:
        ...     # Your code here
        ...     undefined_variable  # This will be automatically explained
    """
    try:
        yield
    except Exception:
        result = explain_current_exception(use_ai, api_key, model, save_explanation)
        
        if on_error:
            on_error(result)
        
        if reraise:
            raise


def explain_function_errors(
    func: Optional[Callable] = None,
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    save_explanation: bool = False,
    on_error: Optional[Callable[[Dict], None]] = None
) -> Callable:
    """
    Decorator to automatically explain errors in a function.
    
    Args:
        func: Function to decorate (optional, for decorator usage)
        use_ai: Whether to use AI explanation (True) or rule-based (False)
        api_key: Google Gemini API key (optional)
        model: AI model to use (only applies when use_ai=True)
        save_explanation: Whether to save explanation to log directory
        on_error: Callback function called with explanation when exception occurs
        
    Example:
        >>> @error_explainer.explain_function_errors()
        ... def my_function():
        ...     return undefined_variable
        >>> 
        >>> my_function()  # Errors will be automatically explained
    """
    def decorator(func_to_decorate: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func_to_decorate(*args, **kwargs)
            except Exception:
                result = explain_current_exception(use_ai, api_key, model, save_explanation)
                
                if on_error:
                    on_error(result)
                
                raise
        
        return wrapper
    
    # Handle both @explain_function_errors and @explain_function_errors()
    if func is None:
        return decorator
    else:
        return decorator(func)


def setup_logging_integration(
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    save_explanation: bool = False
):
    """
    Set up integration with Python's logging system to automatically explain errors.
    
    Args:
        use_ai: Whether to use AI explanation (True) or rule-based (False)
        api_key: Google Gemini API key (optional)
        model: AI model to use (only applies when use_ai=True)
        save_explanation: Whether to save explanation to log directory
        
    Example:
        >>> import logging
        >>> error_explainer.setup_logging_integration()
        >>> 
        >>> # Now all logged errors will be automatically explained
        >>> logging.error("Something went wrong")
    """
    import logging
    
    class ErrorExplainerHandler(logging.Handler):
        def emit(self, record):
            if record.exc_info:
                result = explain_current_exception(use_ai, api_key, model, save_explanation)
                if result.get('success', False):
                    print(f"\n🧐 Error Explanation:\n{result['explanation']}")
    
    # Add handler to root logger
    logging.getLogger().addHandler(ErrorExplainerHandler())


def explain_test_failures(
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    save_explanation: bool = False
):
    """
    Set up integration with pytest to automatically explain test failures.
    
    Args:
        use_ai: Whether to use AI explanation (True) or rule-based (False)
        api_key: Google Gemini API key (optional)
        model: AI model to use (only applies when use_ai=True)
        save_explanation: Whether to save explanation to log directory
        
    Example:
        >>> # In conftest.py
        >>> import error_explainer
        >>> error_explainer.explain_test_failures()
        >>> 
        >>> # Now test failures will be automatically explained
    """
    try:
        import pytest
        
        def pytest_runtest_logreport(report):
            if report.failed and report.longrepr:
                result = explain_error(str(report.longrepr), use_ai, api_key, model, save_explanation)
                if result.get('success', False):
                    print(f"\n🧐 Test Failure Explanation:\n{result['explanation']}")
        
        # This would need to be called from conftest.py
        return pytest_runtest_logreport
        
    except ImportError:
        print("pytest not available for test failure explanation")


# Convenience functions for common use cases
def quick_explain(error_content: str) -> str:
    """
    Quick explanation using rule-based system (no AI required).
    
    Args:
        error_content: Error log content
        
    Returns:
        Simple explanation string
        
    Example:
        >>> import error_explainer
        >>> explanation = error_explainer.quick_explain("NameError: name 'x' is not defined")
        >>> print(explanation)
    """
    result = rule_explainer.explain_error(error_content)
    return result.get('explanation', 'No explanation available')


def ai_explain(error_content: str, api_key: Optional[str] = None) -> str:
    """
    AI-powered explanation (requires API key).
    
    Args:
        error_content: Error log content
        api_key: Google Gemini API key (optional)
        
    Returns:
        AI-generated explanation string
        
    Example:
        >>> import error_explainer
        >>> explanation = error_explainer.ai_explain("NameError: name 'x' is not defined")
        >>> print(explanation)
    """
    result = explain_error(error_content, use_ai=True, api_key=api_key)
    return result.get('explanation', 'No explanation available') 