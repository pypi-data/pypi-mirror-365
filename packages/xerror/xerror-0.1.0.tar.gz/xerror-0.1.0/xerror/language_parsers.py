"""
Language-specific error parsers for multiple programming languages.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .models import model_manager


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CPP = "cpp"
    JAVA = "java"
    RUST = "rust"
    GO = "go"
    PHP = "php"
    RUBY = "ruby"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Structured error information."""
    language: Language
    error_type: str
    error_message: str
    file_path: Optional[str]
    line_number: Optional[int]
    function_name: Optional[str]
    stack_trace: List[Dict]
    is_valid_error: bool
    error_summary: str


class BaseLanguageParser(ABC):
    """Abstract base class for language-specific parsers."""
    
    def __init__(self):
        self.language = Language.UNKNOWN
    
    @abstractmethod
    def detect_language(self, content: str) -> bool:
        """Detect if the content is in this language."""
        pass
    
    @abstractmethod
    def parse_error(self, content: str) -> ErrorInfo:
        """Parse error content and extract structured information."""
        pass
    
    @abstractmethod
    def get_error_patterns(self) -> List[str]:
        """Get regex patterns for error detection."""
        pass


class PythonParser(BaseLanguageParser):
    """Python error parser."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.PYTHON
    
    def detect_language(self, content: str) -> bool:
        """Detect Python errors."""
        # Python-specific patterns that are NOT shared with JavaScript
        python_specific = [
            r"Traceback \(most recent call last\):",
            r"File \"[^\"]+\", line \d+",
            r"IndentationError:",
            r"ImportError:",
            r"ModuleNotFoundError:",
            r"ZeroDivisionError:",
            r"IndexError:",
            r"KeyError:",
            r"ValueError:",
            r"RuntimeError:",
            r"Exception:",
            r"unsupported operand type",  # Python-specific TypeError context
        ]
        
        # Check for Python-specific patterns first
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in python_specific):
            return True
        
        # For shared error types (NameError, TypeError, SyntaxError, AttributeError),
        # check for Python-specific context
        shared_errors = [
            r"NameError:",
            r"TypeError:",
            r"SyntaxError:",
            r"AttributeError:",
        ]
        
        for pattern in shared_errors:
            if re.search(pattern, content, re.IGNORECASE):
                # Check for Python-specific context
                python_context = [
                    r"name '[^']+' is not defined",  # Python NameError pattern
                    r"object has no attribute",      # Python AttributeError pattern
                    r"invalid syntax",               # Python SyntaxError pattern
                    r"unexpected indent",            # Python indentation issues
                    r"File \"[^\"]+\", line \d+",    # Python file references
                ]
                
                if any(re.search(ctx, content, re.IGNORECASE) for ctx in python_context):
                    return True
        
        return False
    
    def parse_error(self, content: str) -> ErrorInfo:
        """Parse Python error content."""
        # Extract error type and message
        error_type = "Unknown"
        error_message = ""
        
        # Look for error type and message
        error_match = re.search(r'(\w+Error):\s*(.+)', content)
        if error_match:
            error_type = error_match.group(1)
            error_message = error_match.group(2).strip()
        
        # Extract file path and line number
        file_path = None
        line_number = None
        function_name = None
        
        file_match = re.search(r'File "([^"]+)", line (\d+)', content)
        if file_match:
            file_path = file_match.group(1)
            line_number = int(file_match.group(2))
        
        # Extract function name
        func_match = re.search(r'in (\w+)', content)
        if func_match:
            function_name = func_match.group(1)
        
        # Parse stack trace
        stack_trace = self._parse_stack_trace(content)
        
        # Create error summary
        error_summary = f"{error_type}: {error_message}"
        if file_path and line_number:
            error_summary += f" (in {file_path}:{line_number})"
        
        return ErrorInfo(
            language=self.language,
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            stack_trace=stack_trace,
            is_valid_error=bool(error_type != "Unknown"),
            error_summary=error_summary
        )
    
    def _parse_stack_trace(self, content: str) -> List[Dict]:
        """Parse Python stack trace."""
        stack_trace = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('File "') and '", line' in line:
                # Extract file and line info
                file_match = re.search(r'File "([^"]+)", line (\d+)', line)
                if file_match:
                    stack_trace.append({
                        'file': file_match.group(1),
                        'line': int(file_match.group(2)),
                        'function': None
                    })
        
        return stack_trace
    
    def get_error_patterns(self) -> List[str]:
        """Get Python error patterns."""
        return [
            r"Traceback \(most recent call last\):",
            r"(\w+Error):\s*(.+)",
            r"File \"[^\"]+\", line \d+",
            r"SyntaxError:",
            r"IndentationError:",
        ]


class JavaScriptParser(BaseLanguageParser):
    """JavaScript error parser."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.JAVASCRIPT
    
    def detect_language(self, content: str) -> bool:
        """Detect JavaScript errors."""
        # JavaScript-specific patterns that are NOT shared with Python
        js_specific = [
            r"at \w+ \(.+:\d+:\d+\)",  # JavaScript stack trace format
            r"Cannot read property",
            r"Cannot set property",
            r"is not a function",
            r"is not defined",
            r"Unexpected token",
            r"Unexpected end of input",
        ]
        
        # Check for JavaScript-specific patterns first
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in js_specific):
            return True
        
        # For shared error types, check for JavaScript-specific context
        shared_errors = [
            r"TypeError:",
            r"ReferenceError:",
            r"SyntaxError:",
        ]
        
        for pattern in shared_errors:
            if re.search(pattern, content, re.IGNORECASE):
                # Check for JavaScript-specific context
                js_context = [
                    r"Cannot read property '[^']+' of",  # JavaScript TypeError pattern
                    r"Cannot set property '[^']+' of",    # JavaScript TypeError pattern
                    r"is not a function",                 # JavaScript TypeError pattern
                    r"is not defined",                    # JavaScript ReferenceError pattern
                    r"Unexpected token",                  # JavaScript SyntaxError pattern
                    r"at \w+ \(.+:\d+:\d+\)",            # JavaScript stack trace
                ]
                
                if any(re.search(ctx, content, re.IGNORECASE) for ctx in js_context):
                    return True
        
        return False
    
    def parse_error(self, content: str) -> ErrorInfo:
        """Parse JavaScript error content."""
        # Extract error type and message
        error_type = "Unknown"
        error_message = ""
        
        # Look for error type and message
        error_match = re.search(r'(\w+Error):\s*(.+)', content)
        if error_match:
            error_type = error_match.group(1)
            error_message = error_match.group(2).strip()
        
        # Extract file path and line number
        file_path = None
        line_number = None
        function_name = None
        
        # Look for stack trace entries
        stack_match = re.search(r'at \w+ \((.+):(\d+):(\d+)\)', content)
        if stack_match:
            file_path = stack_match.group(1)
            line_number = int(stack_match.group(2))
        
        # Extract function name
        func_match = re.search(r'at (\w+) \(', content)
        if func_match:
            function_name = func_match.group(1)
        
        # Parse stack trace
        stack_trace = self._parse_stack_trace(content)
        
        # Create error summary
        error_summary = f"{error_type}: {error_message}"
        if file_path and line_number:
            error_summary += f" (in {file_path}:{line_number})"
        
        return ErrorInfo(
            language=self.language,
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            stack_trace=stack_trace,
            is_valid_error=bool(error_type != "Unknown"),
            error_summary=error_summary
        )
    
    def _parse_stack_trace(self, content: str) -> List[Dict]:
        """Parse JavaScript stack trace."""
        stack_trace = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('at '):
                # Extract function, file, and line info
                match = re.search(r'at (\w+) \((.+):(\d+):(\d+)\)', line)
                if match:
                    stack_trace.append({
                        'function': match.group(1),
                        'file': match.group(2),
                        'line': int(match.group(3)),
                        'column': int(match.group(4))
                    })
        
        return stack_trace
    
    def get_error_patterns(self) -> List[str]:
        """Get JavaScript error patterns."""
        return [
            r"(\w+Error):\s*(.+)",
            r"at \w+ \(.+:\d+:\d+\)",
            r"at \w+ \(.+:\d+\)",
            r"TypeError:",
            r"ReferenceError:",
            r"SyntaxError:",
        ]


