"""
Model abstraction layer for multiple AI providers.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
import json

from rich.console import Console

from .config import config


class BaseModel(ABC):
    """Abstract base class for AI models."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = ""):
        self.api_key = api_key
        self.model_name = model_name
        self.console = Console()
    
    @abstractmethod
    def generate_explanation(self, error_content: str, prompt: str) -> Dict[str, Any]:
        """Generate error explanation using the model."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and configured."""
        pass
    
    def get_model_info(self) -> Dict[str, str]:
        """Get model information."""
        return {
            "provider": self.__class__.__name__,
            "model": self.model_name,
            "available": self.is_available()
        }


class GeminiModel(BaseModel):
    """Google Gemini model implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        super().__init__(api_key, model_name)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            import google.generativeai as genai
            
            api_key = self.api_key or config.api_key
            if not api_key:
                raise ValueError("Google API key not configured")
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model_name)
            
        except ImportError:
            # Silent fail - don't print error during initialization
            pass
        except Exception as e:
            # Silent fail - don't print error during initialization
            pass
    
    def generate_explanation(self, error_content: str, prompt: str) -> Dict[str, Any]:
        """Generate explanation using Gemini."""
        try:
            if not self.client:
                return {"success": False, "error": "Gemini client not initialized"}
            
            response = self.client.generate_content(prompt)
            
            if response.text:
                return {
                    "success": True,
                    "explanation": response.text,
                    "model": self.model_name,
                    "provider": "gemini"
                }
            else:
                return {"success": False, "error": "Empty response from Gemini"}
                
        except Exception as e:
            return {"success": False, "error": f"Gemini API error: {str(e)}"}
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.client is not None and bool(self.api_key or config.api_key)


class OpenAIModel(BaseModel):
    """OpenAI model implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model_name)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        try:
            import openai
            
            api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            self.client = openai.OpenAI(api_key=api_key)
            
        except ImportError:
            # Silent fail - don't print error during initialization
            pass
        except Exception as e:
            # Silent fail - don't print error during initialization
            pass
    
    def generate_explanation(self, error_content: str, prompt: str) -> Dict[str, Any]:
        """Generate explanation using OpenAI."""
        try:
            if not self.client:
                return {"success": False, "error": "OpenAI client not initialized"}
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert Python developer who explains errors clearly and provides helpful fixes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            if response.choices and response.choices[0].message.content:
                return {
                    "success": True,
                    "explanation": response.choices[0].message.content,
                    "model": self.model_name,
                    "provider": "openai"
                }
            else:
                return {"success": False, "error": "Empty response from OpenAI"}
                
        except Exception as e:
            return {"success": False, "error": f"OpenAI API error: {str(e)}"}
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None and bool(self.api_key or os.getenv("OPENAI_API_KEY"))


class OllamaModel(BaseModel):
    """Ollama local model implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "llama2"):
        super().__init__(api_key, model_name)
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Ollama client."""
        try:
            import requests
            
            # Test connection to Ollama
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.client = requests.Session()
                self.client.base_url = self.base_url
            else:
                raise ConnectionError(f"Ollama server not responding: {response.status_code}")
                
        except ImportError:
            # Silent fail - don't print error during initialization
            pass
        except Exception as e:
            # Silent fail - don't print error during initialization
            pass
    
    def generate_explanation(self, error_content: str, prompt: str) -> Dict[str, Any]:
        """Generate explanation using Ollama."""
        try:
            if not self.client:
                return {"success": False, "error": "Ollama client not initialized"}
            
            response = self.client.post("/api/generate", json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1000
                }
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get("response"):
                    return {
                        "success": True,
                        "explanation": result["response"],
                        "model": self.model_name,
                        "provider": "ollama"
                    }
                else:
                    return {"success": False, "error": "Empty response from Ollama"}
            else:
                return {"success": False, "error": f"Ollama API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Ollama API error: {str(e)}"}
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if not self.client:
            return False
        
        try:
            response = self.client.get("/api/tags")
            return response.status_code == 200
        except:
            return False


