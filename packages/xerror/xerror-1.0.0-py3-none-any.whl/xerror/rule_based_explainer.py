"""
Rule-based error explanation system for Error Explainer.
This module provides AI-independent error analysis and explanations.
"""

import re
from typing import Dict, List, Optional
from .parser import parser


class RuleBasedExplainer:
    """Rule-based error explanation system that works offline."""
    
    def __init__(self):
        # Comprehensive error patterns and explanations
        self.error_patterns = {
            'NameError': {
                'patterns': [
                    r"name '(\w+)' is not defined",
                    r"name '(\w+)' is not defined in this scope",
                ],
                'explanation': "This error occurs when you try to use a variable or function that hasn't been defined or imported.",
                'fixes': [
                    "Define the variable before using it: `variable_name = value`",
                    "Import the required module: `from module import function`",
                    "Check for typos in variable names",
                    "Ensure the variable is in the correct scope"
                ],
                'prevention': [
                    "Always define variables before using them",
                    "Use meaningful variable names to avoid typos",
                    "Import required modules at the top of your file",
                    "Use an IDE with autocomplete to catch undefined variables"
                ]
            },
            
            'SyntaxError': {
                'patterns': [
                    r"invalid syntax",
                    r"unexpected indent",
                    r"unexpected token",
                    r"missing parentheses",
                    r"invalid character",
                ],
                'explanation': "This error occurs when Python cannot parse your code due to incorrect syntax.",
                'fixes': [
                    "Check for missing colons `:` after if/for/while/def statements",
                    "Ensure proper indentation (use spaces, not tabs)",
                    "Check for unmatched parentheses, brackets, or braces",
                    "Look for missing commas in lists/tuples",
                    "Check for invalid characters or encoding issues"
                ],
                'prevention': [
                    "Use a code editor with syntax highlighting",
                    "Follow PEP 8 style guidelines",
                    "Use consistent indentation (4 spaces recommended)",
                    "Enable linting tools in your IDE"
                ]
            },
            
            'IndentationError': {
                'patterns': [
                    r"unexpected indent",
                    r"expected an indented block",
                    r"unindent does not match any outer indentation level",
                ],
                'explanation': "This error occurs when the indentation of your code is incorrect or inconsistent.",
                'fixes': [
                    "Use consistent indentation (4 spaces recommended)",
                    "Check for mixed tabs and spaces",
                    "Ensure proper indentation after colons `:`",
                    "Fix indentation levels to match the code structure"
                ],
                'prevention': [
                    "Configure your editor to use spaces instead of tabs",
                    "Use consistent indentation throughout your code",
                    "Enable 'show whitespace' in your editor",
                    "Use auto-formatting tools like Black"
                ]
            },
            
            'ImportError': {
                'patterns': [
                    r"No module named '(\w+)'",
                    r"cannot import name '(\w+)' from '(\w+)'",
                    r"ImportError: No module named '(\w+)'",
                ],
                'explanation': "This error occurs when Python cannot find or import a module or specific item from a module.",
                'fixes': [
                    "Install the missing package: `pip install package_name`",
                    "Check if the module name is spelled correctly",
                    "Verify the module is in your Python path",
                    "Use virtual environments to manage dependencies"
                ],
                'prevention': [
                    "Use requirements.txt to track dependencies",
                    "Use virtual environments for each project",
                    "Keep your packages updated",
                    "Document all external dependencies"
                ]
            },
            
            'TypeError': {
                'patterns': [
                    r"unsupported operand type\(s\) for (\w+): '(\w+)' and '(\w+)'",
                    r"'(\w+)' object is not callable",
                    r"object of type '(\w+)' has no len\(\)",
                    r"can only concatenate (\w+) \(not '(\w+)'\) to (\w+)",
                ],
                'explanation': "This error occurs when you perform an operation on incompatible data types.",
                'fixes': [
                    "Convert data types explicitly: `str(number)`, `int(string)`",
                    "Check variable types before operations: `type(variable)`",
                    "Use appropriate data structures for your operations",
                    "Handle None values before operations"
                ],
                'prevention': [
                    "Use type hints in your code",
                    "Validate input data types",
                    "Use isinstance() to check types before operations",
                    "Write unit tests to catch type errors early"
                ]
            },
            
            'ValueError': {
                'patterns': [
                    r"invalid literal for (\w+)\(\) with base (\d+): '(\w+)'",
                    r"could not convert string to (\w+): '(\w+)'",
                    r"invalid value",
                ],
                'explanation': "This error occurs when a function receives an argument of the correct type but inappropriate value.",
                'fixes': [
                    "Validate input values before passing to functions",
                    "Use try/except blocks to handle conversion errors",
                    "Check for empty strings or None values",
                    "Ensure values are within expected ranges"
                ],
                'prevention': [
                    "Add input validation to your functions",
                    "Use default values for optional parameters",
                    "Document expected value ranges and formats",
                    "Write defensive code that handles edge cases"
                ]
            },
            
            'KeyError': {
                'patterns': [
                    r"'(\w+)'",
                    r"KeyError: '(\w+)'",
                ],
                'explanation': "This error occurs when you try to access a dictionary key that doesn't exist.",
                'fixes': [
                    "Use .get() method with default value: `dict.get(key, default)`",
                    "Check if key exists: `if key in dict:`",
                    "Use try/except to handle missing keys",
                    "Initialize dictionary with all required keys"
                ],
                'prevention': [
                    "Always check if keys exist before accessing them",
                    "Use defaultdict for automatic key creation",
                    "Initialize dictionaries with all expected keys",
                    "Use .get() method instead of direct access"
                ]
            },
            
            'AttributeError': {
                'patterns': [
                    r"'(\w+)' object has no attribute '(\w+)'",
                    r"module '(\w+)' has no attribute '(\w+)'",
                ],
                'explanation': "This error occurs when you try to access an attribute or method that doesn't exist on an object.",
                'fixes': [
                    "Check the object's type: `type(object)`",
                    "Use dir() to see available attributes: `dir(object)`",
                    "Check documentation for correct attribute names",
                    "Ensure the object is of the expected type"
                ],
                'prevention': [
                    "Use type hints to catch attribute errors early",
                    "Read documentation for libraries you use",
                    "Use IDE autocomplete to see available attributes",
                    "Write unit tests to verify object behavior"
                ]
            },
            
            'IndexError': {
                'patterns': [
                    r"list index out of range",
                    r"string index out of range",
                    r"tuple index out of range",
                ],
                'explanation': "This error occurs when you try to access an index that doesn't exist in a sequence (list, tuple, string).",
                'fixes': [
                    "Check sequence length: `len(sequence)`",
                    "Use valid index ranges: `0 to len(sequence)-1`",
                    "Use try/except to handle index errors",
                    "Use negative indexing carefully: `-1` is the last element"
                ],
                'prevention': [
                    "Always check sequence length before indexing",
                    "Use enumerate() for index-based loops",
                    "Validate index values before using them",
                    "Consider using .get() for dictionaries instead of lists"
                ]
            },
            
            'ZeroDivisionError': {
                'patterns': [
                    r"division by zero",
                    r"ZeroDivisionError",
                ],
                'explanation': "This error occurs when you try to divide by zero, which is mathematically undefined.",
                'fixes': [
                    "Check if denominator is zero before division",
                    "Use conditional statements: `if denominator != 0:`",
                    "Provide default values for zero cases",
                    "Use try/except to handle division errors"
                ],
                'prevention': [
                    "Always validate denominators before division",
                    "Use defensive programming practices",
                    "Consider edge cases in mathematical operations",
                    "Write tests for boundary conditions"
                ]
            },
            
            'FileNotFoundError': {
                'patterns': [
                    r"No such file or directory: '([^']+)'",
                    r"FileNotFoundError: [Errno 2] No such file or directory",
                ],
                'explanation': "This error occurs when Python cannot find the specified file or directory.",
                'fixes': [
                    "Check if the file path is correct",
                    "Use absolute paths or correct relative paths",
                    "Ensure the file exists before trying to open it",
                    "Check file permissions"
                ],
                'prevention': [
                    "Use pathlib for robust path handling",
                    "Always check if files exist before operations",
                    "Use try/except for file operations",
                    "Document expected file locations"
                ]
            },
            
            'PermissionError': {
                'patterns': [
                    r"Permission denied",
                    r"PermissionError: [Errno 13] Permission denied",
                ],
                'explanation': "This error occurs when you don't have sufficient permissions to access a file or directory.",
                'fixes': [
                    "Check file permissions and ownership",
                    "Run with appropriate user privileges",
                    "Use different file locations with write access",
                    "Close files before trying to delete them"
                ],
                'prevention': [
                    "Use appropriate file permissions",
                    "Handle permission errors gracefully",
                    "Use user-specific directories when possible",
                    "Test with different permission scenarios"
                ]
            },
            
            'ModuleNotFoundError': {
                'patterns': [
                    r"No module named '(\w+)'",
                    r"ModuleNotFoundError: No module named '(\w+)'",
                ],
                'explanation': "This error occurs when Python cannot find a module that you're trying to import.",
                'fixes': [
                    "Install the missing module: `pip install module_name`",
                    "Check if the module name is spelled correctly",
                    "Verify the module is in your Python path",
                    "Use virtual environments to manage dependencies"
                ],
                'prevention': [
                    "Use requirements.txt for dependency management",
                    "Use virtual environments for project isolation",
                    "Keep a list of all project dependencies",
                    "Test imports in a clean environment"
                ]
            }
        }
    
    def explain_error(self, error_content: str) -> Dict:
        """
        Explain an error using rule-based analysis.
        
        Args:
            error_content: Raw error log content
            
        Returns:
            Dictionary containing explanation and metadata
        """
        # Parse the error first
        parsed_error = parser.parse_error_log(error_content)
        
        if not parsed_error['is_valid_error']:
            return {
                'success': False,
                'error': 'No valid Python error detected in the content',
                'explanation': None,
                'parsed_error': parsed_error,
                'method': 'rule-based'
            }
        
        # Get error type and message
        error_type = parsed_error.get('error_type', 'Unknown')
        error_message = parsed_error.get('error_message', '')
        
        # Find matching pattern
        explanation_data = self._find_explanation(error_type, error_message, error_content)
        
        if explanation_data:
            return {
                'success': True,
                'explanation': explanation_data['formatted_explanation'],
                'parsed_error': parsed_error,
                'method': 'rule-based',
                'error_summary': parser.extract_error_summary(error_content),
                'confidence': explanation_data['confidence']
            }
        else:
            # Generic explanation for unknown errors
            return {
                'success': True,
                'explanation': self._generate_generic_explanation(error_type, error_message),
                'parsed_error': parsed_error,
                'method': 'rule-based',
                'error_summary': parser.extract_error_summary(error_content),
                'confidence': 'low'
            }
    
    def _find_explanation(self, error_type: str, error_message: str, full_content: str) -> Optional[Dict]:
        """Find the best matching explanation for the error."""
        best_match = None
        highest_confidence = 0
        
        for pattern_name, pattern_data in self.error_patterns.items():
            confidence = 0
            
            # Check if error type matches
            if error_type.lower() == pattern_name.lower():
                confidence += 50
            
            # Check pattern matches in error message
            for pattern in pattern_data['patterns']:
                if re.search(pattern, error_message, re.IGNORECASE):
                    confidence += 30
                    break
            
            # Check pattern matches in full content
            for pattern in pattern_data['patterns']:
                if re.search(pattern, full_content, re.IGNORECASE):
                    confidence += 20
                    break
            
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_match = {
                    'pattern_name': pattern_name,
                    'pattern_data': pattern_data,
                    'confidence': confidence
                }
        
        if best_match and best_match['confidence'] > 30:
            return {
                'formatted_explanation': self._format_explanation(best_match['pattern_data']),
                'confidence': 'high' if best_match['confidence'] > 70 else 'medium'
            }
        
        return None
    
    def _format_explanation(self, pattern_data: Dict) -> str:
        """Format the explanation in a consistent way."""
        explanation = f"🧐 **Explanation:**\n{pattern_data['explanation']}\n\n"
        
        explanation += "🔧 **Suggested Fixes:**\n"
        for i, fix in enumerate(pattern_data['fixes'], 1):
            explanation += f"{i}. {fix}\n"
        
        explanation += "\n💡 **Prevention Tips:**\n"
        for i, tip in enumerate(pattern_data['prevention'], 1):
            explanation += f"{i}. {tip}\n"
        
        return explanation
    
    def _generate_generic_explanation(self, error_type: str, error_message: str) -> str:
        """Generate a generic explanation for unknown errors."""
        return f"""🧐 **Explanation:**
This appears to be a {error_type} error with the message: "{error_message}".

🔧 **Suggested Fixes:**
1. Check the error message carefully for clues about what went wrong
2. Look at the line number mentioned in the traceback
3. Verify that all variables and functions are properly defined
4. Check for syntax errors in the code around the error location
5. Ensure all required modules are imported

💡 **Prevention Tips:**
1. Use an IDE with error detection and linting
2. Write unit tests to catch errors early
3. Follow Python coding conventions (PEP 8)
4. Use type hints to catch type-related errors
5. Read the full traceback to understand the error context

Note: This is a generic explanation. For more specific help, consider:
- Checking the Python documentation for {error_type}
- Searching for similar errors online
- Using an AI-powered error explainer for detailed analysis"""


# Global rule-based explainer instance
rule_explainer = RuleBasedExplainer() 