class TypeScriptParser(JavaScriptParser):
    """TypeScript error parser (extends JavaScript parser)."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.TYPESCRIPT
    
    def detect_language(self, content: str) -> bool:
        """Detect TypeScript errors."""
        # TypeScript has additional error types
        ts_indicators = [
            r"TS\d+:",  # TypeScript error codes
            r"Type.*is not assignable to type",
            r"Property.*does not exist on type",
            r"Parameter.*implicitly has.*type",
            r"Type.*has no properties in common with type",
        ]
        
        # Check for TypeScript-specific patterns first
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in ts_indicators):
            return True
        
        # For TypeScript, we need to be more strict - only detect if we have clear TS patterns
        # Don't fall back to JavaScript detection to avoid false positives
        return False
    
    def parse_error(self, content: str) -> ErrorInfo:
        """Parse TypeScript error content."""
        # Check for TypeScript-specific errors
        ts_error_match = re.search(r'(TS\d+):\s*(.+)', content)
        if ts_error_match:
            error_type = "TypeScriptError"
            error_message = f"{ts_error_match.group(1)}: {ts_error_match.group(2)}"
            
            # Extract file path and line number
            file_path = None
            line_number = None
            
            # Look for file:line:column pattern
            file_match = re.search(r'(.+):(\d+):(\d+)', content)
            if file_match:
                file_path = file_match.group(1)
                line_number = int(file_match.group(2))
            
            error_summary = f"{error_type}: {error_message}"
            if file_path and line_number:
                error_summary += f" (in {file_path}:{line_number})"
            
            return ErrorInfo(
                language=self.language,
                error_type=error_type,
                error_message=error_message,
                file_path=file_path,
                line_number=line_number,
                function_name=None,
                stack_trace=[],
                is_valid_error=True,
                error_summary=error_summary
            )
        
        # Fall back to JavaScript parsing
        return super().parse_error(content)


class CppParser(BaseLanguageParser):
    """C++ error parser."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.CPP
    
    def detect_language(self, content: str) -> bool:
        """Detect C++ errors."""
        # Check for C++-specific patterns only
        cpp_specific = [
            r"error: '.*' was not declared in this scope",
            r"error: expected ';' before",  # Add missing semicolon pattern
            r"undefined reference to",
            r"multiple definition of",
            r"no matching function for call",
            r"cannot convert.*to",
            r"in file included from",
            r"compilation terminated",
            r"note: suggested alternative:",
        ]
        
        # Only detect C++ if we find specific C++ patterns
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in cpp_specific)
    
    def parse_error(self, content: str) -> ErrorInfo:
        """Parse C++ error content."""
        # Extract error type and message
        error_type = "CompilationError"
        error_message = ""
        
        # Look for error messages
        error_match = re.search(r'error:\s*(.+)', content, re.IGNORECASE)
        if error_match:
            error_message = error_match.group(1).strip()
        
        # Extract file path and line number
        file_path = None
        line_number = None
        
        # Look for file:line pattern
        file_match = re.search(r'([^:]+):(\d+):', content)
        if file_match:
            file_path = file_match.group(1)
            line_number = int(file_match.group(2))
        
        # Parse compilation errors
        stack_trace = self._parse_compilation_errors(content)
        
        # Create error summary
        error_summary = f"{error_type}: {error_message}"
        if file_path and line_number:
            error_summary += f" (in {file_path}:{line_number})"
        
        return ErrorInfo(
            language=self.language,
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            function_name=None,
            stack_trace=stack_trace,
            is_valid_error=bool(error_message),
            error_summary=error_summary
        )
    
    def _parse_compilation_errors(self, content: str) -> List[Dict]:
        """Parse C++ compilation errors."""
        stack_trace = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for file:line:column patterns
            match = re.search(r'([^:]+):(\d+):(\d+):', line)
            if match:
                stack_trace.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'column': int(match.group(3))
                })
        
        return stack_trace
    
    def get_error_patterns(self) -> List[str]:
        """Get C++ error patterns."""
        return [
            r"error:\s*(.+)",
            r"warning:\s*(.+)",
            r"([^:]+):(\d+):(\d+):",
            r"undefined reference to",
            r"multiple definition of",
        ]