class ModelManager:
    """Manager for multiple AI models."""
    
    def __init__(self):
        self.models: Dict[str, BaseModel] = {}
        self.console = Console()
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available models silently."""
        # Initialize Gemini (default) - only Flash version to avoid rate limits
        try:
            gemini = GeminiModel()
            if gemini.is_available():
                self.models["gemini"] = gemini
                self.models["gemini-1.5-flash"] = gemini
        except Exception:
            pass
        
        # Initialize OpenAI
        try:
            openai_model = OpenAIModel()
            if openai_model.is_available():
                self.models["openai"] = openai_model
                self.models["gpt-3.5-turbo"] = openai_model
                self.models["gpt-4"] = OpenAIModel(model_name="gpt-4")
        except Exception:
            pass
        
        # Initialize Ollama
        try:
            ollama = OllamaModel()
            if ollama.is_available():
                self.models["ollama"] = ollama
                self.models["llama2"] = ollama
                # Add other common Ollama models
                for model in ["codellama", "mistral", "neural-chat"]:
                    try:
                        test_model = OllamaModel(model_name=model)
                        if test_model.is_available():
                            self.models[model] = test_model
                    except:
                        pass
        except Exception:
            pass
    
    def get_model(self, model_name: str) -> Optional[BaseModel]:
        """Get a model by name."""
        return self.models.get(model_name)
    
    def list_models(self) -> List[Dict[str, str]]:
        """List all available models."""
        return [model.get_model_info() for model in self.models.values()]
    
    def get_default_model(self) -> Optional[BaseModel]:
        """Get the default model (Gemini if available, otherwise first available)."""
        # Try Gemini first
        if "gemini" in self.models:
            return self.models["gemini"]
        
        # Return first available model
        for model in self.models.values():
            if model.is_available():
                return model
        
        return None
    
    def generate_explanation(self, error_content: str, prompt: str, model_name: str = "gemini") -> Dict[str, Any]:
        """Generate explanation using specified model."""
        model = self.get_model(model_name)
        
        if not model:
            return {
                "success": False,
                "error": f"Model '{model_name}' not available. Available models: {list(self.models.keys())}"
            }
        
        if not model.is_available():
            return {
                "success": False,
                "error": f"Model '{model_name}' is not properly configured"
            }
        
        return model.generate_explanation(error_content, prompt)
    
    def benchmark_models(self, error_content: str, prompt: str) -> Dict[str, Any]:
        """Benchmark all available models."""
        results = {}
        
        for name, model in self.models.items():
            if model.is_available():
                try:
                    import time
                    start_time = time.time()
                    
                    result = model.generate_explanation(error_content, prompt)
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    results[name] = {
                        "success": result.get("success", False),
                        "response_time": response_time,
                        "model_info": model.get_model_info(),
                        "error": result.get("error") if not result.get("success") else None
                    }
                    
                except Exception as e:
                    results[name] = {
                        "success": False,
                        "error": str(e),
                        "model_info": model.get_model_info()
                    }
        
        return results


# Global model manager instance
model_manager = ModelManager()


def get_model(model_name: str = "gemini") -> Optional[BaseModel]:
    """Get a model by name."""
    return model_manager.get_model(model_name)


def list_available_models() -> List[Dict[str, str]]:
    """List all available models."""
    return model_manager.list_models()


def generate_explanation_with_model(error_content: str, prompt: str, model_name: str = "gemini") -> Dict[str, Any]:
    """Generate explanation using specified model."""
    return model_manager.generate_explanation(error_content, prompt, model_name)


def benchmark_all_models(error_content: str, prompt: str) -> Dict[str, Any]:
    """Benchmark all available models."""
    return model_manager.benchmark_models(error_content, prompt) 