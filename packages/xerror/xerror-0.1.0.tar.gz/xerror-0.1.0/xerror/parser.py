"""
Error parsing and detection for Error Explainer.
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .language_parsers import detect_language, parse_error, get_supported_languages, Language


class ErrorParser:
    """Parser for multi-language error logs and tracebacks."""
    
    def __init__(self):
        # Common Python error patterns (for backward compatibility)
        self.error_patterns = {
            'traceback': r'Traceback \(most recent call last\):',
            'exception': r'(\w+Error): (.+)',
            'file_line': r'File "([^"]+)", line (\d+), in (.+)',
            'syntax_error': r'SyntaxError: (.+)',
            'indentation_error': r'IndentationError: (.+)',
            'import_error': r'ImportError: (.+)',
            'name_error': r'NameError: (.+)',
            'type_error': r'TypeError: (.+)',
            'value_error': r'ValueError: (.+)',
            'key_error': r'KeyError: (.+)',
            'attribute_error': r'AttributeError: (.+)',
            'index_error': r'IndexError: (.+)',
            'zero_division_error': r'ZeroDivisionError: (.+)',
        }
    
    def parse_error_log(self, content: str) -> Dict:
        """
        Parse error log content and extract structured information.
        
        Args:
            content: Raw error log content
            
        Returns:
            Dictionary containing parsed error information
        """
        # Use the new multi-language parser
        error_info = parse_error(content)
        
        # Convert to the expected format for backward compatibility
        result = {
            'error_type': error_info.error_type,
            'error_message': error_info.error_message,
            'traceback': [str(frame) for frame in error_info.stack_trace],
            'files': [frame.get('file', '') for frame in error_info.stack_trace if frame.get('file')],
            'line_numbers': [frame.get('line', 0) for frame in error_info.stack_trace if frame.get('line')],
            'functions': [frame.get('function', '') for frame in error_info.stack_trace if frame.get('function')],
            'full_content': content,
            'is_valid_error': error_info.is_valid_error,
            'language': error_info.language.value,
            'error_summary': error_info.error_summary,
            'file_path': error_info.file_path,
            'function_name': error_info.function_name
        }
        
        # If no structured error found, try legacy Python parsing
        if not result['is_valid_error']:
            result = self._legacy_python_parse(content)
        
        return result
    
    def _legacy_python_parse(self, content: str) -> Dict:
        """Legacy Python-specific parsing for backward compatibility."""
        lines = content.strip().split('\n')
        
        result = {
            'error_type': None,
            'error_message': None,
            'traceback': [],
            'files': [],
            'line_numbers': [],
            'functions': [],
            'full_content': content,
            'is_valid_error': False,
            'language': 'python',
            'error_summary': '',
            'file_path': None,
            'function_name': None
        }
        
        in_traceback = False
        traceback_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is the start of a traceback
            if re.match(self.error_patterns['traceback'], line):
                in_traceback = True
                traceback_lines.append(line)
                continue
            
            # If we're in a traceback, collect lines
            if in_traceback:
                traceback_lines.append(line)
                
                # Check for file/line information
                file_match = re.match(self.error_patterns['file_line'], line)
                if file_match:
                    file_path, line_num, function = file_match.groups()
                    result['files'].append(file_path)
                    result['line_numbers'].append(int(line_num))
                    result['functions'].append(function)
                
                # Check for exception line
                exception_match = re.match(self.error_patterns['exception'], line)
                if exception_match:
                    error_type, error_message = exception_match.groups()
                    result['error_type'] = error_type
                    result['error_message'] = error_message
                    result['is_valid_error'] = True
                    in_traceback = False
                    break
        
        result['traceback'] = traceback_lines
        
        # If no structured traceback found, try to extract error from single lines
        if not result['is_valid_error']:
            for line in lines:
                for error_name, pattern in self.error_patterns.items():
                    if error_name in ['traceback', 'file_line']:
                        continue
                    
                    match = re.match(pattern, line)
                    if match:
                        result['error_type'] = error_name.replace('_error', 'Error').title()
                        result['error_message'] = match.group(1)
                        result['is_valid_error'] = True
                        break
                if result['is_valid_error']:
                    break
        
        return result
    
    def is_python_error(self, content: str) -> bool:
        """
        Check if content contains a Python error.
        
        Args:
            content: Content to check
            
        Returns:
            True if Python error is detected
        """
        # Use the new language detection
        language = detect_language(content)
        return language == Language.PYTHON
    
    def is_error(self, content: str) -> bool:
        """
        Check if content contains any supported language error.
        
        Args:
            content: Content to check
            
        Returns:
            True if any supported error is detected
        """
        language = detect_language(content)
        return language != Language.UNKNOWN
    
    def get_error_language(self, content: str) -> str:
        """
        Get the programming language of the error.
        
        Args:
            content: Content to check
            
        Returns:
            Language name as string
        """
        language = detect_language(content)
        return language.value
    
    def extract_error_summary(self, content: str) -> str:
        """
        Extract a concise summary of the error.
        
        Args:
            content: Error log content
            
        Returns:
            Concise error summary
        """
        parsed = self.parse_error_log(content)
        
        if not parsed['is_valid_error']:
            return "Unknown error format"
        
        summary = f"{parsed['error_type']}: {parsed['error_message']}"
        
        if parsed['files']:
            file_name = Path(parsed['files'][-1]).name
            line_num = parsed['line_numbers'][-1] if parsed['line_numbers'] else "?"
            summary += f" (in {file_name}:{line_num})"
        
        return summary


# Global parser instance
parser = ErrorParser() 