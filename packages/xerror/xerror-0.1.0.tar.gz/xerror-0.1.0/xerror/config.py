"""
Configuration management for Error Explainer.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Error Explainer."""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.log_dir = self._get_log_directory()
        self.default_model = self._get_default_model()
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or command line."""
        return os.getenv("GOOGLE_API_KEY")
    
    def _get_log_directory(self) -> Path:
        """Get log directory path."""
        custom_dir = os.getenv("ERROR_EXPLAINER_LOG_DIR")
        if custom_dir:
            return Path(custom_dir)
        
        # Default to ~/.error_explainer_logs/
        home_dir = Path.home()
        return home_dir / ".error_explainer_logs"
    
    def _get_default_model(self) -> str:
        """Get default model name."""
        return os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    
    def ensure_log_directory(self) -> None:
        """Ensure log directory exists."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def is_configured(self) -> bool:
        """Check if the tool is properly configured."""
        return bool(self.api_key)


# Global configuration instance
config = Config() 