class JavaParser(BaseLanguageParser):
    """Java error parser."""
    
    def __init__(self):
        super().__init__()
        self.language = Language.JAVA
    
    def detect_language(self, content: str) -> bool:
        """Detect Java errors."""
        java_indicators = [
            r"Exception in thread",
            r"java\.\w+\.\w+Exception:",
            r"at \w+\.\w+\.\w+\(.+\.java:\d+\)",
            r"error: cannot find symbol",
            r"error: incompatible types",
            r"error: ';' expected",
        ]
        
        # Check for Java-specific patterns
        java_specific = [
            r"Exception in thread",
            r"java\.\w+\.\w+Exception:",
            r"at \w+\.\w+\.\w+\(.+\.java:\d+\)",
            r"error: cannot find symbol",
            r"error: incompatible types",
            r"error: ';' expected",
        ]
        
        # If we find Java-specific patterns, it's definitely Java
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in java_specific):
            return True
        
        # Otherwise, check for general Java patterns
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in java_indicators)
    
    def parse_error(self, content: str) -> ErrorInfo:
        """Parse Java error content."""
        # Extract error type and message
        error_type = "Exception"
        error_message = ""
        
        # Look for exception type and message
        exception_match = re.search(r'(java\.\w+\.\w+Exception):\s*(.+)', content)
        if exception_match:
            error_type = exception_match.group(1)
            error_message = exception_match.group(2).strip()
        
        # Extract file path and line number
        file_path = None
        line_number = None
        function_name = None
        
        # Look for stack trace entries
        stack_match = re.search(r'at \w+\.\w+\.\w+\((.+\.java):(\d+)\)', content)
        if stack_match:
            file_path = stack_match.group(1)
            line_number = int(stack_match.group(2))
        
        # Extract function name
        func_match = re.search(r'at (\w+\.\w+\.\w+)\(', content)
        if func_match:
            function_name = func_match.group(1)
        
        # Parse stack trace
        stack_trace = self._parse_stack_trace(content)
        
        # Create error summary
        error_summary = f"{error_type}: {error_message}"
        if file_path and line_number:
            error_summary += f" (in {file_path}:{line_number})"
        
        return ErrorInfo(
            language=self.language,
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            stack_trace=stack_trace,
            is_valid_error=bool(error_type != "Exception" or error_message),
            error_summary=error_summary
        )
    
    def _parse_stack_trace(self, content: str) -> List[Dict]:
        """Parse Java stack trace."""
        stack_trace = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('at '):
                # Extract class, method, file, and line info
                match = re.search(r'at (\w+\.\w+\.\w+)\((.+\.java):(\d+)\)', line)
                if match:
                    stack_trace.append({
                        'class': match.group(1),
                        'file': match.group(2),
                        'line': int(match.group(3))
                    })
        
        return stack_trace
    
    def get_error_patterns(self) -> List[str]:
        """Get Java error patterns."""
        return [
            r"Exception in thread",
            r"(java\.\w+\.\w+Exception):\s*(.+)",
            r"at \w+\.\w+\.\w+\(.+\.java:\d+\)",
            r"error: cannot find symbol",
            r"error: incompatible types",
        ]


