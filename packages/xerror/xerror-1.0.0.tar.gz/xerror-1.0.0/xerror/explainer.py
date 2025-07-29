"""
AI-powered error explanation using multiple AI models.
"""

import json
import time
from typing import Dict, Optional, List
from rich.console import Console

from .config import config
from .parser import parser
from .models import model_manager, generate_explanation_with_model


class ErrorExplainer:
    """AI-powered error explanation using multiple AI models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize the error explainer.
        
        Args:
            api_key: API key for the model (optional, can use environment variables)
            model: Model to use for explanations (gemini, openai, ollama, etc.)
        """
        self.api_key = api_key
        self.model_name = model
        self.console = Console()
        
        # Check if model is available
        if not model_manager.get_model(model):
            available_models = list(model_manager.models.keys())
            raise ValueError(f"Model '{model}' not available. Available models: {available_models}")
    
    def build_prompt(self, error_content: str, parsed_error: Dict) -> str:
        """
        Build a structured prompt for error explanation.
        
        Args:
            error_content: Raw error content
            parsed_error: Parsed error information
            
        Returns:
            Formatted prompt for the AI model
        """
        error_type = parsed_error.get('error_type', 'Unknown')
        error_message = parsed_error.get('error_message', '')
        language = parsed_error.get('language', 'python')
        files = parsed_error.get('files', [])
        line_numbers = parsed_error.get('line_numbers', [])
        
        # Language-specific prompt customization
        language_context = self._get_language_context(language)
        
        prompt = f"""You are an expert {language_context} developer and debugging specialist. 

Please analyze this {language_context} error and provide:

1. **Clear Explanation**: What caused this error and why it happened
2. **Fix Suggestions**: Specific code fixes with examples
3. **Prevention Tips**: How to avoid this error in the future

Error Details:
- Language: {language_context}
- Type: {error_type}
- Message: {error_message}
- Files: {', '.join(files) if files else 'Unknown'}
- Line Numbers: {', '.join(map(str, line_numbers)) if line_numbers else 'Unknown'}

Full Error Log:
```
{error_content}
```

Please format your response as follows:

🧐 **Explanation:**
[Clear, concise explanation of what went wrong]

🔧 **Suggested Fixes:**
[Specific code examples and fixes]

💡 **Prevention Tips:**
[How to avoid this error in the future]

Keep your response focused, practical, and beginner-friendly."""
        
        return prompt
    
    def _get_language_context(self, language: str) -> str:
        """Get language-specific context for prompts."""
        language_contexts = {
            'python': 'Python',
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'cpp': 'C++',
            'java': 'Java',
            'rust': 'Rust',
            'go': 'Go',
            'php': 'PHP',
            'ruby': 'Ruby',
        }
        return language_contexts.get(language, 'programming')
    
    def explain_error(self, error_content: str) -> Dict:
        """
        Explain an error using AI.
        
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
                'parsed_error': parsed_error
            }
        
        try:
            # Build the prompt
            prompt = self.build_prompt(error_content, parsed_error)
            
            # Generate explanation using the specified model
            result = generate_explanation_with_model(error_content, prompt, self.model_name)
            
            if result.get('success'):
                return {
                    'success': True,
                    'explanation': result['explanation'],
                    'parsed_error': parsed_error,
                    'model_used': result.get('model', self.model_name),
                    'provider': result.get('provider', 'unknown'),
                    'timestamp': time.time(),
                    'error_summary': parser.extract_error_summary(error_content)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'explanation': None,
                    'parsed_error': parsed_error
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI explanation failed: {str(e)}',
                'explanation': None,
                'parsed_error': parsed_error
            }
    
    def explain_error_simple(self, error_content: str) -> str:
        """
        Get a simple explanation string for an error.
        
        Args:
            error_content: Raw error log content
            
        Returns:
            Simple explanation string
        """
        result = self.explain_error(error_content)
        
        if not result['success']:
            return f"❌ Error: {result['error']}"
        
        return result['explanation']


def explain_error(error_content: str, api_key: Optional[str] = None, model: str = "gemini-1.5-flash") -> Dict:
    """
    Convenience function to explain an error.
    
    Args:
        error_content: Raw error log content
        api_key: Google Gemini API key (optional)
        model: Model to use (optional)
        
    Returns:
        Dictionary containing explanation and metadata
    """
    explainer = ErrorExplainer(api_key=api_key, model=model)
    return explainer.explain_error(error_content) 