class LanguageDetector:
    """Detect programming language from error content."""
    
    def __init__(self):
        self.parsers = {
            Language.PYTHON: PythonParser(),
            Language.JAVASCRIPT: JavaScriptParser(),
            Language.TYPESCRIPT: TypeScriptParser(),
            Language.CPP: CppParser(),
            Language.JAVA: JavaParser(),
        }
    
    def _ai_fallback_language(self, content: str) -> Language:
        """Use AI to detect language if rule-based fails."""
        prompt = (
            "What programming language is this error from? Just return the language name.\n"
            f"Error:\n{content}"
        )
        ai_result = model_manager.generate_explanation(content, prompt)
        print(f"[DEBUG] AI result: {ai_result}")
        if ai_result.get("success"):
            ai_text = ai_result.get("explanation", "").strip().lower()
            mapped = self._map_ai_language(ai_text)
            print(f"[DEBUG] AI text: {ai_text}, mapped: {mapped}")
            return mapped
        return Language.UNKNOWN

    def _map_ai_language(self, ai_text: str) -> Language:
        mapping = {
            "python": Language.PYTHON,
            "py": Language.PYTHON,
            "javascript": Language.JAVASCRIPT,
            "js": Language.JAVASCRIPT,
            "typescript": Language.TYPESCRIPT,
            "ts": Language.TYPESCRIPT,
            "c++": Language.CPP,
            "cpp": Language.CPP,
            "c plus plus": Language.CPP,
            "java": Language.JAVA,
            "go": Language.GO,
            "golang": Language.GO,
            "php": Language.PHP,
            "ruby": Language.RUBY,
            "rust": Language.RUST,
        }
        for key, lang in mapping.items():
            if key in ai_text:
                return lang
        return Language.UNKNOWN

    def detect_language(self, content: str) -> Language:
        """Detect the programming language from error content."""
        # Check languages in order of specificity (most specific first)
        detection_order = [
            Language.TYPESCRIPT,  # Most specific (extends JavaScript)
            Language.CPP,         # Very specific patterns
            Language.JAVA,        # Very specific patterns
            Language.PYTHON,      # Check Python before JavaScript for better accuracy
            Language.JAVASCRIPT,  # General patterns (check last)
        ]
        
        for language in detection_order:
            parser = self.parsers.get(language)
            if parser and parser.detect_language(content):
                return language
        
        return self._ai_fallback_language(content)
    
    def get_parser(self, language: Language) -> Optional[BaseLanguageParser]:
        """Get parser for specific language."""
        return self.parsers.get(language)
    
    def parse_error(self, content: str) -> ErrorInfo:
        """Parse error content and detect language automatically."""
        language = self.detect_language(content)
        parser = self.get_parser(language)
        
        if parser:
            return parser.parse_error(content)
        else:
            # Return unknown error info
            return ErrorInfo(
                language=Language.UNKNOWN,
                error_type="Unknown",
                error_message="",
                file_path=None,
                line_number=None,
                function_name=None,
                stack_trace=[],
                is_valid_error=False,
                error_summary="Unknown error format"
            )
    
    def get_supported_languages(self) -> List[Language]:
        """Get list of supported languages."""
        return list(self.parsers.keys())


# Global language detector instance
language_detector = LanguageDetector()


def detect_language(content: str) -> Language:
    """Detect programming language from error content."""
    return language_detector.detect_language(content)


def parse_error(content: str) -> ErrorInfo:
    """Parse error content and return structured information."""
    return language_detector.parse_error(content)


def get_supported_languages() -> List[Language]:
    """Get list of supported programming languages."""
    return language_detector.get_supported_languages() 